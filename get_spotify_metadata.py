import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import sys

# Configuration - Remplacez par vos vraies valeurs
SPOTIFY_CLIENT_ID = "votre_client_id"
SPOTIFY_CLIENT_SECRET = "votre_client_secret"

def get_track_metadata(query):
    """
    Recherche une chanson sur Spotify et récupère ses métadonnées
    
    Args:
        query: Nom de la chanson (ex: "Bohemian Rhapsody Queen")
    
    Returns:
        dict: Métadonnées complètes de la chanson
    """
    # Authentification
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Recherche de la chanson
    results = sp.search(q=query, type='track', limit=1)
    
    if not results['tracks']['items']:
        print(f"❌ Aucune chanson trouvée pour: {query}")
        return None
    
    track = results['tracks']['items'][0]
    track_id = track['id']
    
    # Récupérer les audio features (tempo, clé, etc.)
    audio_features = sp.audio_features(track_id)[0]
    
    # Construire les métadonnées complètes
    metadata = {
        'titre': track['name'],
        'artistes': [artist['name'] for artist in track['artists']],
        'album': track['album']['name'],
        'date_sortie': track['album']['release_date'],
        'duree_ms': track['duration_ms'],
        'duree_sec': track['duration_ms'] / 1000,
        'popularite': track['popularity'],
        'isrc': track.get('external_ids', {}).get('isrc'),
        'spotify_url': track['external_urls']['spotify'],
        'preview_url': track['preview_url'],
        'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
        
        # Audio features
        'tempo_bpm': audio_features['tempo'] if audio_features else None,
        'key': audio_features['key'] if audio_features else None,
        'mode': 'majeur' if audio_features and audio_features['mode'] == 1 else 'mineur',
        'energie': audio_features['energy'] if audio_features else None,
        'dansabilite': audio_features['danceability'] if audio_features else None,
        'acoustique': audio_features['acousticness'] if audio_features else None,
    }
    
    return metadata


def display_metadata(metadata):
    """Affiche les métadonnées de façon lisible"""
    if not metadata:
        return
    
    print("\n" + "="*60)
    print("🎵 MÉTADONNÉES SPOTIFY")
    print("="*60)
    print(f"Titre        : {metadata['titre']}")
    print(f"Artiste(s)   : {', '.join(metadata['artistes'])}")
    print(f"Album        : {metadata['album']}")
    print(f"Date         : {metadata['date_sortie']}")
    print(f"Durée        : {metadata['duree_sec']:.0f}s ({metadata['duree_ms']}ms)")
    print(f"Popularité   : {metadata['popularite']}/100")
    print(f"ISRC         : {metadata['isrc']}")
    print(f"Tempo        : {metadata['tempo_bpm']:.1f} BPM")
    print(f"Tonalité     : {metadata['key']} ({metadata['mode']})")
    print(f"Spotify URL  : {metadata['spotify_url']}")
    print(f"Cover URL    : {metadata['cover_url']}")
    print("="*60 + "\n")


def save_metadata_json(metadata, filename='metadata.json'):
    """Sauvegarde les métadonnées en JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✅ Métadonnées sauvegardées dans {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_spotify_metadata.py 'nom de la chanson'")
        print("Exemple: python get_spotify_metadata.py 'Bohemian Rhapsody Queen'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"🔍 Recherche: {query}")
    
    metadata = get_track_metadata(query)
    
    if metadata:
        display_metadata(metadata)
        save_metadata_json(metadata)