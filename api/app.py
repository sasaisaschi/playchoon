from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

app = Flask(__name__)
# Use a secret key from environment or generate a random one
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
CORS(app, resources={r"/*": {"origins": "https://playchoon.vercel.app"}})

# Get the base URL from environment or use a default
base_url = os.environ.get('BASE_URL', 'https://playchoon.vercel.app')
redirect_uri = f"{base_url}/callback"

sp_oauth = SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                        client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
                        redirect_uri=redirect_uri,
                        scope="playlist-modify-public")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_auth_url')
def get_auth_url():
    token_info = session.get('token_info', None)
    if token_info:
        # Der Benutzer ist bereits authentifiziert, leiten Sie ihn zur Hauptseite um
        return redirect('/')
    else:
        # Der Benutzer ist nicht authentifiziert, leiten Sie ihn zur Spotify-Authentifizierungs-URL um
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({'auth_url': auth_url})

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info  # Speichern Sie das token_info in der Sitzung
    return redirect('/')  # Leiten Sie den Benutzer zur Hauptseite Ihrer Anwendung um

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    token_info = session.get('token_info', None)
    if not token_info:
        # Der Benutzer ist nicht authentifiziert, geben Sie die Spotify-Authentifizierungs-URL zurück
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({'auth_url': auth_url})

    try:
        sp = spotipy.Spotify(auth=token_info['access_token'])  # Erstellen Sie einen authentifizierten Spotify-Client
        user_info = sp.current_user()
    except spotipy.SpotifyException:
        # Das Zugriffstoken ist abgelaufen, verwenden Sie das Aktualisierungstoken, um ein neues zu erhalten
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info  # Speichern Sie das neue token_info in der Sitzung
        sp = spotipy.Spotify(auth=token_info['access_token'])  # Erstellen Sie einen neuen authentifizierten Spotify-Client
        user_info = sp.current_user()

    # Get data from request
    data = request.get_json()
    artist_names = data.get('artist_names', [])
    total_songs_value = data.get('total_songs', 'First')  # Default to 'First' if not provided

    # Map the dropdown values to actual numbers
    total_songs_map = {
        'First': 10,
        'Second': 20,
        'Third': 30
    }
    total_songs = total_songs_map.get(total_songs_value, 10)  # Default to 10 if value not in map

    spotify_username = user_info['id']

    # Check if artist_names is not empty
    if not artist_names:
        return jsonify({'status': 'error', 'message': 'No artists provided'})

    songs_per_artist = total_songs // len(artist_names)
    if songs_per_artist < 1:
        songs_per_artist = 1  # Ensure at least one song per artist

    track_ids = []

    for artist in artist_names:
        if artist.strip():  # Skip empty artist names
            results = sp.search(q='artist:' + artist.strip(), type='track', limit=songs_per_artist)
            track_ids += [track['id'] for track in results['tracks']['items']]

    if not track_ids:
        return jsonify({'status': 'error', 'message': 'No tracks found for the provided artists'})

    playlist = sp.user_playlist_create(user=spotify_username, name="PlayChoon Playlist")
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)

    return jsonify({'status': 'success', 'playlist_id': playlist['id']})

if __name__ == '__main__':
    app.run(debug=True)
