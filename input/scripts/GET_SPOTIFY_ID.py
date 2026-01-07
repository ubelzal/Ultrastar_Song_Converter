import sys
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Charger le fichier .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Vérification rapide
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Les clés Spotify ne sont pas définies dans .env")

def get_track_id(title, artist):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))
    
    query = f"track:{title} artist:{artist}"
    result = sp.search(q=query, type="track", limit=1)

    if result["tracks"]["items"]:
        track = result["tracks"]["items"][0]
        return track["id"]
    return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python spotify_id_spotipy.py 'TITLE' 'ARTIST'")
        return

    title = sys.argv[1]
    artist = sys.argv[2]

    track_id = get_track_id(title, artist)
    if track_id:
        print(f"ID Spotify pour '{title}' de '{artist}' : {track_id}")
    else:
        print("❌ ID introuvable")

if __name__ == "__main__":
    main()
