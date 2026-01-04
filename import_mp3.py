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

    cursor.execute("SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,'Update' FROM song_list WHERE id >= 1 ORDER BY id")
    rows = cursor.fetchall()
	
    for row in rows:

        try:
            id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,Update = row

            safe_name = sanitize_filename(TITLE or f"song_{id}")

            # 1) mp3_data -> Nom.mp3
            if YoutubeID:
                print(safe_name)
       
            time.sleep(1)

        except Exception as e:
                print(f"❌ Erreur sur {row[1]} (id={row[0]}): {e}\n→ on continue !")
                continue
        
    conn.close()
    print("🎉 Extraction terminée.")


def main():

    read_from_db("/home/belala/git/Ultrastar_Song_Converter/input/database/database.db")

if __name__ == "__main__":
    main()
