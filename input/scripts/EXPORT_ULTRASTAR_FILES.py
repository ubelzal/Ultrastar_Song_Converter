from textgrid import TextGrid
import os
import re
import shutil
import glob

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name.strip().replace(" ", "_")

def textgrid_to_ultrastar(id, textgrid_path, output_path, ARTIST, TITLE, YEAR, MP3, COVER, BPM, VOCALS, INSTRUMENTAL, GAP, LANGUAGE, MFA, cursor, conn):
    """
    Convertit un Long TextGrid MFA en fichier Ultrastar prêt à chanter.
    Chaque mot devient une note (-) avec début et fin en centièmes de seconde.
    """

    tg = TextGrid()
    tg.read(textgrid_path)

    safe_artist = sanitize_filename(ARTIST)
    safe_title = sanitize_filename(TITLE)

    base = "/app/UltraStar"
    target = os.path.join(base, safe_artist, safe_title)
    os.makedirs(target, exist_ok=True)

    # Copier médias
    for ext in ("*.mp3", "*.jpg"):
        for f in glob.glob(os.path.join(os.path.dirname(MP3), ext)):
            shutil.copy2(f, target)

    out = os.path.join(
        target,
        f"{safe_artist} - {safe_title}.txt"
    )

    # Exemple d'utilisation
    #textgrid_file = "output/song_Long.TextGrid"  # le TextGrid MFA
    #ultrastar_file = "output/song.txt"

    # Ultrastar attend généralement un fichier txt avec info de la chanson
    lines = []
    lines.append(f"#TITLE: {title}")
    lines.append(f"#ARTIST: {artist}")
    lines.append(f"#LANGUAGE: {LANGUAGE}")
    lines.append(f"#YEAR: {YEAR}")
    lines.append(f"#MP3: {safe_artist} - {safe_title}.mp3")
    lines.append(f"#COVER: {safe_artist} - {safe_title} [CO].jpg")  
    lines.append(f"#BACKGROUND: {safe_artist} - {safe_title} [BG].jpg")  
    lines.append(f"#EDITION: ")   
    lines.append(f"#GENRE: ") 
    lines.append("")

    # Supposons que le premier intervalle soit la couche des mots
    # MFA Long TextGrid a souvent une seule tier "words" ou "phone" par mot
    if len(tg.tiers) == 0:
        raise ValueError("TextGrid vide ou format incorrect")
    
    tier = tg.tiers[0]  # prend le premier tier
    for interval in tier.intervals:
        word = interval.mark.strip()
        if word == "":
            continue  # ignore les silences
        start_cs = int(interval.minTime * 100)  # Ultrastar utilise centièmes de seconde
        end_cs = int(interval.maxTime * 100)
        lines.append(f"- {start_cs} {end_cs} {word}")

    # Écriture du fichier Ultrastar
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Fichier Ultrastar créé : {output_path}")

    cursor.execute(
        "UPDATE song_list SET Export_Ultrastar='Y' WHERE id=?",
        (id,)
    )
    conn.commit()

    print("🪩 Export UltraStar terminé (version officielle-like)")
