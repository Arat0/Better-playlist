import tkinter as tk
from tkinter import messagebox
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

# Set up API credentials
client_id = 'SPOTIFY_CLIENT_ID'
client_secret = 'SPOTIFY_CLIENT_SECRET'
redirect_uri = 'http://localhost:8888/callback'
# Define the necessary scopes
scope = "user-library-read user-modify-playback-state user-read-playback-state app-remote-control"
# Use the SpotifyOAuth method to get an authenticated Spotify object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))


class ResultWindow(tk.Frame):
    """
    ResultWindow class inherits from tk.Frame and displays the results of a search query.
    It provides options to play a song, add a song to the queue, and switch between light and dark themes.
    """
    def __init__(self, master, sp, results, **kwargs):
        """
        This method initializes the ResultWindow object, sets up the Spotify object, the results, 
        the default theme, and the window size. It also calls the methods to create the widgets and 
        update the results.
        """
        super().__init__(master, **kwargs)
        self.master = master
        self.sp = sp  # Store the Spotify object
        self.results = results
        # Add variables for pagination
        self.results_per_page = 10
        self.current_page = 0
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.dark_mode = False  # Set default theme to light mode

        # Set window size
        self.master.geometry('800x600')

        self.create_widgets()
        self.update_results()

        self.pack(fill="both", expand=True)

    def create_widgets(self):
        """
        This method creates all widgets that are displayed on the ResultWindow frame.
        These include title, results, and buttons for switching the theme and exiting.
        """
        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="both", expand=True)
        self.title_label = tk.Label(self.title_frame, text="Search Results", font=("Arial", 20))
        self.title_label.pack()

        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill="both", expand=True)

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill="both", expand=True)

        self.theme_button = tk.Button(self.bottom_frame, text="Switch Theme", command=self.switch_theme, font=("Arial", 12))
        self.theme_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(self.bottom_frame, text="Exit", command=self.master.destroy, font=("Arial", 12))
        self.exit_button.pack(side=tk.RIGHT, padx=10)

    def configure_widget(self, widget, **options):
        """
        This method configures a widget with the given options, ignoring any options that the widget does not support.
        """
        try:
            widget.config(**options)
        except tk.TclError:
            pass

    def update_results(self):
        """
        This method updates the displayed results based on the current page.
        It clears old results and then shows the results for the current page, 
        creating a new frame for each result with the track name and options to play or add to the queue.
        It also updates the previous and next page buttons based on the current page.
        """
        # Clear old results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Calculate start and end indices for the results on the current page
        start = self.current_page * self.results_per_page
        end = start + self.results_per_page

        for i in range(start, min(end, len(self.results))):
            result = tk.Frame(self.result_frame, bd=2, relief="groove")
            result.pack(fill=tk.X, padx=10, pady=5)

            result_name = tk.Label(result, text=f"{self.results[i]['name']} - {self.results[i]['album']} - {self.results[i]['artist']}")
            result_name.pack(side=tk.LEFT, padx=5)

            result_button_frame = tk.Frame(result)
            result_button_frame.pack(side=tk.RIGHT, padx=5)

            result_play_button = tk.Button(result_button_frame, text="Play", command=lambda i=i: self.play_song(i))
            result_play_button.pack(side=tk.LEFT, padx=5)

            result_queue_button = tk.Button(result_button_frame, text="Add to Queue", command=lambda i=i: self.queue_song(i))
            result_queue_button.pack(side=tk.LEFT, padx=5)

        # Add buttons for previous and next page
        pagination_frame = tk.Frame(self.result_frame)
        pagination_frame.pack(pady=10)
        
        if self.current_page > 0:
            prev_button = tk.Button(pagination_frame, text="Previous Page", command=self.prev_page)
            prev_button.pack(side=tk.LEFT, padx=5)
        if end < len(self.results):
            next_button = tk.Button(pagination_frame, text="Next Page", command=self.next_page)
            next_button.pack(side=tk.RIGHT, padx=5)

    def prev_page(self):
        """
        This method decreases the current page by 1 and updates the results.
        """
        self.current_page -= 1
        self.update_results()

    def next_page(self):
        """
        This method increases the current page by 1 and updates the results.
        """
        self.current_page += 1
        self.update_results()

    def play_song(self, index):
        """
        This method starts playback of the song at the given index in the results.
        If no active device is found, it shows an info message.
        """
        playback_info = self.sp.current_playback()
        if not playback_info or not playback_info['is_playing']:
            tk.messagebox.showinfo("No Active Device", "No active device found. Please open Spotify on your device and try again.")
            return
        track_uri = self.results[index]["uri"]
        self.sp.start_playback(uris=[track_uri])

    def queue_song(self, index):
        """
        This method adds the song at the given index in the results to the queue.
        If no active device is found, it shows an info message.
        """
        playback_info = self.sp.current_playback()
        if not playback_info or not playback_info['is_playing']:
            tk.messagebox.showinfo("No Active Device", "No active device found. Please open Spotify on your device and try again.")
            return
        track_url= self.results[index]["uri"]
        self.sp.add_to_queue(track_url)
    
    def update(self, **kwargs):
        """
        This method updates the state of the ResultWindow.
        If new results are provided, it updates the displayed results.
        """
        # Update results if provided.
        if 'results' in kwargs:
            self.results = kwargs['results']
            self.update_results()

    def new_search(self):
        """
        This method switches the frame to the SearchWindow.
        """
        self.master.show_frame("SearchWindow")

    def switch_theme(self):
        """
        This method switches the color theme between light and dark mode.
        It updates the color scheme of all widgets in the window.
        """
        self.dark_mode = not self.dark_mode  # Toggle the boolean variable
        if self.dark_mode:
            # Dark theme colors
            new_bg = "#E1D6F8"
            new_fg = "#25629B"
            new_highlight = "#052A6A"
        else:
            # Light theme colors
            new_bg = "#e8d5d3"
            new_fg = "#9E2224"
            new_highlight = "#B2Adb4"

            # Apply the new colors to all widgets
        for widget in self.winfo_children() + self.title_frame.winfo_children() + self.bottom_frame.winfo_children():
            widget.config(bg=new_bg)
            if isinstance(widget, (tk.Label, tk.Button)):
                widget.config(fg=new_fg)

    # Update result entries' color
        for result in self.result_frame.winfo_children():
            result.config(bg=new_bg)
            for widget in result.winfo_children():
                widget.config(bg=new_bg)
                if isinstance(widget, (tk.Label, tk.Button)):
                    widget.config(fg=new_fg)


