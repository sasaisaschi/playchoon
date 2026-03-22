import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# --- Config ---
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
BASE_URL = os.environ.get('BASE_URL', 'https://playchoon.vercel.app')
REDIRECT_URI = f"{BASE_URL}/callback"

CORS_ORIGINS = [
    'https://playchoon.vercel.app',
    'http://localhost:8888',
    'http://localhost:5000',
]

SONGS_MAP = {'First': 10, 'Second': 20, 'Third': 30}
MAX_ARTISTS = 10
MAX_ARTIST_NAME_LENGTH = 100

# --- App ---
app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, resources={r'/*': {'origins': CORS_ORIGINS}})

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='playlist-modify-public',
)


# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_auth_url')
def get_auth_url():
    if session.get('token_info'):
        return redirect('/')
    return jsonify({'auth_url': sp_oauth.get_authorize_url()})


@app.route('/callback')
def callback():
    code = request.args.get('code')
    session['token_info'] = sp_oauth.get_access_token(code)
    return redirect('/')


@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    token_info = session.get('token_info')
    if not token_info:
        return jsonify({'auth_url': sp_oauth.get_authorize_url()})

    data = request.get_json(silent=True) or {}
    artist_names = data.get('artist_names', [])
    total_songs_value = data.get('total_songs', 'First')

    artist_names = [a.strip() for a in artist_names if a.strip()]

    if not artist_names:
        return jsonify({'status': 'error', 'message': 'Bitte mindestens einen Künstler eingeben.'})
    if len(artist_names) > MAX_ARTISTS:
        return jsonify({'status': 'error', 'message': f'Maximal {MAX_ARTISTS} Künstler erlaubt.'})
    if any(len(a) > MAX_ARTIST_NAME_LENGTH for a in artist_names):
        return jsonify({'status': 'error', 'message': 'Ein Künstlername ist zu lang (max. 100 Zeichen).'})

    total_songs = SONGS_MAP.get(total_songs_value, 10)
    songs_per_artist = max(1, total_songs // len(artist_names))

    try:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_info = sp.current_user()
    except spotipy.SpotifyException:
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
            sp = spotipy.Spotify(auth=token_info['access_token'])
            user_info = sp.current_user()
        except Exception:
            session.pop('token_info', None)
            return jsonify({'auth_url': sp_oauth.get_authorize_url()})

    try:
        track_ids = []
        for artist in artist_names:
            results = sp.search(q='artist:' + artist, type='track', limit=songs_per_artist)
            track_ids += [track['id'] for track in results['tracks']['items']]

        if not track_ids:
            return jsonify({'status': 'error', 'message': 'Keine Tracks für die angegebenen Künstler gefunden.'})

        playlist = sp.user_playlist_create(user=user_info['id'], name='PlayChoon Playlist')
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Fehler bei der Spotify-Anfrage. Bitte versuche es erneut.'})

    return jsonify({'status': 'success', 'playlist_id': playlist['id']})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=8888, debug=debug)
