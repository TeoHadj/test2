import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from webscrape2 import get_wiki_genres
from database import populate_database, reset_database
from queries import print_full_song_view
import tkinter as tk
from tkinter import font



to_try = ["", "_(singer)", "_(musician)", "_(DJ)", "_(band)", "_(British_band)"]

CLIENT_ID = '04df9df5cd8e400483dc0cfbce4dcd66'
CLIENT_SECRET = '202662453275474f801833a07e418586'
REDIRECT_URI = 'http://127.0.0.1:8000/callback'  # You can change this to your preferred URI

# Set up the SpotifyOAuth object for authentication
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         redirect_uri=REDIRECT_URI,
                         scope="user-library-read user-top-read")  # Example scopes, adjust as needed

# Create a Spotify instance using the authorization manager
sp = spotipy.Spotify(auth_manager=sp_oauth)


# Get the current user’s information
user = sp.current_user()
print(f"Authorized as: {user['display_name']}")



offset = 0
limit = 50  # Number of tracks per request
all_tracks = []

# Use a loop to paginate through all the saved tracks
while True:
    # Fetch a page of saved tracks
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    all_tracks.extend(results['items'])  # Add the fetched tracks to the list

    # Check if there are more tracks to fetch
    if len(results['items']) < limit:
        break  # No more tracks, exit the loop

    # Update the offset to get the next set of tracks
    offset += limit

#pull names of all songs and add to a list
song_ids = []
for item in all_tracks:
    track = item['track']
    track_id = track['id']
    song_ids.append(track_id)

print(song_ids)



song_names = []
for item in all_tracks:
    track = item['track']
    track_name = track['name']
    song_names.append(track_name)

song_artists = []

for item in all_tracks:
    track = item['track']
    temp_names = []
    for artist in track['artists']:
        temp_names.append(artist['name'])
    song_artists.append(temp_names)

song_duration = []
for item in all_tracks:
    track = item['track']
    temp_duration = track['duration_ms']//1000
    song_duration.append(temp_duration)

print(song_names)
print(song_duration)
print(song_artists)

song_release_dates = []
for item in all_tracks:
    track = item['track']
    song_release_dates.append(track['album']['release_date'])

print(song_release_dates)

song_albums = []
for item in all_tracks:
    track = item['track']
    song_albums.append(track['album']['name'])

print(song_albums)


artist_ids = []
for item in all_tracks:
    track = item['track']
    for artist in track['artists']:
        artist_ids.append(artist['id'])

# Remove duplicates
artist_ids = list(set(artist_ids))

# Fetch artist info in batches of up to 50
artist_genre_map = {}
batch_size = 50
for i in range(0, len(artist_ids), batch_size):
    batch = artist_ids[i:i + batch_size]
    results = sp.artists(batch)
    for artist in results['artists']:
        artist_genre_map[artist['id']] = artist.get('genres', [])



    time.sleep(0.2)  # slight pause to be kind to API

# Now map genres back to each song
song_genres = []
missing_artist_names = []
for item in all_tracks:
    track = item['track']
    track_genres = []
    for artist in track['artists']:
        track_genres.extend(artist_genre_map.get(artist['id'], []))
    song_genres.append(list(set(track_genres)))
print(song_genres)

# for index in range(len(song_genres)):
#     if not song_genres[index]:
#         missing_artist_names.append([song_artists[index], index])
#
# print(missing_artist_names)
# #missing_artist_genres = [[] for i in range(len(missing_artist_names))]
# missing_artist_genres = [[] for i in range(10)]
# # for i in range(len(missing_artist_names)):
# for i in range(10):
#     Found = False
#     while not Found:
#         print(f"{i+1} out of 10")
#         artist = missing_artist_names[i][0][0]
#
#
#         page_title = artist.replace(" ", "_")
#
#         for ending in to_try:
#             url = f"https://en.wikipedia.org/wiki/{page_title}"
#             url += ending
#             genres = get_wiki_genres(url)
#
#             if len(genres) > 0:
#                 missing_artist_genres[i] = genres
#                 Found = True
#                 break
#
#         if not missing_artist_genres[i]:
#                 for ending in to_try:
#                     url = f"https://en.wikipedia.org/wiki/{page_title.title()}"
#                     url += ending
#                     genres = get_wiki_genres(url)
#                     if len(genres) > 0:
#                         missing_artist_genres[i] = genres
#                         Found = True
#                         break
#     # print(f"{i} out of {len(missing_artist_genres)}")
#         if not missing_artist_genres[i]:
#             missing_artist_genres[i] = []
#             Found = True
#             break
#
# print(missing_artist_genres)
#
# for i in range(10):
#     insert_index = missing_artist_names[i][1]
#     song_genres[insert_index] = missing_artist_genres[i]
reset_database()
populate_database(song_names, song_artists, song_duration, song_release_dates, song_albums, song_genres, song_ids)