class SearchWindow(tk.Frame):
    """
    SearchWindow class inherits from tk.Frame and provides an interface for the user to enter search queries.
    It also allows the user to switch between light and dark themes.
    """
    def __init__(self, master, sp, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.sp = sp
        self.pack(fill="both", expand=True)
        self.dark_mode = False  # Default color theme is light mode
        self.create_widgets()

    def create_widgets(self):
        """
        This method creates all widgets that are displayed on the SearchWindow frame.
        These include instructions, search label and entry, search button, switch theme button, and exit button.
        """
        instructions_text = (
                "Instructions: \n"
                "To use this program effectively, you must be a Spotify Premium subscriber.\n"
                "Please ensure that you have a Spotify application\n"
                "logged into the same account that you authorize for this program, and that\n"
                "this application is actively playing music.\n"
                "This is necessary for your device to be recognized by the program."
            )

        self.instructions = tk.Label(
                self, 
                text=instructions_text, 
                bg="#e8d5d3", 
                font=("Arial", 14), 
                wraplength=400,  # You can adjust this value to fit your needs
                justify='left'
            )
        self.instructions.pack(side="top", padx=10, pady=10)

        self.search_label = tk.Label(self, text="Search:", bg="#e8d5d3", font=("Arial", 14))
        self.search_label.pack(side="top", padx=10, pady=10)

        self.search_entry = tk.Entry(self, highlightthickness=2, highlightbackground="#B2Adb4", highlightcolor="#B2Adb4", font=("Arial", 14))
        self.search_entry.pack(side="top", padx=5, pady=10, fill="x", expand=True)

        self.search_button = tk.Button(self, text="Search", command=self.search, bg="#9E2224", fg="white", font=("Arial", 14))
        self.search_button.pack(side="top", padx=5, pady=10)

        self.theme_button = tk.Button(self, text="Switch Theme", command=self.switch_theme, bg="#9E2224", fg="white", font=("Arial", 14))
        self.theme_button.pack(side="top", padx=5, pady=10)

        # Here's the updated exit button
        self.exit_button = tk.Button(self, text="Exit", command=self.master.master.destroy, bg="#9E2224", fg="white", font=("Arial", 14))
        self.exit_button.pack(side="top", padx=5, pady=10)

    
    def search(self):
        """
        This method executes when the search button is clicked. 
        It queries the Spotify API for tracks and albums based on the user's search input.
        If any results are found, they are passed to the ResultWindow frame.
        """
        query = self.search_entry.get()
        results = self.sp.search(q=query, type='track,album')
    # Handle empty results
        if not results['tracks']['items']:
            tk.messagebox.showinfo("No Results", "No tracks or albums found for your search.")
            return
        self.results = []
        for track in results['tracks']['items']:
            track_info = {
                "id": track['id'],
                "name": track['name'],
                "artist": ", ".join([artist['name'] for artist in track['artists']]),
                "album": track['album']['name'],
                "preview_url": track['preview_url'],
                "uri": track['uri']  # Add this line
            }

            self.results.append(track_info)
            self.master.show_frame("ResultWindow", results=self.results)

    def switch_theme(self):
        self.dark_mode = not self.dark_mode  # Toggle the boolean variable
        if self.dark_mode:
            # Dark theme colors
            new_bg = "#E1D6F8"
            new_fg = "#25629B"
            new_highlight = "#052A6A"
        else:
            # Light theme colors
            new_bg = "#e8d5d3"
            new_fg = "#9E2224"
            new_highlight = "#B2Adb4"

        # Apply the new colors to all widgets
        self.config(bg=new_bg)
        self.instructions.config(bg=new_bg, fg=new_fg)
        self.search_label.config(bg=new_bg, fg=new_fg)
        self.search_entry.config(highlightbackground=new_highlight, highlightcolor=new_highlight, bg=new_bg, fg=new_fg)
        self.search_button.config(bg=new_highlight, fg=new_fg)
        self.theme_button.config(bg=new_highlight, fg=new_fg)
        self.exit_button.config(bg=new_highlight, fg=new_fg)
        
    def update(self, **kwargs):
        # No state to update
        pass


    def search(self):
        query = self.search_entry.get()
        results = self.sp.search(q=query, type='track,album')
    # Handle empty results
        if not results['tracks']['items']:
            tk.messagebox.showinfo("No Results", "No tracks or albums found for your search.")
            return
        self.results = []
        for track in results['tracks']['items']:
            track_info = {
                "id": track['id'],
                "name": track['name'],
                "artist": ", ".join([artist['name'] for artist in track['artists']]),
                "album": track['album']['name'],
                "preview_url": track['preview_url'],
                "uri": track['uri']  # Add this line
            }

            self.results.append(track_info)
            self.master.show_frame("ResultWindow", results=self.results)


    def switch_theme(self):
        """
        This method is bound to the switch theme button.
        It toggles between light and dark theme color modes, updating the color scheme of all widgets.
        """
        self.dark_mode = not self.dark_mode  # Toggle the boolean variable
        if self.dark_mode:
            # Dark theme colors
            new_bg = "#E1D6F8"
            new_fg = "#25629B"
            new_highlight = "#052A6A"
        else:
            # Light theme colors
            new_bg = "#e8d5d3"
            new_fg = "#9E2224"
            new_highlight = "#B2Adb4"

        # Apply the new colors to all widgets
        self.config(bg=new_bg)
        self.instructions.config(bg=new_bg, fg=new_fg)
        self.search_label.config(bg=new_bg, fg=new_fg)
        self.search_entry.config(highlightbackground=new_highlight, highlightcolor=new_highlight, bg=new_bg, fg=new_fg)
        self.search_button.config(bg=new_highlight, fg=new_fg)
        self.theme_button.config(bg=new_highlight, fg=new_fg)
        self.exit_button.config(bg=new_highlight, fg=new_fg)
        
    def update(self, **kwargs):
        """
        This method is used to update the state of the SearchWindow.
        Currently, it does nothing as there is no state to update.
        """
        # No state to update
        pass

class MainWindow(tk.Frame):
    """
    MainWindow class inherits from tk.Frame and serves as the main application window.
    It manages and switches between different frames (like SearchWindow and ResultWindow) based on user interactions.
    """
    def __init__(self, master, sp, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sp = sp  # Store the Spotify object
        self.frames = {}

        # Initialize frames and store them in the frames dictionary
        search_frame = SearchWindow(master=self, sp=self.sp)
        self.frames["SearchWindow"] = search_frame

        search_frame.pack(fill="both", expand=True)

    def show_frame(self, frame_name, **kwargs):
        """
        This function takes a frame_name as input and retrieves the frame instance from the frames dictionary.
        If the frame does not exist, it creates and stores a new instance.
        It raises the specified frame to the front, making it visible to the user.
        """
        frame = self.frames.get(frame_name)  # Retrieve the frame instance
        if not frame:
            result_frame = ResultWindow(master=tk.Toplevel(), sp=self.sp, results=kwargs.get('results', []))
            self.frames[frame_name] = result_frame
            result_frame.pack(fill="both", expand=True)
            frame = result_frame
        else:
            frame.update(**kwargs)
        frame.tkraise()  # Raise the frame to the front

    def update_frame(self, frame_name, **kwargs):
        """
        This function updates a frame with new data by calling the update method on the frame instance.
        """
        frame = self.frames[frame_name]
        frame.update(**kwargs)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Music Player")
    app = MainWindow(root, sp=sp)  # Pass the Spotify object to the MainWindow
    app.pack(fill="both", expand=True)
    root.mainloop()

