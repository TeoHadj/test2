import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from Add_playlist import add_playlist
from webscrape2 import get_wiki_genres
from database import populate_database, reset_database
from queries import get_all_artists, get_all_genres, get_song_with_artist, get_song_with_genre, get_song_with_year, genre_count, artist_count, genre_count_with_artist_name
import tkinter as tk
from tkinter import font
from Add_playlist import add_playlist
from sqlalchemy.orm import Session
from database import engine
from recommendations import cosine_similarity
import math

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
print(f"Authorised as: {user['display_name']}")



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

# print(song_ids)



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

# print(song_names)
# print(song_duration)
# print(song_artists)

song_release_dates = []
for item in all_tracks:
    track = item['track']
    song_release_dates.append(track['album']['release_date'])

# print(song_release_dates)

song_albums = []
for item in all_tracks:
    track = item['track']
    song_albums.append(track['album']['name'])

# print(song_albums)


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
# print(song_genres)

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
genreOptions = sorted(get_all_genres())
artistOptions = sorted(get_all_artists())

yearOptions = []
for date in song_release_dates:
    if date[:4] not in yearOptions:
        yearOptions.append(date[:4])
yearOptions = sorted(yearOptions)
optionsGlobal = ["By Genre", "By Year Released", "By Artist"]


genre_percentages = {}
no_songs = len(song_names)
with Session(engine) as session:
    for genre in genreOptions:
        no_genre = genre_count(session, genre)
        genre_percentages[genre] = no_genre/no_songs


artist_percentages = {}
with Session(engine) as session:
    for artist in artistOptions:
        no_artist = artist_count(session, artist)
        artist_percentages[artist] = no_artist/no_songs
top_10_genres = sorted(genre_percentages, key = genre_percentages.get, reverse = True)[:10]
top_10_artists = sorted(artist_percentages, key = artist_percentages.get, reverse = True)[:10]

artist_cosine_match = {}
with Session(engine) as session:
    for artist in top_10_artists:
        artist_genre_percentages = {}
        for genre in genreOptions:
            temp_no_artist = artist_count(session, artist)
            no_specific_genre_for_artist = genre_count_with_artist_name(session, genre, artist)
            artist_genre_percentages[genre] = no_specific_genre_for_artist/temp_no_artist

        artist_cosine_match[artist] = cosine_similarity(list(artist_genre_percentages.values()), list(genre_percentages.values()))
print(artist_cosine_match)
top5_artists = sorted(artist_cosine_match, key = artist_cosine_match.get, reverse = True)[:5]
print(top5_artists)
songsUse = []
for i in range(len(song_names)):
    songsUse.append({
        "name": song_names[i],
        "artists": song_artists[i],
        "album": song_albums[i]
    })


top5_songs = {}
def get_artist_id(name):
    result = sp.search(f"artist:{name}", type="artist", limit=1)
    return result["artists"]["items"][0]["id"]

for artist in top5_artists:
    artist_id = get_artist_id(artist)
    top_tracks = sp.artist_top_tracks(artist_id, "US")
    top5_songs[artist] = top_tracks["tracks"]

