import discord
import os
import asyncio
from discord.ext import commands
from threading import Thread
from flask import Flask
import yt_dlp

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
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Music configuration
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True,
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Managing & Music! 👑🎵"))
    print(f'{bot.user.name} is ready!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) successfully!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"Welcome {member.mention} to our server! 🎉")

# --- 1. SLASH COMMAND: INFO ---
@bot.tree.command(name="info", description="View all available bot commands")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="OLAM BOT", description="Server Management & Music Slash Commands:", color=0x00ff00)
    embed.add_field(name="/info", value="Check all available commands", inline=False)
    embed.add_field(name="/ping", value="Check if the bot is online", inline=False)
    embed.add_field(name="/clear [amount]", value="Delete multiple messages (Admin Only)", inline=False)
    embed.add_field(name="/kick [user] [reason]", value="Kick a user (Admin Only)", inline=False)
    embed.add_field(name="/ban [user] [reason]", value="Ban a user (Admin Only)", inline=False)
    embed.add_field(name="/announce [message]", value="Create a beautiful announcement box (Admin Only)", inline=False)
    embed.add_field(name="/setup_ticket", value="Setup the support ticket system (Admin Only)", inline=False)
    embed.add_field(name="/play [song]", value="Play music from YouTube inside Voice Channel", inline=False)
    embed.add_field(name="/skip", value="Skip current song", inline=False)
    embed.add_field(name="/stop", value="Stop music and disconnect", inline=False)
    await interaction.response.send_message(embed=embed)

# --- 2. SLASH COMMAND: PING ---
@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is active and running! ⚡")

# --- 3. SLASH COMMAND: CLEAR ---
@bot.tree.command(name="clear", description="Delete messages from the channel (Admin Only)")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {len(deleted)} messages!", ephemeral=True)

# --- 4. SLASH COMMAND: KICK ---
@bot.tree.command(name="kick", description="Kick a member from the server (Admin Only)")
@discord.app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been kicked! Reason: {reason}")

# --- 5. SLASH COMMAND: BAN ---
@bot.tree.command(name="ban", description="Ban a member from the server (Admin Only)")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been banned! Reason: {reason}")

# --- 6. SLASH COMMAND: ANNOUNCE ---
@bot.tree.command(name="announce", description="Create a beautiful announcement box (Admin Only)")
@discord.app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, message_content: str):
    embed = discord.Embed(
        title="📢 New Announcement!",
        description=message_content,
        color=0xff0000
    )
    embed.set_footer(text=f"Announced by {interaction.user.name}")
    await interaction.response.send_message("Announcement sent successfully!", ephemeral=True)
    await interaction.channel.send(embed=embed)

# --- 7. SLASH COMMAND: PLAY MUSIC ---
@bot.tree.command(name="play", description="Play a song by its name from YouTube")
async def play(interaction: discord.Interaction, song_name: str):
    await interaction.response.defer()
    
    if not interaction.user.voice:
        await interaction.followup.send("You need to be in a voice channel to play music!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    try:
        info = ytdl.extract_info(song_name, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        
        url = info['url']
        title = info['title']
        
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        voice_client.play(source)
        
        await interaction.followup.send(f"🎵 Now playing: **{title}**")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# --- 8. SLASH COMMAND: STOP MUSIC ---
@bot.tree.command(name="stop", description="Stop music and disconnect from the voice channel")
async def stop(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.response.send_message("Stopped the music and disconnected! 👋")
    else:
        await interaction.response.send_message("I am not connected to any voice channel!", ephemeral=True)

# --- 9. SLASH COMMAND: SKIP MUSIC ---
@bot.tree.command(name="skip", description="Skip the current playing song")
async def skip(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("Skipped the song! ⏭️")
    else:
        await interaction.response.send_message("No music is currently playing!", ephemeral=True)


# --- TICKET BUTTON SYSTEM ---

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing and deleting this ticket right now...", ephemeral=False)
        await interaction.channel.delete()

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 Ticket Created!",
            description=f"Hello {member.mention},\nOur Support Team/Admins will assist you shortly. Please state your issue here.\n\nClick the button below to **Close** this ticket.",
            color=0x00ff00
        )
        
        await ticket_channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"Ticket created successfully! Go to {ticket_channel.mention}", ephemeral=True)

# --- 10. SLASH COMMAND: SETUP TICKET ---
@bot.tree.command(name="setup_ticket", description="Setup the private support ticket box (Admin Only)")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📩 Support Ticket System",
        description="Click the button below to create a private support ticket and talk to the Admins.",
        color=0x5865F2
    )
    await interaction.response.send_message("Deploying ticket system...", ephemeral=True)
    await interaction.channel.send(embed=embed, view=TicketSetupView())


if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("TOKEN")
    bot.run(token)
