import requests
from ShazamAPI import Shazam
    
# def main(id, MP3: str, cursor: object, conn: object):

LASTFM_API_KEY = "f0932cc1077866388abf874dac1a697b"

IGNORE_TAGS = {
    "quebecois", "canadian", "francophone", "french", "english",
    "male vocalists", "female vocalists", "seen live", "favorites"
}

def normalize_artist(name):
    various = [
        "Разные артисты",
        "Various Artists",
        "Artistes divers",
        "Verschiedene Künstler",
        "Varios artistas"
    ]
    if name.strip() in various:
        return "Various Artists"
    return name

def get_lastfm_tags(artist, title):
    url = "https://ws.audioscrobbler.com/2.0/"
    
    # 1) essayer la piste
    params = {
        "method": "track.getTopTags",
        "artist": artist,
        "track": title,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    r = requests.get(url, params=params).json()
    tags = r.get("toptags", {}).get("tag", [])

    # 2) si vide → artiste
    if not tags:
        params = {
            "method": "artist.getTopTags",
            "artist": artist,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }
        r = requests.get(url, params=params).json()
        tags = r.get("toptags", {}).get("tag", [])

    return tags

def pick_genre(tags):
    for tag in tags:
        name = tag["name"].lower()
        if name not in IGNORE_TAGS:
            return tag["name"].title()
    return "Unknown"

def identify_mp3(mp3_path):
    mp3 = open(mp3_path, "rb").read()
    shazam = Shazam(mp3)

    chanson = next(shazam.recognizeSong())
    track = chanson[1]["track"]

    title = track["title"]
    artist = normalize_artist(track["subtitle"])

    return title, artist

# =============================

def main(id, MP3, ARTIST, TITLE, cursor, conn):
    
    import sys

    # if len(sys.argv) != 2:
    #     print("Usage: python genre_from_mp3.py fichier.mp3")
    #     exit(1)

    # mp3 = sys.argv[1]

    title, artist = identify_mp3(MP3)
    print("🎵", title)
    print("🎤", artist)

    tags = get_lastfm_tags(ARTIST, TITLE)
    genre = pick_genre(tags)

    print("🎧 GENRE:", genre)


  #tags_json = json.dumps(genres, ensure_ascii=False)


  # cursor.execute(
  #     "UPDATE song_list SET TAGS = ? WHERE id = ?",
  #     (tags_json, id)
  # )
  # conn.commit()

    print(f"     𓂀  Shazam executé !")
