import re
import unicodedata
import os

# clean_lyrics("lyrics.txt", "lyrics_clean.txt")

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


def main(id, LYRICS: str, MP3: str, cursor: object, conn: object):

    audio_path = MP3

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
    lyrics_file = os.path.join(output_dir, f"{base_name}-vocals.txt")

    #print(lyrics_file)
    cleaned_lyrics = clean_lyrics_text(LYRICS)

    with open(lyrics_file, "w", encoding="utf-8") as f:
        f.write(cleaned_lyrics)
        print(f"     📝 Lyrics exporté !")

if __name__ == "__main__":
    main()