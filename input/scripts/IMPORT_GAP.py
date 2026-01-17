from pydub import AudioSegment
import numpy as np

def find_lyric_start_delay(wav_file, silence_thresh=-35, frame_ms=5):
    """
    Retourne le délai avant le premier mot (en ms)
    """

    audio = AudioSegment.from_wav(wav_file)
    audio = audio.set_channels(1)  # mono pour plus de précision

    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate

    frame_size = int(sample_rate * frame_ms / 1000)

    max_amplitude = np.max(np.abs(samples))
    threshold = max_amplitude * (10 ** (silence_thresh / 20))

    for i in range(0, len(samples), frame_size):
        frame = samples[i:i + frame_size]
        if np.max(np.abs(frame)) > threshold:
            return int(i / sample_rate * 1000)

    return 0  # si aucune voix détectée


# === UTILISATION ===
def main(id, WAV: str, cursor: object, conn: object):

    delay_ms = find_lyric_start_delay(WAV)

    cursor.execute(
        "UPDATE song_list SET GAP = ? WHERE id = ?",
        (delay_ms, id)
    )
    conn.commit()

    print(f"     ∅  GAP importé !")
