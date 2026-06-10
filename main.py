import discord
import os
from discord.ext import commands
from threading import Thread
from flask import Flask

app = Flask('')
@app.route('/')
def home():
    return "Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Managing Server! 👑"))
    print(f'{bot.user.name} is ready!')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"Welcome {member.mention} to our server! 🎉")

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="All in One Bot", description="Server Management Bot Commands:", color=0x00ff00)
    embed.add_field(name="!ping", value="Check if the bot is online", inline=False)
    embed.add_field(name="!kick @user", value="Kick a user (Admin Only)", inline=False)
    embed.add_field(name="!ban @user", value="Ban a user (Admin Only)", inline=False)
    embed.add_field(name="!clear 10", value="Delete multiple messages", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send("Bot is active and running! ⚡")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {amount} messages!", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned!")

@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message_content):
    # Deletes the command message you typed to keep it clean
    await ctx.message.delete()
    
    # Creates the beautiful embed box
    embed = discord.Embed(
        title="📢 New Announcement!",
        description=message_content,
        color=0xff0000
    )
    embed.set_footer(text=f"Announced by {ctx.author.name}")
    
    # Sends the embed directly to the current channel
    await ctx.send(embed=embed)
    # --- TICKET SYSTEM WITH BUTTONS ---

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Keeps the button active forever

    @discord.ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        
        # Checking if ticket channel already exists for this member
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Setting permissions: Only the creator and Admins can see it
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Creating the private ticket channel
        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        
        # Sending welcome message inside the new ticket channel
        embed = discord.Embed(
            title="🎫 Ticket Created!",
            description=f"Hello {member.mention},\nOur Support Team/Admins will assist you shortly. Please state your issue here.",
            color=0x00ff00
        )
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket created successfully! Go to {ticket_channel.mention}", ephemeral=True)

# Command to send the Ticket Setup Box (Only for Admins)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📩 Support Ticket System",
        description="Click the button below to create a private support ticket and talk to the Admins.",
        color=0x5865F2
    )
    await ctx.send(embed=embed, view=TicketSetupView())

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("TOKEN")
    bot.run(token)
