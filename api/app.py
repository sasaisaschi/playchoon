import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS

from config import SECRET_KEY, CORS_ORIGINS, SONGS_MAP, MAX_ARTISTS, MAX_ARTIST_NAME_LENGTH
from spotify_service import get_oauth, refresh_token_if_needed, build_playlist

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, resources={r'/*': {'origins': CORS_ORIGINS}})

sp_oauth = get_oauth()


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

    # Input-Validierung
    if not artist_names:
        return jsonify({'status': 'error', 'message': 'Bitte mindestens einen Künstler eingeben.'})

    artist_names = [a for a in artist_names if a.strip()]
    if not artist_names:
        return jsonify({'status': 'error', 'message': 'Kein gültiger Künstlername gefunden.'})

    if len(artist_names) > MAX_ARTISTS:
        return jsonify({'status': 'error', 'message': f'Maximal {MAX_ARTISTS} Künstler erlaubt.'})

    if any(len(a) > MAX_ARTIST_NAME_LENGTH for a in artist_names):
        return jsonify({'status': 'error', 'message': 'Ein Künstlername ist zu lang (max. 100 Zeichen).'})

    total_songs = SONGS_MAP.get(total_songs_value, 10)
    songs_per_artist = max(1, total_songs // len(artist_names))

    try:
        sp, user_info, token_info = refresh_token_if_needed(sp_oauth, token_info)
        session['token_info'] = token_info
    except Exception:
        session.pop('token_info', None)
        return jsonify({'auth_url': sp_oauth.get_authorize_url()})

    try:
        playlist_id, track_ids = build_playlist(sp, user_info['id'], artist_names, songs_per_artist)
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Fehler bei der Spotify-Anfrage. Bitte versuche es erneut.'})

    if not playlist_id:
        return jsonify({'status': 'error', 'message': 'Keine Tracks für die angegebenen Künstler gefunden.'})

    return jsonify({'status': 'success', 'playlist_id': playlist_id})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=8888, debug=debug)
