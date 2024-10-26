import subprocess
import os
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from mutagen.easyid3 import EasyID3
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
import base64
import mimetypes

class PostProcessing:

    @staticmethod
    def convert_file(input_file, output_file_name):
        try:
            command = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                output_file_name
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Datei {input_file} wurde erfolgreich konvertiert")
            return output_file_name
        except Exception as e:
            print(f"Fehler beim Konvertieren {e}")
        finally:
            PostProcessing.delete_files(input_file)

    @staticmethod
    def extract_audio(input_file, output_file):
        try:
            command = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-vn', '-acodec', 'copy',
                output_file
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Audio wurde erfolgreich von {input_file} extrahiert")
            return output_file
        except FileNotFoundError:
            print(f"Fehler: Die Datei {input_file} wurde nicht gefunden.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen von FFmpeg: {e}")
        except Exception as e:
            print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
        finally:
            PostProcessing.delete_files(input_file)

    @staticmethod
    def ffmpeg_merge_streams(stream1, stream2, output_file):
        try:
            command = [
                'ffmpeg',
                '-y',
                '-i', stream1,
                '-i', stream2,
                '-c', 'copy',
                output_file
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Video und Audio wurden gemergt.")
            return output_file
        except FileNotFoundError:
            print(f"Fehler: Eine oder beide Dateien ({stream1}, {stream2}) wurden nicht gefunden.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen von FFmpeg: {e}")
        except Exception as e:
            print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
        finally:
            PostProcessing.delete_files(stream1, stream2)

    @staticmethod
    def delete_files(*files):
        for file in files:
            try:
                os.remove(file)
            except FileNotFoundError:
                print(f"Die Datei {file} wurde nicht gefunden.")

    @staticmethod
    def embed_thumbnail(input_file, cover_file, selected_format):
        if os.path.exists(cover_file):
            if selected_format == "mp3":
                try:
                    temp_output_file = "temp_" + input_file
                    command = [
                        'ffmpeg',
                        '-i', input_file,
                        '-i', cover_file,
                        '-c', 'copy',
                        '-map', '0:0',
                        '-map', '1:0',
                        '-write_id3v1', '1',
                        '-id3v2_version', '3',
                        '-metadata:s:v', 'title="Album cover"',
                        '-metadata:s:v', 'comment=Cover (front)',
                        temp_output_file
                    ]
                    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.replace(temp_output_file, input_file)
                    print("Thumbnail erlogreich eingebettet")
                except Exception as e:
                    print(f"Fehler bei der Einbettung für MP3: {e}")
            elif selected_format == "opus":
                try:
                    opus = OggOpus(input_file)

                    with open(cover_file, 'rb') as thumbnail:
                        thumbnail_data = thumbnail.read()

                    mime_type, _ = mimetypes.guess_type(cover_file)
                    # thumbnail_mime = 'image/%s' % imghdr.what(cover_file)
                    pic = Picture()
                    pic.mime = mime_type
                    pic.data = thumbnail_data
                    pic.type = 3

                    opus['METADATA_BLOCK_PICTURE'] = base64.b64encode(pic.write()).decode('ascii')
                    opus.save()
                    print("Thumbnail erlogreich eingebettet")
                except Exception as e:
                    print(f"Fehler bei der Einbettung für Opus: {e}")
            elif selected_format in ["m4a", "mp4"]:
                # try:
                #     mp4 = MP4(input_file)
                #     with open(cover_file, "rb") as thumbnail:
                #         thumbnail_data = thumbnail.read()
                #     mp4.tags['covr'] = [MP4Cover(data=thumbnail_data, imageformat=MP4Cover.FORMAT_JPEG)]
                #     mp4.save()
                #     print("Thumbnail erlogreich eingebettet")
                # except Exception as e:
                #     print(f"Mutagen Fehler: {e}")
                #     print("Versuche AtomicParsley...")
                try:
                    temp_output_file = "temp_" + input_file
                    command = [
                        "AtomicParsley",
                        input_file,
                        "--artwork", cover_file,
                        "--output", temp_output_file
                    ]
                    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.replace(temp_output_file, input_file)
                    print("Thumbnail erlogreich eingebettet")
                except Exception as e:
                    print(f"AtomicParsley Fehler: {e}")
            elif selected_format in ["mkv", "webm"]:
                try:
                    command = [
                        "mkvpropedit",
                        "--add-attachment", cover_file,
                        input_file
                    ]
                    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("Thumbnail erlogreich eingebettet")
                except Exception as e:
                    print(f"Fehler bei der Einbettung für MKV/WebM: {e}")
            PostProcessing.delete_files(cover_file)

    @staticmethod
    def embed_metadata(input_file, selected_format, title=None, artist=None, album=None, genre=None, track_number=None):
        try:
            if selected_format == "opus":
                audio = OggOpus(input_file)
                if title:
                    audio["title"] = [title]
                if artist:
                    audio["artist"] = [artist]
                if album:
                    audio["album"] = [album]
                if genre:
                    audio["genre"] = [genre]
                if track_number:
                    audio['tracknumber'] = [str(track_number)]
                audio.save()
            elif selected_format in ["m4a", "mp4"]:
                # file = MP4(input_file)
                # tags = MP4Tags()
                # if title:
                #     tags['\xa9nam'] = title
                # if artist:
                #     tags['\xa9ART'] = artist
                # if album:
                #     tags['\xa9alb'] = album
                # if genre:
                #     tags["\xa9gen"] = genre
                # file.tags = tags
                # file.save()
                audio = MP4(input_file)
                current_cover = audio.get('covr')
                if title:
                    audio['\xa9nam'] = title
                if artist:
                    audio['\xa9ART'] = artist
                if album:
                    audio['\xa9alb'] = album
                if genre:
                    audio["\xa9gen"] = genre
                if current_cover:
                    audio["covr"] = current_cover
                if track_number:
                    audio['trkn'] = [(track_number, 0)]
                audio.save()
            elif selected_format == "mp3":
                audio = EasyID3(input_file)
                if title:
                    audio["title"] = title
                if artist:
                    audio["artist"] = artist
                if album:
                    audio["album"] = album
                if genre:
                    audio["genre"] = genre
                if track_number:
                    audio["tracknumber"] = str(track_number)
                audio.save()
            elif selected_format in ["webm", "mkv"]:
                if title:
                    command = [
                        "mkvpropedit",
                        input_file,
                        "--edit",
                        "info",
                        "--set",
                        f"title={title}"
                    ]
                    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen des Kommandos: {e}")
        except OSError as e:
            print(f"Fehler beim Dateizugriff: {e}")
        except Exception as e:
            print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
        else:
            print("Metadaten erfolgreich eingebettet")
            return input_file

    @staticmethod
    def embed_subs(input_file, srt_files, downloaded_subs, selected_format):
        try:
            if selected_format in ["mkv", "webm"]:
                temp_output_file = "temp_" + input_file
                command = [
                    'mkvmerge',
                    "-o", temp_output_file,
                    input_file,
                ]
                for index, file in enumerate(srt_files):
                    command.extend(["--language", f"0:{downloaded_subs[index][1]}", file])
                    # command.extend(["--default-track-flag", "0:0"])
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.replace(temp_output_file, input_file)
            elif selected_format == "mp4":
                temp_output_file = "temp_" + input_file
                command = [
                    "ffmpeg",
                    "-i", input_file
                ]
                for i, file in enumerate(srt_files):
                    command.extend(["-i", file])
                command.extend([
                    "-map", "0"
                ])
                for i in range(len(srt_files)):
                    command.extend(["-map", str(i + 1)])
                command.extend([
                    "-c", "copy",
                    "-c:s", "mov_text",
                ])
                # for i, file in enumerate(srt_files):
                #     i += 1
                #     command.extend(["-metadata:s:s:" + str(i), "language=" + downloaded_subs[i-1][1]])
                command.extend([temp_output_file])
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.replace(temp_output_file, input_file)

        except FileNotFoundError as e:
            print(f"Fehler: Eine oder mehrere Dateien wurden nicht gefunden: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Fehler: Beim Ausführen von externem Programm ist ein Fehler aufgetreten: {e}")
        except OSError as e:
            print(f"Fehler: Beim Zugriff auf das Dateisystem ist ein Fehler aufgetreten: {e}")
        except Exception as e:
            print(f"Fehler: Ein unbekannter Fehler ist aufgetreten: {e}")
        else:
            print("Untertitel erfolgreich eingebettet")
            return input_file
        finally:
            PostProcessing.delete_files(*srt_files)