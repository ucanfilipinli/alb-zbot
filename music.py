import discord
from discord.ext import commands
from discord import app_commands

from discord.ui import View, Button

import yt_dlp
import asyncio

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

            "player_client": [

                "android",

                "web"

            ]

        }

    }

}



FFMPEG_OPTIONS = {

    "before_options":
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 10",

    "options":

        "-vn"

}





class MusicButtons(View):


    def __init__(self, music):

        super().__init__(timeout=None)

        self.music = music




    @discord.ui.button(
        emoji="⏯️",
        style=discord.ButtonStyle.primary
    )
    async def pause_resume(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        voice = interaction.guild.voice_client



        if not voice:

            await interaction.response.send_message(
                "❌ Bot ses kanalında değil.",
                ephemeral=True
            )

            return



        if voice.is_playing():

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





    @discord.ui.button(
        emoji="⏭️",
        style=discord.ButtonStyle.secondary
    )
    async def skip(
        self,
        interaction: discord.Interaction,
        button: Button
    ):


        voice = interaction.guild.voice_client



        if voice and voice.is_playing():

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





    @discord.ui.button(
        emoji="⏹️",
        style=discord.ButtonStyle.danger
    )
    async def stop(
        self,
        interaction: discord.Interaction,
        button: Button
    ):


        voice = interaction.guild.voice_client



        if voice:

            voice.stop()



        self.music.queue[interaction.guild.id] = []



        await interaction.response.send_message(
            "⏹️ Müzik durduruldu.",
            ephemeral=True
        )





    @discord.ui.button(
        emoji="🔁",
        style=discord.ButtonStyle.success
    )
    async def loop(
        self,
        interaction: discord.Interaction,
        button: Button
    ):


        guild_id = interaction.guild.id



        mode = self.music.loop_mode.get(
            guild_id,
            "off"
        )



        if mode == "off":

            self.music.loop_mode[guild_id] = "song"

            text = "🔂 Tek şarkı döngüsü açıldı."


        elif mode == "song":

            self.music.loop_mode[guild_id] = "queue"

            text = "🔁 Kuyruk döngüsü açıldı."


        else:

            self.music.loop_mode[guild_id] = "off"

            text = "➡️ Döngü kapatıldı."



        await interaction.response.send_message(
            text,
            ephemeral=True
        )





class Music(commands.Cog):


    def __init__(self, bot):

        self.bot = bot

        self.queue = {}

        self.current = {}

        self.loop_mode = {}

        self.volume = {}
    async def extract(self, query):

        loop = asyncio.get_event_loop()


        def run():

            search = query


            if "spotify.com" in search:

                search = "ytsearch1:" + search



            elif not search.startswith("http"):

                search = "ytsearch1:" + search



            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:


                print(
                    "ARAMA:",
                    search
                )


                info = ydl.extract_info(

                    search,

                    download=False

                )



                if "entries" in info:


                    entries = info["entries"]


                    if not entries:

                        raise Exception(
                            "Playlist boş"
                        )


                    info = entries[0]




                if not info.get("url"):


                    for fmt in reversed(

                        info.get(

                            "formats",

                            []

                        )

                    ):


                        if (

                            fmt.get("url")

                            and

                            fmt.get("acodec") != "none"

                        ):


                            info["url"] = fmt["url"]

                            break





                if not info.get("url"):

                    raise Exception(
                        "Ses URL bulunamadı"
                    )



                return info




        return await loop.run_in_executor(

            None,

            run

        )





    def create_embed(self, info):


        title = info.get(

            "title",

            "Bilinmeyen"

        )


        uploader = info.get(

            "uploader",

            "Bilinmiyor"

        )


        thumbnail = info.get(

            "thumbnail"

        )


        duration = info.get(

            "duration",

            0

        )


        dakika = duration // 60

        saniye = duration % 60



        embed = EmbedManager.info(

            "🎵 Şimdi Çalıyor",

            f"""

**🎶 Şarkı**

{title}


**👤 Kanal**

{uploader}


**⏱ Süre**

{dakika}:{saniye:02}

"""

        )



        if thumbnail:

            embed.set_thumbnail(

                url=thumbnail

            )



        return embed





    async def play_song(self, guild, info):


        voice = guild.voice_client



        if not voice:

            return



        print(
            "FFMPEG BAŞLIYOR"
        )



        audio = discord.FFmpegPCMAudio(

            info["url"],

            executable=FFMPEG_PATH,

            before_options=FFMPEG_OPTIONS["before_options"],

            options=FFMPEG_OPTIONS["options"]

        )




        def after(error):


            if error:

                print(
                    "PLAYER HATASI:",
                    error
                )



            asyncio.run_coroutine_threadsafe(

                self.next_song(guild),

                self.bot.loop

            )




        voice.play(

            audio,

            after=after

        )



        print(
            "SES BAŞLADI"
        )





    async def next_song(self, guild):


        guild_id = guild.id



        mode = self.loop_mode.get(

            guild_id,

            "off"

        )



        current = self.current.get(

            guild_id

        )



        if mode == "song" and current:


            await self.play_song(

                guild,

                current

            )

            return




        if mode == "queue" and current:


            self.queue[guild_id].append(

                current["webpage_url"]

            )




        if not self.queue.get(guild_id):

            return




        song = self.queue[guild_id].pop(0)



        try:


            info = await self.extract(song)



            self.current[guild_id] = info



            await self.play_song(

                guild,

                info

            )


        except Exception as e:


            print(

                "SONRAKİ ŞARKI HATASI:",

                e

            )





    @app_commands.command(

        name="join",

        description="Ses kanalına girer"

    )
    async def join(

        self,

        interaction: discord.Interaction

    ):


        if not interaction.user.voice:


            await interaction.response.send_message(

                "❌ Önce ses kanalına gir."

            )

            return



        await interaction.user.voice.channel.connect()



        await interaction.response.send_message(

            "🎵 Ses kanalına katıldım."

        )





    @app_commands.command(

        name="play",

        description="Müzik açar"

    )
    async def play(

        self,

        interaction: discord.Interaction,

        arama: str

    ):


        await interaction.response.defer()



        if not interaction.user.voice:


            await interaction.followup.send(

                "❌ Ses kanalına gir."

            )

            return





        if not interaction.guild.voice_client:


            await interaction.user.voice.channel.connect()



        guild = interaction.guild



        if guild.id not in self.queue:


            self.queue[guild.id] = []



        try:


            info = await self.extract(arama)



        except Exception as e:


            await interaction.followup.send(

                f"❌ Hata: {e}"

            )

            return




        voice = guild.voice_client



        if voice.is_playing():


            self.queue[guild.id].append(arama)


            await interaction.followup.send(

                "➕ Kuyruğa eklendi."

            )


            return




        self.current[guild.id] = info



        await self.play_song(

            guild,

            info

        )



        await interaction.followup.send(

            embed=self.create_embed(info),

            view=MusicButtons(self)

        )
    @app_commands.command(
        name="skip",
        description="Şarkıyı geçer"
    )
    async def skip(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice and voice.is_playing():

            voice.stop()

            await interaction.response.send_message(
                "⏭️ Şarkı geçildi."
            )

        else:

            await interaction.response.send_message(
                "❌ Çalan şarkı yok."
            )





    @app_commands.command(
        name="pause",
        description="Müziği durdurur"
    )
    async def pause(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice and voice.is_playing():

            voice.pause()

            await interaction.response.send_message(
                "⏸️ Müzik durduruldu."
            )

        else:

            await interaction.response.send_message(
                "❌ Müzik çalmıyor."
            )





    @app_commands.command(
        name="resume",
        description="Müziği devam ettirir"
    )
    async def resume(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice and voice.is_paused():

            voice.resume()

            await interaction.response.send_message(
                "▶️ Müzik devam ediyor."
            )

        else:

            await interaction.response.send_message(
                "❌ Duraklatılmış müzik yok."
            )





    @app_commands.command(
        name="stop",
        description="Müziği durdurur"
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice:

            voice.stop()



        self.queue[interaction.guild.id] = []



        await interaction.response.send_message(
            "⏹️ Müzik durduruldu."
        )





    @app_commands.command(
        name="queue",
        description="Kuyruğu gösterir"
    )
    async def queue(
        self,
        interaction: discord.Interaction
    ):


        songs = self.queue.get(

            interaction.guild.id,

            []

        )



        if not songs:

            await interaction.response.send_message(
                "🎵 Kuyruk boş."
            )

            return




        text = ""



        for i, song in enumerate(
            songs,
            start=1
        ):

            text += f"**{i}.** {song}\n"




        await interaction.response.send_message(

            embed=EmbedManager.info(

                "🎶 Kuyruk",

                text

            )

        )





    @app_commands.command(
        name="volume",
        description="Ses ayarı"
    )
    async def volume(
        self,
        interaction: discord.Interaction,
        seviye: int
    ):


        voice = interaction.guild.voice_client



        if not voice or not voice.source:


            await interaction.response.send_message(
                "❌ Müzik çalmıyor."
            )

            return





        if seviye < 0 or seviye > 100:


            await interaction.response.send_message(
                "❌ 0-100 arası değer gir."
            )

            return





        voice.source.volume = seviye / 100



        await interaction.response.send_message(
            f"🔊 Ses %{seviye} yapıldı."
        )





    @app_commands.command(
        name="nowplaying",
        description="Çalan şarkıyı gösterir"
    )
    async def nowplaying(
        self,
        interaction: discord.Interaction
    ):


        info = self.current.get(
            interaction.guild.id
        )



        if not info:


            await interaction.response.send_message(
                "❌ Şu anda müzik yok."
            )

            return





        await interaction.response.send_message(

            embed=self.create_embed(info)

        )





    @app_commands.command(
        name="leave",
        description="Ses kanalından çıkar"
    )
    async def leave(
        self,
        interaction: discord.Interaction
    ):


        voice = interaction.guild.voice_client



        if voice:

            await voice.disconnect()



            await interaction.response.send_message(
                "👋 Ses kanalından ayrıldım."
            )


        else:

            await interaction.response.send_message(
                "❌ Ses kanalında değilim."
            )





    @app_commands.command(
        name="loop",
        description="Loop modunu değiştirir"
    )
    async def loop(
        self,
        interaction: discord.Interaction
    ):


        guild_id = interaction.guild.id



        mode = self.loop_mode.get(

            guild_id,

            "off"

        )



        if mode == "off":

            self.loop_mode[guild_id] = "song"

            mesaj = "🔂 Tek şarkı loop açıldı."


        elif mode == "song":

            self.loop_mode[guild_id] = "queue"

            mesaj = "🔁 Kuyruk loop açıldı."


        else:

            self.loop_mode[guild_id] = "off"

            mesaj = "➡️ Loop kapatıldı."



        await interaction.response.send_message(
            mesaj
        )





    @app_commands.command(
        name="playlist",
        description="YouTube playlist ekler"
    )
    async def playlist(
        self,
        interaction: discord.Interaction,
        link: str
    ):


        await interaction.response.defer()



        try:


            loop = asyncio.get_event_loop()



            def get_playlist():


                with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:


                    data = ydl.extract_info(

                        link,

                        download=False

                    )


                    return [

                        x["webpage_url"]

                        for x in data["entries"]

                    ]



            songs = await loop.run_in_executor(

                None,

                get_playlist

            )



            if interaction.guild.id not in self.queue:

                self.queue[interaction.guild.id] = []



            self.queue[interaction.guild.id].extend(
                songs
            )



            await interaction.followup.send(

                f"📃 {len(songs)} şarkı kuyruğa eklendi."

            )


        except Exception as e:


            await interaction.followup.send(

                f"❌ Playlist hatası: {e}"

            )





async def setup(bot):

    await bot.add_cog(

        Music(bot)

    )