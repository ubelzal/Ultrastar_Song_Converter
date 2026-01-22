from scripts import IMPORT_MP3
from scripts import DEMUCS
from scripts import IMPORT_LYRICS
from scripts import CONVERT_WAV
from scripts import IMPORT_COVER
from scripts import EXPORT_ULTRASTAR_FILES
#from scripts import IMPORT_GAP
#from scripts import IMPORT_TAGS
from scripts import IMPORT_SHAZAM
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
    # remplacer les COVERespaces par "_"
    name = name.replace(" ", "_")
    return name

def refresh_song(id, cursor):
    cursor.execute("""
        SELECT
            MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA
        FROM song_list
        WHERE id = ?
    """, (id,))
    return cursor.fetchone()

def main():

    conn = sqlite3.connect(DATABASE_LOCATION)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,VERSION,YoutubeID,SpotifyID,ARTIST,TITLE,ALBUM,LYRICS,
               BPM,COVER,BACKGROUND,VOCALS,INSTRUMENTAL,GENRE,TAGS,
               LANGUAGE,YEAR,MP3,'Update',Re_Import,WAV,MFA,Export_Ultrastar,GAP,Speaker   
        FROM song_list
        WHERE id >= 1  
        ORDER BY id
    """)
    
    rows = cursor.fetchall()

    for row in rows:
        try:
            (
                id, VERSION, YoutubeID, SpotifyID, ARTIST, TITLE, ALBUM, LYRICS,
                BPM, COVER, BACKGROUND, VOCALS, INSTRUMENTAL, GENRE, TAGS,
                LANGUAGE, YEAR, MP3, Update, Re_Import, WAV, MFA, Export_Ultrastar,GAP,Speaker  
            ) = row

            print(f"\n{id} - {ARTIST} : {TITLE}")

            # 🔄 RESET FIELDS
            if Re_Import and Re_Import.strip() == "Y":
                IMPORT_MP3.Reset_Fields(id, TITLE, ARTIST, Re_Import, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
                print("     ✅ Reset effectué")


            # 🎵 IMPORT MP3
            if YoutubeID and ARTIST and TITLE and MP3 is None:
                IMPORT_MP3.load_MP3(id, YoutubeID, TITLE, ARTIST, MP3, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            else:
                print("     🎵 MP3 déjà importé")


            # # 𓂀 SHAZAM
            # if MP3:
            #     IMPORT_SHAZAM.main(id, MP3, ARTIST, TITLE, cursor, conn)
            #     conn.commit()
            #     MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            # else:
            #     print("     𓂀 Shazam déjà effectué")


            # 💓 BPM
            if MP3 and BPM is None:
                IMPORT_MP3.Import_BPM(id, MP3, BPM, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            else:
                print("     💓 BPM déjà importé")


            # 🎤 DEMUCS
            if MP3 and VOCALS is None and INSTRUMENTAL is None:
                DEMUCS.Separation(id, MP3, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            else:
                print("     🎤 DEMUCS déjà importé")


            # 📝 LYRICS
            if LYRICS:
                IMPORT_LYRICS.main(id, LYRICS, MP3, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)


            # 🔊 WAV
            if VOCALS and WAV is None:
                CONVERT_WAV.main(id, WAV, VOCALS, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            else:
                print("     🔊 WAV déjà importé")


            # 🎨 COVER
            if MP3 and COVER is None:
                IMPORT_COVER.main(id, MP3, ARTIST, TITLE, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            else:
                print("     🎨 COVER déjà importé")


            # # 🏷️ TAGS
            # if TAGS is None or TAGS == "[]":
            #     IMPORT_TAGS.main(id, ARTIST, TITLE, TAGS, cursor, conn)
            #     conn.commit()
            #     MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            # else:
            #     print("     🏷️ Tags déjà importé")


            # # 🪩 IMPORT GAP
            # if WAV and GAP is None:
            #     IMPORT_GAP.main(id, WAV, cursor, conn)
            #     conn.commit()
            #     MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
            # else:
            #     print("     ∅  GAP déjà importé")

            # 🎶 EXPORT ULTRASTAR
            if Export_Ultrastar == "Y" and MP3 and COVER and ARTIST and TITLE and BPM and VOCALS and INSTRUMENTAL:
                EXPORT_ULTRASTAR_FILES.main(id, ARTIST, TITLE, YEAR, MP3, COVER, BPM, VOCALS, INSTRUMENTAL, GAP, LANGUAGE, MFA, GENRE, cursor, conn)
                conn.commit()
                MP3, BPM, VOCALS, INSTRUMENTAL, WAV, MFA = refresh_song(id, cursor)
   
            #time.sleep(1)

        except Exception as e:
            print(f"     ❌ Erreur d'importation sur {VERSION} (id={id}): {e}\n→!")
            continue

    conn.close()
    print("\n🎉 Extraction terminée.")

if __name__ == "__main__":
    main()