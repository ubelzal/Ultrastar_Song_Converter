import os
import re
import glob
import shutil

# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name.strip().replace(" ", "_")

# ------------------------------------------------------------
# TextGrid → UltraStar (PRO / MOTS ENTIERS)
# ------------------------------------------------------------

class TextGridToUltraStar:

    SCALE = [0, 2, 4, 5, 7, 9, 11, 12]
    TRIGGERS = {
        "et", "mais", "que", "qui", "pour",
        "quand", "comme", "si", "alors"
    }
    VOWELS = "aeiouyàâéèêëîïôùûœ"

    def __init__(self, bpm: int):
        self.bpm = bpm
        self.gap_ms = 0

    # --------------------------------------------------------
    # Temps → beats (UltraStar officiel)
    # --------------------------------------------------------

    def time_to_beat(self, seconds: float) -> int:
        ms = seconds * 1000.0 - self.gap_ms
        if ms < 0:
            return 0
        beats = (ms / 1000.0) * (self.bpm / 60.0)
        return int(round(beats))

    # --------------------------------------------------------
    # Parser TextGrid (tier words)
    # --------------------------------------------------------

    def parse_words(self, path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        section = re.search(
            r'name = "words".*?intervals: size = \d+(.*?)(?=item \[|$)',
            content,
            re.DOTALL
        )

        if not section:
            raise ValueError("Tier 'words' introuvable")

        intervals = re.findall(
            r'xmin = ([\d.]+)\s*xmax = ([\d.]+)\s*text = "(.*?)"',
            section.group(1),
            re.DOTALL
        )

        words = []
        for xmin, xmax, text in intervals:
            text = text.strip()
            if text:
                words.append({
                    "xmin": float(xmin),
                    "xmax": float(xmax),
                    "text": text
                })

        return words

    # --------------------------------------------------------
    # Syllabes (INTERNE UNIQUEMENT)
    # --------------------------------------------------------

    def count_syllables(self, word):
        count = 0
        prev = False
        for c in word.lower():
            is_vowel = c in self.VOWELS
            if is_vowel and not prev:
                count += 1
            prev = is_vowel
        return max(1, count)

    # --------------------------------------------------------
    # Détection intelligente de fin de phrase
    # --------------------------------------------------------

    def should_end_phrase(
        self,
        pause_ms,
        phrase_duration,
        syllables,
        word_text
    ):
        score = 0.0

        if pause_ms > 300:
            score += 2.0
        elif pause_ms > 150:
            score += 1.0

        if phrase_duration > 1.8:
            score += 2.0
        elif phrase_duration > 1.2:
            score += 1.0

        if syllables >= 8:
            score += 2.0
        elif syllables >= 6:
            score += 1.0

        if word_text.lower() in self.TRIGGERS:
            score += 1.0

        return score >= 3.0

    # --------------------------------------------------------
    # Pitch humain simple et chantable
    # --------------------------------------------------------

    def pitch_for(self, index):
        base = 4
        return self.SCALE[(base + index) % len(self.SCALE)]

    # --------------------------------------------------------
    # Conversion principale
    # --------------------------------------------------------

    def convert(self, textgrid, output, meta):
        words = self.parse_words(textgrid)

        # GAP réel = début du premier mot
        self.gap_ms = int(words[0]["xmin"] * 1000)

        lines = []

        # Headers
        for k in (
            "TITLE", "ARTIST", "EDITION", "GENRE",
            "YEAR", "LANGUAGE", "MP3", "COVER", "BACKGROUND"
        ):
            if meta.get(k):
                lines.append(f"#{k}:{meta[k]}")

        lines.append(f"#BPM:{self.bpm}")
        lines.append(f"#GAP:{self.gap_ms}")
        lines.append("")

        phrase_start_time = words[0]["xmin"]
        phrase_syllables = 0
        phrase_note_indices = []

        prev_end = 0
        note_index = 0

        for i, w in enumerate(words):
            start = self.time_to_beat(w["xmin"])
            end = self.time_to_beat(w["xmax"])
            duration = max(1, end - start)

            pitch = self.pitch_for(note_index)

            phrase_note_indices.append(len(lines))
            lines.append(f": {start} {duration} {pitch} {w['text']} ")

            prev_end = end
            note_index += 1
            phrase_syllables += self.count_syllables(w["text"])

            pause_ms = 0
            if i < len(words) - 1:
                pause_ms = (words[i + 1]["xmin"] - w["xmax"]) * 1000

            phrase_duration = w["xmax"] - phrase_start_time

            if self.should_end_phrase(
                pause_ms,
                phrase_duration,
                phrase_syllables,
                w["text"]
            ):
                # Golden note = note centrale de la phrase
                if phrase_note_indices:
                    golden = phrase_note_indices[len(phrase_note_indices) // 2]
                    lines[golden] = lines[golden].replace(": ", "* ", 1)

                lines.append(f"- {prev_end}")
                phrase_note_indices.clear()
                phrase_syllables = 0
                phrase_start_time = (
                    words[i + 1]["xmin"] if i < len(words) - 1 else 0
                )

        lines.append("E")

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ UltraStar quasi-officiel généré : {output}")

# ------------------------------------------------------------
# MAIN (pipeline existante)
# ------------------------------------------------------------

def main(
    id, YEAR, MP3, COVER, ARTIST, TITLE, BPM,
    VOCALS, INSTRUMENTAL, GAP, LANGUAGE, MFA,
    cursor, conn
):
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

    meta = {
        "TITLE": TITLE,
        "ARTIST": ARTIST,
        "LANGUAGE": LANGUAGE,
        "YEAR": str(YEAR),
        "MP3": f"{safe_artist} - {safe_title}.mp3",
        "COVER": f"{safe_artist} - {safe_title} [CO].jpg",
        "BACKGROUND": f"{safe_artist} - {safe_title} [BG].jpg",
        "EDITION": "mange-disque.tv",
        "GENRE": "Generique"
    }

    converter = TextGridToUltraStar(BPM)
    converter.convert(MFA, out, meta)

    cursor.execute(
        "UPDATE song_list SET Export_Ultrastar='Y' WHERE id=?",
        (id,)
    )
    conn.commit()

    print("🪩 Export UltraStar terminé (version officielle-like)")