for artist in top5_artists:
    for track in top5_songs[artist]:
        if track['name'] not in song_names:
            print(track['name'], track['artists'][0]['name'], track['popularity'])

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
    def __init__(self, parent, options = optionsGlobal):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.configure(bg="light blue")
        self.playlist_button_state = False
        self.lookup = {}
        self.options = options
        self.playlist = []
        self.value_inside_menu = tk.StringVar()
        self.value_in_year_menu = tk.StringVar()
        self.value_in_year_menu.set("Select Year")
        self.value_inside_menu.set("Select How You Want Music to be Sorted")
        self.title_label = tk.Label(self, text="Sort Music", font=("Helvetica", 24))
        self.menu_button = tk.Button(self, text="Menu", command=self.menu)
        self.options = tk.OptionMenu(self, self.value_inside_menu, *self.options)
        self.genre_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height=15)
        for genre in genreOptions:
            self.genre_menu.insert(tk.END, genre)
        self.year_menu = tk.OptionMenu(self, self.value_in_year_menu, *yearOptions)
        self.artist_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height=15)
        for artist in artistOptions:
            self.artist_menu.insert(tk.END, artist)
        self.title_label.pack(pady=20)
        self.menu_button.pack()
        self.options.pack()
        self.value_inside_menu.trace_add("write", self.check)
        self.value_in_year_menu.trace_add("write", self.display_year_match)
        self.genre_confirm_button = tk.Button(self, text = "Confirm Genres", command = self.confirm_genres)
        self.artist_confirm_button = tk.Button(self, text="Confirm Artists", command=self.confirm_artists)
        self.genre_match_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height=15)
        self.artist_match_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height=15)
        self.year_match_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height=15)
        self.add_to_playlist_button = tk.Button(self, text="Add songs to new playlist", command = self.add_to_playlist)
        self.view_playlist_button = tk.Button(self, text = "View New Playlist", command = self.view_playlist)
        self.view_playlist_button.pack()
        self.view_playlist_menu = tk.Listbox(self, selectmode=tk.MULTIPLE, height = 15)
        self.remove_from_playlist_button = tk.Button(self, text = "Remove song from playlist", command = self.remove_from_playlist)
        self.clear_playlist_button = tk.Button(self, text = "Clear playlist", command = self.clear_playlist)
        self.create_playlist_button = tk.Button(self, text = "Add Playlist to Spotify Account", command = self.create_playlist)
        self.value_inside_name_entry = tk.StringVar()
        self.playlist_name_entry = tk.Entry(self, textvariable = self.value_inside_name_entry)
        self.name_entry_label = tk.Label(self, text = "Enter name of playlist: ")
        self.pls_enter_name_label = tk.Label(self, text = "Please enter a name for the playlist")


    def check(self, *args):
        if self.value_inside_menu.get() == "By Genre":
            self.pls_enter_name_label.forget()
            self.clear_playlist_button.forget()
            self.name_entry_label.forget()
            self.playlist_name_entry.forget()
            self.remove_from_playlist_button.forget()
            self.create_playlist_button.forget()
            self.view_playlist_menu.forget()
            self.add_to_playlist_button.forget()
            self.artist_confirm_button.forget()
            self.year_menu.forget()
            self.artist_menu.forget()
            self.artist_match_menu.forget()
            self.year_match_menu.forget()
            self.genre_match_menu.forget()
            self.genre_menu.pack(side="left", fill="both", expand=True)
            self.genre_confirm_button.pack()

        elif self.value_inside_menu.get() == "By Year Released":
            self.pls_enter_name_label.forget()
            self.clear_playlist_button.forget()
            self.name_entry_label.forget()
            self.playlist_name_entry.forget()
            self.remove_from_playlist_button.forget()
            self.create_playlist_button.forget()
            self.view_playlist_menu.forget()
            self.add_to_playlist_button.forget()
            self.artist_match_menu.forget()
            self.year_match_menu.forget()
            self.genre_match_menu.forget()
            self.artist_confirm_button.forget()
            self.genre_confirm_button.forget()
            self.genre_menu.forget()
            self.artist_menu.forget()
            self.year_menu.pack()

        else:
            self.pls_enter_name_label.forget()
            self.clear_playlist_button.forget()
            self.name_entry_label.forget()
            self.playlist_name_entry.forget()
            self.remove_from_playlist_button.forget()
            self.create_playlist_button.forget()
            self.view_playlist_menu.forget()
            self.add_to_playlist_button.forget()
            self.artist_match_menu.forget()
            self.year_match_menu.forget()
            self.genre_match_menu.forget()
            self.genre_confirm_button.forget()
            self.genre_menu.forget()
            self.year_menu.forget()
            self.artist_menu.pack(side="left", fill="both", expand=True)
            self.artist_confirm_button.pack()

    def confirm_genres(self):
        selected_genres = [self.genre_menu.get(i) for i in self.genre_menu.curselection()]
        self.genre_menu.forget()
        print(selected_genres)
        self.display_genre_match(selected_genres)



    def confirm_artists(self):
        selected_artists = [self.artist_menu.get(i) for i in self.artist_menu.curselection()]
        self.artist_menu.forget()
        print(selected_artists)
        self.display_artist_match(selected_artists)

    def display_genre_match(self, selected_genres):
        self.genre_confirm_button.forget()
        genre_match = get_song_with_genre(selected_genres)
        self.genre_match_menu.delete(0, tk.END)
        for index, [title, uri] in enumerate(genre_match):
            self.genre_match_menu.insert(tk.END, title)
            self.lookup[title] = uri
        self.genre_match_menu.pack(fill = tk.BOTH, expand=True)
        self.add_to_playlist_button.pack()


    def display_artist_match(self, selected_artists):
        self.artist_confirm_button.forget()
        artist_match = get_song_with_artist(selected_artists)
        self.artist_match_menu.delete(0, tk.END)
        for index, [title, uri] in enumerate(artist_match):
            self.artist_match_menu.insert(tk.END, title)
            self.lookup[title] = uri
        self.artist_match_menu.pack(fill=tk.BOTH, expand=True)
        self.add_to_playlist_button.pack()


    def display_year_match(self, *args):
        year_value = self.value_in_year_menu.get()
        year_match = get_song_with_year(year_value)
        self.year_match_menu.delete(0, tk.END)
        for index, [title, uri] in enumerate(year_match):
            self.year_match_menu.insert(tk.END, title)
            self.lookup[title] = uri
        self.year_match_menu.pack(fill=tk.BOTH, expand=True)
        self.add_to_playlist_button.pack()



    def add_to_playlist(self):

        if self.value_inside_menu.get() == "By Genre":
            source = self.genre_match_menu
        elif self.value_inside_menu.get() == "By Artist":
            source = self.artist_match_menu
        else:
            source = self.year_match_menu

        selected = [source.get(i) for i in source.curselection()]
        for song in selected:
            if song not in self.playlist:
                self.playlist.append(song)
        print("Playlist: ", self.playlist)
        return self.playlist

    def view_playlist(self):
        self.pls_enter_name_label.forget()
        self.playlist_name_entry.forget()
        self.name_entry_label.forget()
        self.add_to_playlist_button.forget()
        self.artist_match_menu.forget()
        self.year_match_menu.forget()
        self.genre_match_menu.forget()
        self.artist_confirm_button.forget()
        self.genre_confirm_button.forget()
        self.genre_menu.forget()
        self.artist_menu.forget()
        self.year_menu.forget()
        self.view_playlist_menu.delete(0, tk.END)
        self.value_inside_name_entry.set("")
        for song in self.playlist:
            self.view_playlist_menu.insert(tk.END, song)
        self.view_playlist_menu.pack(expand=True, fill=tk.BOTH)
        self.name_entry_label.pack(side = tk.LEFT, padx = (0,8))
        self.playlist_name_entry.pack(side = tk.LEFT)
        self.create_playlist_button.pack(side = tk.RIGHT, padx = (0,8))
        self.remove_from_playlist_button.pack()
        self.clear_playlist_button.pack()


    def create_playlist(self):
        if not(self.value_inside_name_entry.get() == ""):
            self.pls_enter_name_label.forget()
            self.playlist_name_entry.forget()
            self.name_entry_label.forget()
            self.name_entry_label.pack(side=tk.LEFT, padx=(0, 8))
            self.playlist_name_entry.pack(side=tk.LEFT)
            insertion_list = []
            for song in self.playlist:
                insertion_list.append(self.lookup[song])
            add_playlist(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, self.value_inside_name_entry.get(), insertion_list)
        else:
            self.name_entry_label.forget()
            self.playlist_name_entry.forget()
            self.pls_enter_name_label.pack(side=tk.LEFT, padx=(0, 8))
            self.playlist_name_entry.pack(side=tk.LEFT)


    def remove_from_playlist(self):
        source = self.view_playlist_menu
        selected = [source.get(i) for i in source.curselection()]
        for song in selected:
            self.playlist.remove(song)
        print(self.playlist)

    def clear_playlist(self):
        self.playlist.clear()



    def menu(self):
        self.destroy()
        Menu(self.master)





