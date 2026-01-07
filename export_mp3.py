import os
import subprocess
import sys
import sqlite3
import re
import base64
import shutil
import stat
import time
from pathlib import Path

# Clear terminal (optionnel)
os.system("clear" if os.name == "posix" else "cls")

pwd = os.getcwd()

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

def read_from_db(db_path: str):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,'Update' FROM song_list WHERE id >= 1 ORDER BY id")
    rows = cursor.fetchall()
	
    for row in rows:

        try:
            id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,Update = row

            safe_name = sanitize_filename(TITLE or f"song_{id}")
            safe_title = sanitize_filename(TITLE or f"song_{id}")
            safe_artist = sanitize_filename(ARTIST)

            # Download MP3
            if YoutubeID and safe_artist and safe_title:
                song_dir = os.path.join("output", safe_artist, safe_title)
                os.makedirs(song_dir, exist_ok=True)

                mp3_path = os.path.join(song_dir, f"{safe_title}.mp3")

                print(id, " - ", safe_artist, " : ",safe_title)

                if not os.path.exists(mp3_path):

                    youtube_url = f"https://www.youtube.com/watch?v={YoutubeID}"
                    output_template = os.path.join(song_dir, f"{safe_title}.%(ext)s")

                    subprocess.run([
                        "docker", "compose", "run", "--rm", "karaoke", "yt-dlp",
                        "-x",
                        "--audio-format", "mp3",
                        "--audio-quality", "0",
                        youtube_url,
                        "-o", output_template
                    ], check=True)
                    

                if os.path.exists(mp3_path):
                    relative_mp3_path = os.path.relpath(mp3_path)

                    if not MP3:
                        cursor.execute(
                            "UPDATE song_list SET MP3 = ? WHERE id = ?",
                            (relative_mp3_path, id)
                        )
                        conn.commit()

            #  

            time.sleep(0.25)

        except Exception as e:
                print(f"❌ Erreur sur {row[1]} (id={row[0]}): {e}\n→ on continue !")
                continue
        
    conn.close()
    print("🎉 Extraction terminée.")


def main():

    read_from_db("/home/belala/git/Ultrastar_Song_Converter/input/database/database.db")

if __name__ == "__main__":
    main()
