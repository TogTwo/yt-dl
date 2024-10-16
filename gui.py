import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox
import queue
from download import Download, YouTube
from urllib.parse import urlparse
import threading
from post_processing import PostProcessing


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.selected_index = None

        self.combobox_format = None
        self.combobox_thumbnail = None
        self.combobox_subtitle = None
        self.combobox_res = None
        self.combobox_playlist_index = None

        self.start_button = None

        self.listbox_metadata = None
        self.listbox_caption_available = None
        self.listbox_caption_selected = None

        self.entry_title = None
        self.entry_artist = None
        self.entry_album = None
        self.entry_genre = None

        self.stringVar_url = None
        self.stringVar_title = None
        self.stringVar_artist = None
        self.stringVar_album = None
        self.stringVar_genre = None
        self.stringVar_metadata = None
        self.stringVar_caption_available = None
        self.stringVar_caption_selected = None

        self.metadata_list_for_listbox = []
        self.metadata_list = []

        self.list_caption_available = []
        self.list_caption_available_for_listbox = []
        self.list_caption_selected = []
        self.list_caption_selected_for_listbox = []

        self.threads = []

        self.progressbar = None
        self.BooleanVar_OAuth = tk.BooleanVar()
        self.BooleanVar_sync = tk.BooleanVar()
        self.data_queue = queue.Queue()
        self.setup_gui()
        self.check_queue()
        self.check_thread_status()

    def setup_gui(self):
        self.resizable(width=False, height=False)
        # root.columnconfigure(0, weight=1)
        # root.rowconfigure(0, weight=1)
        # root.minsize(600, 400)

        # Frames
        main_frame = ttk.Frame(self, width=400, height=400)
        main_frame.grid(row=0, column=0)

        label_option_frame = ttk.Label(text="Optionen", font="15")
        option_frame = ttk.Labelframe(main_frame, borderwidth=5, relief="solid", labelwidget=label_option_frame)
        option_frame.grid(row=0, column=0, sticky="NEWS")

        label_metadata_frame = ttk.Label(text="Metadaten", font="15")
        metadata_frame = ttk.LabelFrame(main_frame, borderwidth=5, relief="solid", labelwidget=label_metadata_frame)
        metadata_frame.grid(row=0, column=1, sticky="NEWS")

        label_caption_frame = ttk.Label(text="Untertitel", font="15")
        caption_frame = ttk.Labelframe(main_frame, relief="solid", labelwidget=label_caption_frame)
        caption_frame.grid(row=0, column=2, sticky="NEWS")

        # option_frame
        # Label
        label_url = ttk.Label(option_frame, text="Url")
        label_url.grid(row=0, column=0, pady=3, padx=3, columnspan=2)

        label_format = ttk.Label(option_frame, text="Format")
        label_format.grid(row=2, column=0, pady=3, padx=3)

        label_thumbnail = ttk.Label(option_frame, text="Thumbnail")
        label_thumbnail.grid(row=4, column=0, pady=3, padx=3)

        label_subs = ttk.Label(option_frame, text="Untertitel")
        label_subs.grid(row=2, column=1, pady=3, padx=3)

        label_res = ttk.Label(option_frame, text="Video Auflösung")
        label_res.grid(row=4, column=1, pady=3, padx=3)

        label_playlist_index = ttk.Label(option_frame, text="Playlist Index")
        label_playlist_index.grid(row=6, column=0, pady=3, padx=3)

        # ComboBox
        self.combobox_format = ttk.Combobox(option_frame, state="readonly")
        self.combobox_format['values'] = ("opus", "m4a", "mp3", "mkv", "mp4", "webm")
        self.combobox_format.grid(row=3, column=0, pady=3, padx=3)
        self.combobox_format.bind("<<ComboboxSelected>>", self.validate_combobox)
        self.combobox_format.set("Bitte auswählen")

        self.combobox_thumbnail = ttk.Combobox(option_frame, state="readonly")
        self.combobox_thumbnail['values'] = ("Mit Thumbnail", "Ohne Thumbnail")
        self.combobox_thumbnail.grid(row=5, column=0, pady=3, padx=3)
        self.combobox_thumbnail.set("Bitte auswählen")

        self.combobox_subtitle = ttk.Combobox(option_frame, state="readonly")
        self.combobox_subtitle['values'] = ("Mit Untertitel", "Ohne Untertitel")
        self.combobox_subtitle.grid(row=3, column=1, pady=3, padx=3)
        self.combobox_subtitle.set("Bitte auswählen")
        self.combobox_subtitle.bind("<<ComboboxSelected>>", self.validate_combobox)

        self.combobox_res = ttk.Combobox(option_frame, state="readonly")
        self.combobox_res['values'] = ("Automatisch", "144", "240", "360", "480", "720", "1080", "1440", "2160")
        self.combobox_res.set("Automatisch")
        self.combobox_res.grid(row=5, column=1, pady=3, padx=3)

        self.combobox_playlist_index = ttk.Combobox(option_frame, state="disabled")
        self.combobox_playlist_index["values"] = ("Dateiname", "Titelnummer", "Dateiname & Titelnummer")
        self.combobox_playlist_index.set("Bitte auswählen")
        self.combobox_playlist_index.grid(row=7, column=0, pady=3, padx=3)

        # Entry
        validate_url_wrapper = self.register(self.check_url)
        self.stringVar_url = tk.StringVar()
        url_entry = ttk.Entry(option_frame, textvariable=self.stringVar_url, validatecommand=validate_url_wrapper, validate="focusout")
        url_entry.grid(row=1, column=0, pady=3, padx=3, sticky="NEWS", columnspan=2)

        # Button
        self.start_button = ttk.Button(option_frame, text="Start", command=self.wrapper_download_and_process_media)
        self.start_button.grid(row=8, column=0, pady=3, padx=3)

        # Checkbutton
        checkbutton_OAuth = ttk.Checkbutton(option_frame, text="Use OAuth", variable=self.BooleanVar_OAuth)
        checkbutton_OAuth.grid(row=8, column=1, pady=3, padx=3)

        # Progressbar
        self.progressbar = ttk.Progressbar(option_frame, orient="horizontal", mode="indeterminate")
        self.progressbar.grid(row=9, column=0, pady=10, padx=3, columnspan=2)

        # metadata_frame
        # Label
        label_title = ttk.Label(metadata_frame, text="Titel")
        label_title.grid(row=0, column=0, pady=3, padx=3)

        label_artist = ttk.Label(metadata_frame, text="Künstler")
        label_artist.grid(row=2, column=0, pady=3, padx=3)

        label_album = ttk.Label(metadata_frame, text="Album")
        label_album.grid(row=0, column=1, pady=3, padx=3)

        label_genre = ttk.Label(metadata_frame, text="Genre")
        label_genre.grid(row=2, column=1, pady=3, padx=3)

        # Entry
        self.stringVar_title = tk.StringVar()
        self.entry_title = ttk.Entry(metadata_frame, textvariable=self.stringVar_title)
        self.entry_title.grid(row=1, column=0, pady=3, padx=3, sticky="WE")

        self.stringVar_artist = tk.StringVar()
        self.entry_artist = ttk.Entry(metadata_frame, textvariable=self.stringVar_artist)
        self.entry_artist.grid(row=3, column=0, pady=3, padx=3, sticky="WE")

        self.stringVar_album = tk.StringVar()
        self.entry_album = ttk.Entry(metadata_frame, textvariable=self.stringVar_album)
        self.entry_album.grid(row=1, column=1, pady=3, padx=3, sticky="WE")

        self.stringVar_genre = tk.StringVar()
        self.entry_genre = ttk.Entry(metadata_frame, textvariable=self.stringVar_genre)
        self.entry_genre.grid(row=3, column=1, pady=3, padx=3, sticky="WE")

        # Listbox
        self.stringVar_metadata = tk.StringVar(value=self.metadata_list_for_listbox)
        self.listbox_metadata = tk.Listbox(metadata_frame, width=60, height=10, listvariable=self.stringVar_metadata)
        self.listbox_metadata.grid(row=4, column=0, sticky="NEWS", padx=3, pady=3, rowspan=8, columnspan=2)
        self.listbox_metadata.bind("<<ListboxSelect>>", self.show_metadata)

        # Scrollbar
        scrollbar_metadata = ttk.Scrollbar(metadata_frame, orient="horizontal", command=self.listbox_metadata.xview)
        scrollbar_metadata.grid(row=13, column=0, sticky="EW", columnspan=2)
        self.listbox_metadata.configure(xscrollcommand=scrollbar_metadata.set)

        # Button
        button_update_metadata = ttk.Button(metadata_frame, text="Update", command=self.edit_metadata)
        button_update_metadata.grid(row=14, column=0, pady=3, padx=3)

        # checkbutton
        checkbutton_sync = ttk.Checkbutton(metadata_frame, text="Sync", variable=self.BooleanVar_sync)
        checkbutton_sync.grid(row=14, column=1, pady=3, padx=3)

        # caption_frame
        # Label
        label_available_subs = ttk.Label(caption_frame, text="Verfügbare Untertitel")
        label_available_subs.grid(row=0, column=0, columnspan=2)

        label_selected_subs = ttk.Label(caption_frame, text="Ausgewählte Untertitel")
        label_selected_subs.grid(row=3, column=0, columnspan=2)
        # Listbox
        self.stringVar_caption_available = tk.StringVar(value=self.list_caption_available_for_listbox)
        self.listbox_caption_available = tk.Listbox(caption_frame, width=25, height=7, listvariable=self.stringVar_caption_available)
        self.listbox_caption_available.grid(row=1, column=0, columnspan=2, pady=3, padx=3)

        self.stringVar_caption_selected = tk.StringVar(value=self.list_caption_selected_for_listbox)
        self.listbox_caption_selected = tk.Listbox(caption_frame, width=25, height=7, listvariable=self.stringVar_caption_selected)
        self.listbox_caption_selected.grid(row=4, column=0, columnspan=2, pady=3, padx=3)

        # Button
        button_add_available_subs = ttk.Button(caption_frame, text="Hinzufügen", command=self.add_subs)
        button_add_available_subs.grid(row=5, column=0, pady=3, padx=3)

        button_remove_selected_subs = ttk.Button(caption_frame, text="Entfernen", command=self.remove_subs)
        button_remove_selected_subs.grid(row=5, column=1, pady=3, padx=3)

    def validate_combobox(self, event):
        value1 = self.combobox_subtitle.get()
        value2 = self.combobox_format.get()
        invalid_combinations = [
            ("Mit Untertitel", "opus"),
            ("Mit Untertitel", "m4a"),
            ("Mit Untertitel", "mp3")
        ]
        if (value1, value2) in invalid_combinations:
            messagebox.showerror(message="Diese Kombination ist nicht erlaubt.")
            if event.widget == self.combobox_subtitle:
                self.combobox_subtitle.set("Bitte auswählen")
            else:
                self.combobox_format.set("Bitte auswählen")

    def disable_widgets(self):
        self.combobox_format.configure(state="disabled")
        self.combobox_res.configure(state="disabled")
        self.combobox_thumbnail.configure(state="disabled")
        self.combobox_subtitle.configure(state="disabled")
        self.start_button.configure(state="disabled")

    def enable_widgets(self):
        self.combobox_format.configure(state="readonly")
        self.combobox_res.configure(state="readonly")
        self.combobox_thumbnail.configure(state="readonly")
        self.combobox_subtitle.configure(state="readonly")
        self.start_button.configure(state="normal")

    def check_queue(self):
        try:
            while True:
                source, data = self.data_queue.get_nowait()
                if source == "list_caption_available_for_listbox":
                    self.stringVar_caption_available.set(data)
                elif source == "metadata_list_for_listbox":
                    self.stringVar_metadata.set(data)
                elif source == "list_caption_selected_for_listbox":
                    self.stringVar_caption_selected.set(data)
        except queue.Empty:
            pass
        finally:
            self.after(1000, self.check_queue)

    def check_thread_status(self):
        self.threads = [thread for thread in self.threads if thread.is_alive()]
        if len(self.threads) == 0 and self.data_queue.empty():
            self.progressbar.stop()
            self.enable_widgets()
        for thread in self.threads:
            if "get_video_subtitles_and_metadata" in thread.name or "download_and_process_media" in thread.name:
                self.progressbar.start()
                self.disable_widgets()

        self.after(1000, self.check_thread_status)

    def get_video_subtitles_and_metadata(self):
        download = Download(self)
        if download.playlist:
            self.combobox_playlist_index.configure(state="readonly")
            playlist = download.initialize_playlist_instance(download.url)
            urls = playlist.video_urls
        else:
            self.combobox_playlist_index.set("Bitte auswählen")
            self.combobox_playlist_index.configure(state="disabled")
            urls = [download.url]

        self.list_caption_available.clear()
        self.list_caption_available_for_listbox.clear()

        self.list_caption_selected.clear()
        self.list_caption_selected_for_listbox.clear()

        self.metadata_list_for_listbox.clear()
        self.metadata_list.clear()

        self.data_queue.put(("list_caption_available_for_listbox", self.list_caption_available_for_listbox))
        self.data_queue.put(("list_caption_selected_for_listbox", self.list_caption_selected_for_listbox))
        self.data_queue.put(("metadata_list_for_listbox", self.metadata_list_for_listbox))

        for counter, url in enumerate(urls, start=1):
            yt = download.initialize_youtube_instance(url, return_error=True)
            if not isinstance(yt, YouTube):
                self.metadata_list_for_listbox.append(f"{counter}: {yt}")
                self.data_queue.put(("metadata_list_for_listbox", self.metadata_list_for_listbox))
                self.metadata_list.append([yt, "", "", ""])
                continue
            self.get_available_subs(yt)
            self.get_metadata(yt, counter)

    def check_url(self):
        parsed_url = urlparse(self.stringVar_url.get())
        if parsed_url.hostname == "www.youtube.com":
            download = Download(self)
            if download.playlist:
                yt = download.initialize_playlist_instance(download.url)
            else:
                yt = download.initialize_youtube_instance(download.url)
            if yt is not None:
                get_video_subtitles_and_metadata_thread = threading.Thread(target=self.get_video_subtitles_and_metadata, name="get_video_subtitles_and_metadata")
                get_video_subtitles_and_metadata_thread.start()
                self.threads.append(get_video_subtitles_and_metadata_thread)
                return True
            else:
                return False
        else:
            print("Not a valid URL")
            return False

    def get_available_subs(self, yt: YouTube):
        yt.streams
        captions = yt.captions
        if captions:
            for caption in captions:
                if "(auto-generated)" in caption.name:
                    continue
                if caption.name in self.list_caption_available_for_listbox:
                    continue
                self.list_caption_available_for_listbox.append(caption.name)
                self.data_queue.put(("list_caption_available_for_listbox", self.list_caption_available_for_listbox))
                self.list_caption_available.append([caption.name, caption.code])

    def wrapper_download_and_process_media(self):
        download_process_media_thread = threading.Thread(target=self.download_and_process_media, name="download_and_process_media")
        download_process_media_thread.start()
        self.threads.append(download_process_media_thread)

    def download_and_process_media(self):
        download = Download(self)
        if download.playlist:
            download.pl = download.initialize_playlist_instance(download.url)
            if download.pl is not None:
                urls = download.pl.video_urls
                for index, url in enumerate(urls):
                    print(f"Video {index + 1} of {download.pl.length}")
                    download.yt = download.initialize_youtube_instance(url)
                    if download.yt is None:
                        print("-----------------------------------------------------------------------------------")
                        continue
                    download.determine_download_format()
                    stream_available = download.check_for_stream_availability()
                    if stream_available:
                        download.fetch_video_and_audio()
                        video = PostProcessing(download, self)
                        video.process_download(index)
                        print("-----------------------------------------------------------------------------------")
                    else:
                        continue
        else:
            for index, url in enumerate([download.url]):
                download.yt = download.initialize_youtube_instance(url)
                if download.yt is None:
                    print("-----------------------------------------------------------------------------------")
                    continue
                download.determine_download_format()
                stream_available = download.check_for_stream_availability()
                if stream_available:
                    download.fetch_video_and_audio()
                    video = PostProcessing(download, self)
                    video.process_download(index)
                    print("-----------------------------------------------------------------------------------")
                else:
                    continue

    def edit_metadata(self, event=None):
        if self.selected_index is not None:
            self.metadata_list[self.selected_index][0] = self.stringVar_title.get()
            self.metadata_list[self.selected_index][1] = self.stringVar_artist.get()
            self.metadata_list[self.selected_index][2] = self.stringVar_album.get()
            self.metadata_list[self.selected_index][3] = self.stringVar_genre.get()
            counter = self.selected_index + 1
            self.metadata_list_for_listbox[self.selected_index] = (
                f"{counter}: "
                f"{self.metadata_list[self.selected_index][0]} || "
                f"{self.metadata_list[self.selected_index][1]} || "
                f"{self.metadata_list[self.selected_index][2]} || "
                f"{self.metadata_list[self.selected_index][3]}"
                )
            self.stringVar_metadata.set(self.metadata_list_for_listbox)

            if self.BooleanVar_sync.get():
                album = self.metadata_list[self.selected_index][2]
                genre = self.metadata_list[self.selected_index][3]
                for metadata in self.metadata_list:
                    metadata[2] = album
                    metadata[3] = genre

                for index, metadata in enumerate(self.metadata_list):
                    self.metadata_list_for_listbox[index] = (
                        f"{index+1}: "
                        f"{metadata[0]} || "
                        f"{metadata[1]} || "
                        f"{metadata[2]} || "
                        f"{metadata[3]}"
                    )
                self.stringVar_metadata.set(self.metadata_list_for_listbox)









    def show_metadata(self, event=None):
        selected_indices = self.listbox_metadata.curselection()
        if selected_indices:
            self.selected_index = selected_indices[0]
            self.entry_title.delete(0, "end")
            self.entry_title.insert(0, self.metadata_list[self.selected_index][0])
            self.entry_artist.delete(0, "end")
            self.entry_artist.insert(0, self.metadata_list[self.selected_index][1])
            self.entry_album.delete(0, "end")
            self.entry_album.insert(0, self.metadata_list[self.selected_index][2])
            self.entry_genre.delete(0, "end")
            self.entry_genre.insert(0, self.metadata_list[self.selected_index][3])

    def get_metadata(self, yt: YouTube, counter):
        title = yt.title
        artist = yt.author
        album = self.stringVar_album.get()
        genre = self.stringVar_genre.get()
        self.metadata_list_for_listbox.append(f"{counter}: {title} || {artist} || {album} || {genre}")
        self.data_queue.put(("metadata_list_for_listbox", self.metadata_list_for_listbox))
        self.metadata_list.append([title, artist, album, genre])

    def add_subs(self):
        selected_index = self.listbox_caption_available.curselection()
        if len(selected_index) == 0:
            return
        elif self.listbox_caption_available.get(selected_index) in self.listbox_caption_selected.get(0, tk.END):
            return
        self.list_caption_selected_for_listbox.append(self.listbox_caption_available.get(selected_index))
        self.stringVar_caption_selected.set(self.list_caption_selected_for_listbox)
        self.list_caption_selected.append(self.list_caption_available[selected_index[0]])

    def remove_subs(self):
        selected_index = self.listbox_caption_selected.curselection()
        if len(selected_index) == 0:
            return
        self.list_caption_selected_for_listbox.pop(selected_index[0])
        self.stringVar_caption_selected.set(self.list_caption_selected_for_listbox)
        self.list_caption_selected.pop(selected_index[0])