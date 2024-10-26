from tkinter import messagebox
import urllib.request
import requests
from urllib.parse import urlparse
from pathlib import Path
from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix.exceptions import *
import os
from typing import Optional
import re

class Download:
    def __init__(self):
        # self.gui_settings = gui_settings gui_settings: dict[str, Union[str, bool]]
        self.needs_conversion = None
        self.format_for_download = None
        self.audio_stream = None
        self.video_stream = None
        self.audio_path = None
        self.video_path = None
        self.output_file_name = None

    def change_download_format(self, yt: YouTube):
        response = messagebox.askquestion(
            title="Info",
            message=f"Für das Video {yt.title} sind keine passenden Streams für das ausgewählte Format verfügbar.\n"
                    f"Soll in das gewünsche Format konvertiert werden?",
        )
        if response == "yes":
            if self.format_for_download == "webm":
                self.format_for_download = ["mp4"]
                self.needs_conversion = True
            elif self.format_for_download == "mp4":
                self.format_for_download = ["webm"]
                self.needs_conversion = True
            return True
        elif response == "no":
            return False

    def check_stream_availability(self, yt: YouTube, resolution, selected_format):
        if selected_format in ["mp4", "webm", "mkv"]:
            video_stream = self.get_video_stream_availability(yt, resolution)
            audio_stream = self.get_audio_stream_availability(yt)
            if video_stream and audio_stream:
                return True
            else:
                return False
        elif selected_format in ["opus", "m4a", "mp3"]:
            return self.get_audio_stream_availability(yt)


    @staticmethod
    def is_playlist(url):
        parsed_url = urlparse(url)
        if parsed_url.path == "/watch":
            return False
        elif parsed_url.path == "/playlist":
            return True
        else:
            return None

    @staticmethod
    def initialize_youtube_instance(
            url,
            gui_settings: dict[str, Union[str, bool]] = None,
            return_error: bool = False,
    ) -> Optional[Union[YouTube, str]]:
        try:
            use_oauth = gui_settings["use_OAuth"] if gui_settings else None
            yt = YouTube(url, use_oauth=use_oauth, allow_oauth_cache=False)
            yt.streams
        except RegexMatchError:
            error_message = "Regex pattern did not return any matches."
        except VideoPrivate:
            error_message = f"The video is private. You do not have access to this video."
        except VideoRegionBlocked:
            error_message = f"The video is blocked in your region."
        except AgeRestrictedError:
            error_message = f"The Video is age restricted, and cannot be accessed without OAuth."
        except MembersOnly:
            error_message = "Video is members-only."
        except LiveStreamError:
            error_message = "Video is a live stream."
        else:
            return yt
        if return_error:
            print(error_message)
            return error_message
        else:
            print(error_message)
            return None

    @staticmethod
    def initialize_playlist_instance(url) -> Optional[Playlist]:
        try:
            pl = Playlist(url)
            if len(pl) == 0:
                #print("Private Playlist können nicht heruntergeladen werden.")
                print("Private playlists cannot be downloaded")
                return None
        except RegexMatchError:
            print("Regex pattern did not return any matches.")
            return None
        else:
            return pl

    def determine_download_format(self, selected_format: str):
        if selected_format == "mp3":
            self.format_for_download = ["webm", "mp4"]
            self.needs_conversion = True
        elif selected_format in ["opus", "webm"]:  # format for VP9, Opus
            self.format_for_download = ["webm"]
            self.needs_conversion = False
        elif selected_format in ["m4a", "mp4"]:  # format for MP4, m4a
            self.format_for_download = ["mp4"]
            self.needs_conversion = False
        elif selected_format in ["mkv"]:
            self.format_for_download = ["webm", "mp4"]
            self.needs_conversion = False

    def generate_output_file_name(self, selected_format: str):
        if selected_format in ["opus", "m4a", "mp3", "mkv"]: # The file extension does not need to be adjusted for MP4 and WebM.
            self.output_file_name = Path(self.audio_stream.default_filename).with_suffix("." + selected_format)
        else:
            if self.needs_conversion:
                self.output_file_name = Path(self.audio_stream.default_filename).with_suffix("." + selected_format)
            else:
                self.output_file_name = self.audio_stream.default_filename

        self.output_file_name = re.sub(r'[<>:"/\\|?*]', '', self.output_file_name)
        self.output_file_name = self.output_file_name.strip()

    def download_thumbnail(self, yt: YouTube):
        api_url = f"https://i.ytimg.com/vi/{yt.video_id}/maxresdefault.jpg"
        response = requests.get(api_url)
        thumbnail_file_name = "cover.jpg"

        if response.status_code == 200:
            with open(thumbnail_file_name, 'wb') as f:
                f.write(response.content)
            print("Thumbnail erfolgreich heruntergeladen")
            cover_file = self.get_file_path(thumbnail_file_name)
            return cover_file
        elif response.status_code == 404:
            print("Maxres Thumbnail nicht verfügbar, alternativer Download wird versucht.")
        else:
            print(f"Fehler beim Herunterladen des maxres Thumbnails (Statuscode {response.status_code})")

        for attempt in range(1, 6):
            thumbnail_url = yt.thumbnail_url
            thumbnail_file_name = "cover.jpg"
            urllib.request.urlretrieve(thumbnail_url, thumbnail_file_name)
            if os.path.isfile(thumbnail_file_name) and os.path.getsize(thumbnail_file_name) > 0:
                cover_file = self.get_file_path(thumbnail_file_name)
                print("Thumbnail erfolgreich heruntergeladen")
                return cover_file
            else:
                print(f"alternativer Download fehlgeschlagen (Versuch {attempt} von 5)")

        print("Beide Download-Versuche sind fehlgeschlagen.")
        return None

    @staticmethod
    def get_file_path(file_name):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, file_name)
        return file_path

    def download_subs(self, list_caption_selected, yt: YouTube):
        srt_files = []
        downloaded_subs = []
        if len(list_caption_selected) != 0:
            captions = yt.caption_tracks
            for entry in list_caption_selected:
                try:
                    yt.streams
                    for caption in captions:
                        if entry[0] == caption.name:
                            file = caption.download(title=caption.name, srt=True)
                            srt_files.append(file)
                            downloaded_subs.append(entry)
                            break
                except Exception as e:
                    print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
            if srt_files:
                print("Untertitel erfolgreich heruntergeladen")
        return srt_files, downloaded_subs

    def download_audio(self):
        self.audio_path = self.audio_stream.download(filename_prefix='audio_')
        print("Audio erfolgreich heruntergeladen")

    def download_video(self):
        self.video_path = self.video_stream.download(filename_prefix='video_')
        print("Video erfolgreich heruntergeladen")

    def get_video_stream_availability(self, yt: YouTube, selected_res: str):
        attempt_counter = 0
        format_changed = False

        while not self.video_stream and attempt_counter < 2:
            for attempt, possible_format in enumerate(self.format_for_download, start=1):
                self.video_stream = (
                    yt.streams
                    .filter(file_extension=possible_format, only_video=True, res=selected_res, adaptive=True)
                )
                # video_stream = None
                if self.video_stream:
                    return True
                else:
                    self.video_stream = (
                        yt.streams
                        .filter(file_extension=possible_format, only_video=True, adaptive=True)
                        .order_by("resolution").desc().first()
                    )
                    # video_stream = None
                    if self.video_stream:
                        return True

                if attempt == len(possible_format) and not format_changed:
                    if self.change_download_format(yt):
                        format_changed = True
                    else:
                        return False

            attempt_counter += 1

        return False

    def get_audio_stream_availability(self, yt: YouTube):
        attempt_counter = 0
        format_changed = False

        while not self.audio_stream and attempt_counter < 2:
            for attempt, possible_format in enumerate(self.format_for_download, start=1):
                self.audio_stream = (
                    yt.streams
                    .filter(only_audio=True, file_extension=possible_format).order_by("abr").desc().first())
                if self.audio_stream:
                    return True

                if attempt == len(possible_format) and not format_changed:
                    if self.change_download_format(yt):
                        format_changed = True
                    else:
                        return False

            attempt_counter += 1

        return False