from scripts import IMPORT_MP3
from scripts import DEMUCS
from scripts import IMPORT_LYRICS
from scripts import CONVERT_WAV
import os
import sqlite3
import subprocess
import time
import re
import unicodedata

DATABASE_LOCATION="/app/input/database/database.db"
pwd = os.getcwd()

# Clear terminal (optionnel)
os.system("clear" if os.name == "posix" else "cls")

def clean_lyrics_text(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():VOCALS

        # 🔥 Supprimer toute ligne contenant [
    if "[" in line: 

        # Normalisation unicode
        line = unicodedata.normalize("NFKC", line)

        # Minusculesfrom scripts import CONVERT_WAV
        line = line.lower()

        # Remplacer apostrophes par espace
        line = re.sub(r"[’']", " ", line)

        # Supprimer ponctuation (garder lettres + accents)
        line = re.sub(r"[^a-zàâäçéèêëîïôöùûüÿñæœ\s]", " ", line)

        # Supprimer chiffres
        line = re.sub(r"\d+", " ", line)

        # Espaces multiples
        line = re.sub(r"\s+", " ", line)

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

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

    cursor.execute("SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,'Update',Re_Import, WAV, MFA FROM song_list WHERE id >= 1 ORDER BY id")
    rows = cursor.fetchall()
	
    for row in rows:

        try:
            id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,LANGUAGE,YEAR,MP3,Update,Re_Import, WAV,MFA = row

            print("")
            print(id, "-", ARTIST, ":",TITLE)
            
            # RE_IMPORT
            if Re_Import and Re_Import.strip() == "Y":
                IMPORT_MP3.Reset_MP3(id,cursor,conn,TITLE, ARTIST)
                print(f"     ✅ Reseter! ") 


            # IMPORT MP3
            if (YoutubeID and ARTIST and TITLE) and not MP3:
                IMPORT_MP3.load_MP3(id,YoutubeID,TITLE,ARTIST,MP3,cursor,conn)
                time.sleep(0.15)
            else:
                print(f"     💿 MP3 Déjà importé !")  


            # FIND BPM
            if MP3 and BPM is None:
                #print(f"🔍 Type de id: {type(id)} | Valeur: {id}")  
                #print(f"🔍 Type de BPM: {type(BPM)} | Valeur: {BPM}")  
                IMPORT_MP3.Import_BPM(id,MP3,BPM,cursor,conn)
                time.sleep(0.15)
            else:
                print(f"     🎧 BPM Déjà importé !")  


            # Demucs
            if VOCALS is None and INSTRUMENTAL is None:
                DEMUCS.Separation (id,MP3,cursor,conn)
                time.sleep(0.15)
            else:
                print(f"     🎤 DEMUCS Déjà importé !") 


            # Lyrics
            if LYRICS:
                IMPORT_LYRICS.main (id,LYRICS,MP3,cursor,conn)
                time.sleep(0.15)


            # CONVERT_WAV
            if WAV is None and VOCALS:
                CONVERT_WAV.main (id,WAV,VOCALS,cursor,conn)
                time.sleep(0.15)


        except Exception as e:
                print(f"     ❌ Erreur d'importation sur {row[1]} (id={row[0]}): {e}\n→!")
                continue
        
    conn.close()
    print()
    print("🎉 Extraction terminée.")

if __name__ == "__main__":
    main()