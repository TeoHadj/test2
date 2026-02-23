import spotipy
from spotipy.oauth2 import SpotifyOAuth


def add_playlist(client_id, secret, uri, pname, song_list:list):
    sp_oauth = SpotifyOAuth(client_id=client_id,
                         client_secret=secret,
                         redirect_uri=uri,
                         scope="playlist-modify-public playlist-modify-private")

    sp = spotipy.Spotify(auth_manager=sp_oauth)

    user_id = sp.current_user()["id"]

    playlist = sp.user_playlist_create(user = user_id, name = pname, public = True, description = "Created by VibeList")
    playlist_id = playlist["id"]
    sp.playlist_add_items(playlist_id, song_list)

# add_playlist('04df9df5cd8e400483dc0cfbce4dcd66',
#              '202662453275474f801833a07e418586',
#              'http://127.0.0.1:8000/callback',
#              "Test",
#              ["spotify:track:4cOdK2wGLETKBW3PvgPWqT","spotify:track:7GhIk7Il098yCjg4BQjzvb","spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"])
