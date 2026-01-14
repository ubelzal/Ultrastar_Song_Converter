import re
import unicodedata
import os
import subprocess

def main(id, WAV: str, MFA: str, cursor: object, conn: object):

    audio_path = WAV

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
    wav_file = os.path.join(output_dir, f"{base_name}.wav")
    lyrics_file = os.path.join(output_dir, f"{base_name}.txt")

    subprocess.run(
    [
        "mfa",
        "align",
        wav_file,
        lyrics_file,
        "french_mfa",
        output_dir,
        "--clean",
        "--overwrite",
        "--beam", "100",
        "--retry_beam", "400",
        "--output_format", "long_textgrid"
    ],
    #stdout=subprocess.DEVNULL,
    #stderr=subprocess.DEVNULL,
    check=True
    )

    # if not MFA:
    #     cursor.execute(
    #         "UPDATE song_list SET WAV = ? WHERE id = ?",
    #         (wav_file, id)
    #     )
    #     conn.commit()

    print(f"     📝 Fichier MFA créer !")

if __name__ == "__main__":
    main()