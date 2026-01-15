import os
import shutil
import glob
import re

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


def main(id, YEAR, MP3: str, COVER: str, ARTIST: str, TITLE: str, BPM: str, VOCALS: str, INSTRUMENTAL: str, cursor: object, conn: object):

    safe_title = sanitize_filename(TITLE)
    safe_artist = sanitize_filename(ARTIST)

    UltraStar_base = "/app/UltraStar"

    target_dir = os.path.join(UltraStar_base, safe_artist, safe_title)
   
    # Créer le dossier si nécessaire
    os.makedirs(target_dir, exist_ok=True)

    # Dossier source du MP3
    source_dir = os.path.dirname(MP3)

    # Copier tous les .mp3 et .pg
    for ext in ("*.mp3", "*.pg"):
        for file in glob.glob(os.path.join(source_dir, ext)):
            shutil.copy2(file, target_dir)

    # Créer le fichier .txt
    txt_filename = f"{safe_artist} - {safe_title}.txt"
    txt_path = os.path.join(target_dir, txt_filename)

    txt_content = f"""#ID:{id}
#TITLE:{TITLE}
#ARTIST:{ARTIST}
#LANGUAGE:French
#EDITION:
#GENRE:
#YEAR:{YEAR}
#MP3:{safe_artist} - {safe_title}.mp3
#COVER:{safe_artist} - {safe_title} [CO].jpg
#BACKGROUND:{safe_artist} - {safe_title} [BG].jpg
#BPM:{BPM}
#BEAT:0
#GAP:0
#OFFSET:-200
F 0 0 0 
- 1
F 1 0 0 
E
"""
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    cursor.execute(
        "UPDATE song_list SET Export_Ultrastar = ? WHERE id = ?",
        ("N", id)
    )
    conn.commit()

    print(f"     🎨 Cover téléchargé !")


if __name__ == "__main__":
    main()