import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY environment variable is not set')

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

BASE_URL = os.environ.get('BASE_URL', 'https://playchoon.vercel.app')
REDIRECT_URI = f"{BASE_URL}/callback"

CORS_ORIGINS = [
    'https://playchoon.vercel.app',
    'http://localhost:8888',
    'http://localhost:5000',
]

SONGS_MAP = {
    'First': 10,
    'Second': 20,
    'Third': 30,
}

MAX_ARTISTS = 10
MAX_ARTIST_NAME_LENGTH = 100
