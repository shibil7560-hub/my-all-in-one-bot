import discord
import os
import asyncio
from discord.ext import commands
from threading import Thread
from flask import Flask
import yt_dlp

# --- ഇവിടെയാണ് പുതിയ മാറ്റം വരുന്നത് ---
import static_ffmpeg
static_ffmpeg.add_paths() 
# --------------------------------------

