import asyncio

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

from utils.embeds import EmbedManager


FFMPEG_PATH = r"C:\Users\akbas\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    "extract_flat": False,
    "default_search": "ytsearch1",
    "socket_timeout": 20,
    "retries": 5,
    "fragment_retries": 5,
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        }
    }
}

FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 10"
    ),
    "options": "-vn"
}


class MusicButtons(View):
    def __init__(self, music):
        super().__init__(timeout=None)
        self.music = music

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary)
    async def pause_resume(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        voice = interaction.guild.voice_client if interaction.guild else None

        if not voice:
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil.",
                ephemeral=True
            )
        elif voice.is_playing():
            voice.pause()
            await interaction.response.send_message(
                "⏸️ Müzik duraklatıldı.",
                ephemeral=True
            )
        elif voice.is_paused():
            voice.resume()
            await interaction.response.send_message(
                "▶️ Müzik devam ediyor.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Çalan müzik yok.",
                ephemeral=True
            )

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        voice = interaction.guild.voice_client if interaction.guild else None

        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            await interaction.response.send_message(
                "⏭️ Şarkı geçildi.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Çalan şarkı yok.",
                ephemeral=True
            )
