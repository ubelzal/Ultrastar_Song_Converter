import os
import sys
from glob import glob
from pydub import AudioSegment
import subprocess
import shutil

def replace_line(msg):
    sys.stdout.write("\r\033[K" + msg + "\n")
    sys.stdout.flush()

def Separation(id, MP3: str, cursor: object, conn: object):
    
    audio_path = MP3

    # 1️⃣ Appel CLI Demucs
    print("     ℹ️  Lancement de Demucs… cela peut prendre quelques minutes", end="", flush=True)
    # os.system(f"demucs --two-stems=vocals '{audio_path}' > /dev/null 2>&1")
    subprocess.run(
        ["demucs", "--two-stems=vocals", audio_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    # os.system(f"demucs --two-stems=vocals '{audio_path}'")

    # 2️⃣ Récupérer automatiquement le dossier créé par Demucs
    separated_base = "separated/htdemucs/"
    base_name = os.path.splitext(os.path.basename(audio_path))[0]

    # Cherche le dossier qui contient le fichier vocal
    search_pattern = os.path.join(separated_base, f"{base_name}*")
    folders = glob(search_pattern)
    if not folders:
        raise FileNotFoundError(f"❌ Impossible de trouver le dossier de sortie de Demucs pour {base_name}")
    demucs_output_dir = folders[0]  # prend le premier résultat

    # 3️⃣ Chemins WAV générés
    vocals_path_wav = os.path.join(demucs_output_dir, "vocals.wav")
    instr_path_wav = os.path.join(demucs_output_dir, "no_vocals.wav")

    if not os.path.exists(vocals_path_wav) or not os.path.exists(instr_path_wav):
        raise FileNotFoundError("❌ Les fichiers vocaux ou instrumentaux n'ont pas été trouvés après séparation.")

    # 4️⃣ Chemins finaux souhaités
    output_dir = os.path.dirname(audio_path)
    vocals_mp3 = os.path.join(output_dir, f"{base_name}-vocals.mp3")
    instr_mp3 = os.path.join(output_dir, f"{base_name}-no-vocals.mp3")

    # 5️⃣ Conversion WAV -> MP3
    AudioSegment.from_wav(vocals_path_wav).export(vocals_mp3, format="mp3")
    AudioSegment.from_wav(instr_path_wav).export(instr_mp3, format="mp3")

    if os.path.exists(demucs_output_dir):
        shutil.rmtree(demucs_output_dir)

    if MP3:
        cursor.execute(
            "UPDATE song_list SET VOCALS = ? WHERE id = ?",
            (vocals_mp3, id)
        )
        conn.commit()

    if MP3:
        cursor.execute(
            "UPDATE song_list SET INSTRUMENTAL = ? WHERE id = ?",
            (instr_mp3, id)
        )
        conn.commit()

    replace_line("     🎤 Extraction Demucs terminée")