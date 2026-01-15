import re
import unicodedata
import os
import subprocess
import requests

def main(id, MP3: str, ARTIST: str, TITLE: str, cursor: object, conn: object):

    audio_path = MP3

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
   
    cover_file = os.path.join(
            output_dir,
            f"{ARTIST} - {TITLE} [CO].jpg"
        )

    download_itunes_cover(
            artist=ARTIST,
            title=TITLE,
            output_path=cover_file,
            size=1000
    )

    cursor.execute(
        "UPDATE song_list SET COVER = ? WHERE id = ?",
        (cover_file, id)
    )
    conn.commit()

    print(f"     🎨 Cover téléchargé !")


def download_itunes_cover(artist, title, output_path="cover.jpg", size=600):
    """
    Télécharge un cover d'album depuis l'iTunes Search API
    size: 100, 300, 600, 1000 (selon disponibilité)
    """

    query = f"{artist} {title}"
    url = "https://itunes.apple.com/search"

    params = {
        "term": query,
        "media": "music",
        "entity": "song",
        "limit": 1
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if data["resultCount"] == 0:
        print("❌ Aucun résultat trouvé")
        return False

    artwork_url = data["results"][0].get("artworkUrl100")

    if not artwork_url:
        print("❌ Aucun cover disponible")
        return False

    # Remplacer la taille pour une meilleure résolution
    artwork_url = artwork_url.replace("100x100bb", f"{size}x{size}bb")

    img = requests.get(artwork_url)
    img.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(img.content)

    # print(f"     🎨 Cover téléchargé : {output_path}")
    return True


if __name__ == "__main__":
    main()