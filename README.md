# YouTube Downloader

A Python application to download YouTube videos and playlists with post-processing features like file conversion, metadata editing, and embedding subtitles and thumbnails, wiht a simpel GUI.

## Features

- Download YouTube videos and playlists.
- Convert files to various formats.
- Edit metadata.
- Embed subtitles in MKV, WebM and MP4 files.
- Embed Thumbnails

## Requirements

The project relies on several external tools to enable all its features:

- **ffmpeg** – used extensively for converting downloaded media files to different formats.
- **mkvmerge** – required for embedding subtitles in MKV and WebM files.
- **mkvpropedit** – used for editing MKV file metadata and thumbnails.
- **AtomicParsley** – used for embedding thumbnails in MP4 files.
