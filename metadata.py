class Metadata:
    def __init__(self, title: str, artist: str, album: str, genre: str, playlist_index: int):
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.playlist_index = playlist_index

    def __dir__(self):
        return 