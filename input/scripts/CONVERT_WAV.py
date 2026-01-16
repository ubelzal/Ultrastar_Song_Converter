import re
import unicodedata
import os
import subprocess

def main(id, WAV: str, VOCALS: str, cursor: object, conn: object):

    audio_path = VOCALS

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
    wav_file = os.path.join(output_dir, f"{base_name}.wav")

    wav_file = re.sub(r"\s*\[VOC\]", "", wav_file)

    subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", "16000",
        wav_file
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=True
    )

    cursor.execute(
        "UPDATE song_list SET WAV = ? WHERE id = ?",
        (wav_file, id)
    )
    conn.commit()

    print(f"     📝 Fichier .wav créer !")

if __name__ == "__main__":
    main()