from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from flask import session

app = Flask(__name__)
app.secret_key = 'your secret key'  # Replace this with your own secret key
CORS(app, resources={r"/*": {"origins": "https://ts-playchoon.vercel.app"}})

load_dotenv()
sp_oauth = SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                        client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
                        redirect_uri="http://localhost:8888/callback",
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

    spotify_username = user_info['id']

    songs_per_artist = total_songs // len(artist_names)
    track_ids = []

    for artist in artist_names:
        results = sp.search(q='artist:' + artist, type='track', limit=songs_per_artist)
        track_ids += [track['id'] for track in results['tracks']['items']]

    playlist = sp.user_playlist_create(user=spotify_username, name="PlayChoon Playlist")
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)

    return jsonify({'status': 'success', 'playlist_id': playlist['id']})

if __name__ == '__main__':
    app.run(debug=True)