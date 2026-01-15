import re
import unicodedata
import os
import subprocess

def main(id, WAV: str, MFA: str, LANGUAGE: str, cursor: object, conn: object):

    audio_path = WAV

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
    wav_file = os.path.join(output_dir, f"{base_name}.wav")
    lyrics_file = os.path.join(output_dir, f"{base_name}.txt")
    TextGrid_file = os.path.join(output_dir, f"{base_name}-vocals.TextGrid")

    # DOSSIER corpus (wav + txt dedans)
    corpus_dir = os.path.dirname(audio_path)

    subprocess.run(
    [
        "mfa",
        "align",
        corpus_dir,          # ✅ dossier, pas fichier
        "french_mfa",        # dictionnaire
        "french_mfa",        # modèle acoustique
        output_dir,
        "--clean",
        "--overwrite",
        "--beam", "100",
        "--retry_beam", "400",
        "--output_format", "long_textgrid",
        "--include_original_text" # ligne par ligne
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=True
    )

    if not MFA:
        cursor.execute(
            "UPDATE song_list SET MFA = ? WHERE id = ?",
            (TextGrid_file, id)
        )
        conn.commit()

    print(f"     📝 Fichier TextGrids créer !")



if __name__ == "__main__":
    main()