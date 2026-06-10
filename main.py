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

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("TOKEN")
    bot.run(token)
@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message_content):
            channel = discord.utils.get(ctx.guild.text_channels, name=("【📢】announcement")
    if channel is None:
        await ctx.send("Please check the channel name in the code!")
        return

    # Sends the message beautifully inside a red Embed box
    embed = discord.Embed(
        title="📢 New Announcement!",
        description=message_content,
        color=0xff0000 # Red Color
    )
    embed.set_footer(text=f"Announced by {ctx.author.name}")
    
    await channel.send(embed=embed)
    await ctx.send("Announcement sent successfully!")
