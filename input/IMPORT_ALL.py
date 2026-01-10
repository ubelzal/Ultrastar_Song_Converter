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

    cursor.execute("SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,'Update',Re_Import FROM song_list WHERE id >= 1 ORDER BY id")
    rows = cursor.fetchall()
	
    for row in rows:

        try:
            id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,Update,Re_Import = row

            print()
            print(id, "-", ARTIST, ":",TITLE)
            
            # RE_IMPORT
            if Re_Import and Re_Import.strip() == "Y":
                IMPORT_MP3.Reset_Record(id,cursor,conn)
                print(f"     ✅ Reseter! ") 


            # IMPORT MP3
            if YoutubeID and ARTIST and TITLE:
                
                IMPORT_MP3.load_MP3(id,YoutubeID,TITLE,ARTIST,MP3,cursor,conn)

            else:
                print(f"     ✅ MP3 Déjà importé !")  

            time.sleep(0.25)




        except Exception as e:
                print(f"     ❌ Erreur d'importation sur {row[1]} (id={row[0]}): {e}\n→!")
                continue
        
    conn.close()
    print("🎉 Extraction terminée.")

if __name__ == "__main__":
    main()