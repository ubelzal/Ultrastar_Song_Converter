from scripts import MFA_CONVERT
import os
import sqlite3
import subprocess
import time
import re
import unicodedata

DATABASE_LOCATION="/data/input/database/database.db"
pwd = os.getcwd()

# Clear terminal (optionnel)
os.system("clear" if os.name == "posix" else "cls")

def clean_lyrics_text(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():

        # 🔥 Supprimer toute ligne contenant [
        if "[" in line:
            continue

        # Normalisation unicode
        line = unicodedata.normalize("NFKC", line)

        # Minuscules
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

            # MFA_CONVERT
            if MFA: # is None and WAV and LANGUAGE:
                MFA_CONVERT.main (id,WAV,MFA,LANGUAGE,cursor,conn)
                time.sleep(0.15)

        except Exception as e:

            print(f"     ❌ Erreur d'importation sur {row[1]} (id={row[0]}): {e}\n→!")
            continue
        
    conn.close()
    print()
    print("🎉 Extraction MFA terminée.")


if __name__ == "__main__":
    main()