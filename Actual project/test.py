import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

from urllib.request import urlopen

# Set your credentials here
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

# get the user's playlists)
# playlists = sp.current_user_playlists()
# for playlist in playlists['items']:
#     print(f"Playlist name: {playlist['name'],playlist['name']}")

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

song_genres = []

for item in all_tracks:
    track = item['track']
    artist_id = track['artists'][0]['id']
    artist_info = sp.artist(artist_id)
    artist_genres = artist_info.get('genres', [])
    song_genres.append(artist_genres)

print(song_genres)
