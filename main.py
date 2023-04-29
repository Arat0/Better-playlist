import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# Set up API credentials
client_id = '38d005a17f724a3c82ef2e40a3974d03'
client_secret = 'c8ebb4ef39d14bb9a5e5f361e1443c31'
scope = 'user-library-read'
redirect_uri = 'http://localhost:8888/callback'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri=redirect_uri))


#this Window is for searching the song
class SearchWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.search_label = tk.Label(self, text="Search:")
        self.search_label.pack(side="left")

        self.search_entry = tk.Entry(self)
        self.search_entry.pack(side="left")

        self.search_button = tk.Button(self, text="Search", command=self.search)
        self.search_button.pack(side="left")

class ResultWindow(tk.Frame):
    def __init__(self, master=None, results=None):
        super().__init__(master)
        self.master = master
        self.results = results
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        for result in self.results['tracks']['items']:
            result_frame = tk.Frame(self)
            result_frame.pack()

            title_label = tk.Label(result_frame, text=result['name'])
            title_label.pack()

            artist_label = tk.Label(result_frame, text=result['artists'][0]['name'])
            artist_label.pack()

            length_label = tk.Label(result_frame, text=f"Length: {result['duration_ms'] / 1000} seconds")
            length_label.pack()

        for result in self.results['albums']['items']:
            result_frame = tk.Frame(self)
            result_frame.pack()

            title_label = tk.Label(result_frame, text=result['name'])
            title_label.pack()

            artist_label = tk.Label(result_frame, text=result['artists'][0]['name'])
            artist_label.pack()

            release_date_label = tk.Label(result_frame, text=f"Release date: {result['release_date']}")
            release_date_label.pack()


class app(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Search")
        self.geometry("500x500")
        self.switch_frame(SearchWindow)

    def switch_frame(self, frame_class, results=None):
        new_frame = frame_class(self, results=results)
        new_frame.pack()
        self._frame.destroy()
        self._frame = new_frame