class Music_View(tk.Frame):
    def __init__(self, parent, songs = songsUse):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.configure(bg="light blue")

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
        self.configure(bg="light blue")
        self.title_label = tk.Label(self, text="Recommend Music", font=("Helvetica", 24))
        self.menu_button = tk.Button(self, text="Menu", command=self.menu)
        self.left_frame = tk.Frame(self, bg ="light blue")
        self.left_frame.pack(side=tk.LEFT, anchor = "n", padx = 0, pady = 70)
        self.bottom_frame = tk.Frame(self, bg ="light blue")
        self.bottom_frame.pack(side=tk.BOTTOM, anchor="w", padx = 10, pady = 100)
        self.right_frame = tk.Frame(self, bg ="light blue")
        self.right_frame.pack(side=tk.RIGHT, anchor = "n", padx = 20, pady = 70)
        self.title_label.pack(pady=20)
        self.menu_button.pack()
        self.genre_title = tk.Label(self.left_frame, text="Top 10 Genres In Your Account: ", font=("Helvetica", 15, "bold"))
        self.genre_title.pack()
        self.artist_title = tk.Label(self.right_frame, text="Top 10 Artists In Your Account: ", font=("Helvetica", 15, "bold"))
        self.artist_title.pack()
        self.artist_match_title = tk.Label(self.bottom_frame, text = "Top 3 artists that match your music taste: ", font=("Helvetica", 15, "bold"))
        self.artist_match_title.pack()
        for genre in top_10_genres:
            self.top10_genre_label = tk.Label(self.left_frame, font = ("Helvetica", 15), text=f"{genre}: {round(genre_percentages[genre]*100,2)}%")
            self.top10_genre_label.pack()
        for artist in top_10_artists:
            self.top10_artist_label = tk.Label(self.right_frame, font = ("Helvetica", 15), text=f"{artist}: {round(artist_percentages[artist]*100,2)}%")
            self.top10_artist_label.pack()
        for artist in top5_artists:
            self.top5_artist_label = tk.Label(self.bottom_frame, font = ("Helvetica", 15), text=f"{artist} matches your music taste by: {round((math.asin(artist_cosine_match[artist])/(math.pi/2))*100,2)}%")
            self.top5_artist_label.pack()

    def menu(self):
        self.destroy()
        Menu(self.master)



root = tk.Tk()
root.title("VibeList")
root.geometry("1000x600")
root.minsize(800, 500)

Menu(root)


root.mainloop()