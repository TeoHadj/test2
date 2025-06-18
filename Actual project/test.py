import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# Now you can interact with Spotify API (example: get the user's playlists)
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

#query the songs by genre
for track in all_tracks:
    track_info = sp.track(track['id'])
    artist_id = track_info['artists'][0]['id']
    artist = sp.artist(artist_id)
    genres = artist['genres']
    print(f"Artist: {artist['name']}, track name: {track_info['name']}, genres: {genres}")