songsUse = []
for i in range(len(song_names)):
    songsUse.append({
        "name": song_names[i],
        "artists": song_artists[i],
        "album": song_albums[i]
    })

class Menu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.configure(bg="light blue")

        # Fonts
        self.title_font = font.Font(family="Helvetica", size=36, weight="bold")
        self.box_font = font.Font(family="Helvetica", size=30, weight="bold")

        # Title
        self.title_label = tk.Label(
            self,
            text="VibeList",
            font=self.title_font,
            bg="light blue",
            fg="white"
        )
        self.title_label.pack(pady=30)

        # Container for boxes
        self.box_container = tk.Frame(self, bg="light blue")
        self.box_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        self.box_container.columnconfigure((0, 1, 2), weight=1)
        self.box_container.rowconfigure(0, weight=1)

        # Big menu boxes
        self.view_button = tk.Button(
            self.box_container,
            text="View Music",
            font=self.box_font,
            command=self.music_view,
            bg="#F7F7F2",
            fg="black",
            relief="flat"
        )

        self.sort_button = tk.Button(
            self.box_container,
            text="Sort Music",
            font=self.box_font,
            command=self.window_one,
            bg="#F7F7F2",
            fg="black",
            relief="flat"
        )

        self.recommend_button = tk.Button(
            self.box_container,
            text="Recommend Music",
            font=self.box_font,
            command=self.recommend_view,
            bg="#F7F7F2",
            fg="black",
            relief="flat"
        )

        # Layout
        self.view_button.grid(row=0, column=0, sticky="nsew", padx=15)
        self.sort_button.grid(row=0, column=1, sticky="nsew", padx=15)
        self.recommend_button.grid(row=0, column=2, sticky="nsew", padx=15)

    def window_one(self):
        self.destroy()
        Music_Sort(self.master)

    def music_view(self):
        self.destroy()
        Music_View(self.master)

    def recommend_view(self):
        self.destroy()
        Recommend_View(self.master)


class Music_Sort(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(self, text="Sort Music", font=("Helvetica", 24))
        self.menu_button = tk.Button(self, text="Menu", command=self.menu)

        self.title_label.pack(pady=20)
        self.menu_button.pack()

    def menu(self):
        self.destroy()
        Menu(self.master)


class Music_View(tk.Frame):
    def __init__(self, parent, songs = songsUse):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.songs = songs

        self.title_label = tk.Label(self, text="View Music", font=("Helvetica", 24))
        self.menu_button = tk.Button(self, text="Menu", command=self.menu)

        self.title_label.pack(pady=20)
        self.menu_button.pack()

        song_container = tk.Frame(self)
        song_container.pack(fill=tk.BOTH, expand=True, padx = 10, pady = 10)
        canvas = tk.Canvas(song_container)
        scrollbar = tk.Scrollbar(song_container, orient="vertical", command = canvas.yview)
        self.scrollableframe = tk.Frame(canvas)

        self.scrollableframe.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollableframe, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))


        for song in self.songs:
            label = tk.Label(
                self.scrollableframe,
                text=f"{song['name']} – {', '.join(song['artists'])} ({song['album']})",
                anchor="w"
            )
            label.pack(fill="x", padx=20, pady=2)

    def menu(self):
        self.destroy()
        Menu(self.master)





class Recommend_View(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(self, text="Recommend Music", font=("Helvetica", 24))
        self.menu_button = tk.Button(self, text="Menu", command=self.menu)

        self.title_label.pack(pady=20)
        self.menu_button.pack()

    def menu(self):
        self.destroy()
        Menu(self.master)



root = tk.Tk()
root.title("VibeList")
root.geometry("1000x600")
root.minsize(800, 500)

Menu(root)


root.mainloop()