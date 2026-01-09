from scripts import IMPORT_MP3
import os
import sqlite3
import subprocess
import time
import re

DATABASE_LOCATION="/app/input/database/database.db"
pwd = os.getcwd()

# Clear terminal (optionnel)
os.system("clear" if os.name == "posix" else "cls")

def sanitize_filename(name: str) -> str:
    """
    Nettoie le nom pour être sûr qu'il puisse être utilisé comme nom de fichier.
    Conserve les lettres accentuées et remplace les espaces par "_".
    """
    # remplacer les caractères invalides par "_"
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # remplacer les espaces par "_"
    name = name.replace(" ", "_")
    return name

def main():

    conn = sqlite3.connect(DATABASE_LOCATION)
    cursor = conn.cursor()

    cursor.execute("SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,'Update' FROM song_list WHERE id >= 1 ORDER BY id")
    rows = cursor.fetchall()
	
    for row in rows:

        try:
            id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,Update = row

            safe_name = sanitize_filename(TITLE or f"song_{id}")
            safe_title = sanitize_filename(TITLE or f"song_{id}")
            safe_artist = sanitize_filename(ARTIST)

            print()
            print(id, "-", safe_artist, ":",safe_title)

            #import subprocess Download MP3
            if YoutubeID and safe_artist and safe_title:
                song_dir = os.path.join("/app/output", safe_artist, safe_title)
                os.makedirs(song_dir, exist_ok=True)

                mp3_path = os.path.join(song_dir, f"{safe_title}.mp3")

                if not os.path.exists(mp3_path):

                    youtube_url = f"https://www.youtube.com/watch?v={YoutubeID}"
                    output_template = os.path.join(song_dir, f"{safe_title}.%(ext)s")                    

            time.sleep(0.15)

        except Exception as e:
                print(f"❌ Erreur sur {row[1]} (id={row[0]}): {e}\n→ on continue !")
                continue
        
    conn.close()
    print("🎉 Extraction terminée.")

if __name__ == "__main__":
    main()