import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI


def get_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='playlist-modify-public',
    )


def get_spotify_client(token_info):
    return spotipy.Spotify(auth=token_info['access_token'])


def refresh_token_if_needed(sp_oauth, token_info):
    try:
        sp = get_spotify_client(token_info)
        user_info = sp.current_user()
        return sp, user_info, token_info
    except spotipy.SpotifyException:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        sp = get_spotify_client(token_info)
        user_info = sp.current_user()
        return sp, user_info, token_info


def build_playlist(sp, spotify_username, artist_names, songs_per_artist):
    track_ids = []
    for artist in artist_names:
        artist = artist.strip()
        if not artist:
            continue
        results = sp.search(q='artist:' + artist, type='track', limit=songs_per_artist)
        track_ids += [track['id'] for track in results['tracks']['items']]

    if not track_ids:
        return None, None

    playlist = sp.user_playlist_create(user=spotify_username, name='PlayChoon Playlist')
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)
    return playlist['id'], track_ids
