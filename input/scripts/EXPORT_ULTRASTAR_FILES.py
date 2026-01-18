import re
from pathlib import Path
import shutil
import os
import glob

class TextGridToUltraStar:
    def __init__(self, bpm=300):
        self.bpm = bpm
        self.beat_duration = 60.0 / (bpm * 4)  # Durée d'un beat en secondes
        
    def parse_textgrid(self, textgrid_path):
        """Parse le fichier TextGrid et extrait les mots avec leurs timings"""
        with open(textgrid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire les intervalles de mots
        words = []
        in_words_tier = False
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Détecter le tier "words"
            if 'name = "words"' in line:
                in_words_tier = True
            elif in_words_tier and 'intervals [' in line:
                # Extraire xmin, xmax et text
                xmin = None
                xmax = None
                text = None
                
                # Chercher les 3 lignes suivantes
                for j in range(i+1, min(i+4, len(lines))):
                    if 'xmin' in lines[j]:
                        xmin = float(lines[j].split('=')[1].strip())
                    elif 'xmax' in lines[j]:
                        xmax = float(lines[j].split('=')[1].strip())
                    elif 'text' in lines[j]:
                        text = lines[j].split('=')[1].strip().strip('"').strip()
                
                # Ajouter seulement si le texte n'est pas vide
                if text and xmin is not None and xmax is not None:
                    words.append({
                        'text': text,
                        'start': xmin,
                        'end': xmax,
                        'duration': xmax - xmin
                    })
            elif in_words_tier and 'item [' in line and 'item [1]' not in line:
                # Fin du tier words
                break
                
            i += 1
        
        return words
    
    def time_to_beat(self, time_seconds):
        """Convertit un temps en secondes en beats UltraStar"""
        return int(round(time_seconds / self.beat_duration))
    
    def estimate_pitch(self, word_index, total_words):
        """Estime une hauteur de note basique (à améliorer avec analyse audio)"""
        # Pattern simple qui varie la hauteur
        base_pitch = 4
        variation = (word_index % 8) - 2
        return base_pitch + variation
    
    def create_ultrastar_file(self, words, output_path, metadata=None):
        """Crée le fichier UltraStar à partir des mots"""
        if metadata is None:
            metadata = {}
        
        lines = []
        
        # En-tête
        lines.append(f"#TITLE:{metadata.get('title', 'Sans titre')}")
        lines.append(f"#ARTIST:{metadata.get('artist', 'Artiste inconnu')}")
        lines.append(f"#EDITION:{metadata.get('edition', '')}")
        lines.append(f"#GENRE:{metadata.get('genre', '')}")
        lines.append(f"#BACKGROUND:{metadata.get('background', '')}")
        lines.append(f"#COVER:{metadata.get('cover', '')}")
        lines.append(f"#MP3:{metadata.get('mp3', '')}")
        lines.append(f"#BPM:{self.bpm}")
        lines.append(f"#GAP:{metadata.get('gap', 5000)}")
        
        # Traiter les mots
        prev_end_beat = 0
        
        for i, word in enumerate(words):
            start_beat = self.time_to_beat(word['start'])
            end_beat = self.time_to_beat(word['end'])
            duration = end_beat - start_beat
            
            # Assurer une durée minimale
            if duration < 1:
                duration = 1
                end_beat = start_beat + duration
            
            # Ajouter une pause si nécessaire
            if start_beat > prev_end_beat + 2:
                lines.append(f"- {prev_end_beat}")
            
            # Estimer la hauteur de note
            pitch = self.estimate_pitch(i, len(words))
            
            # Formater le mot (ajouter un espace après)
            text = word['text'].strip() + " "

            # Ajouter la ligne de note
            lines.append(f": {start_beat} {duration} {pitch} {text}")
            
            prev_end_beat = end_beat
        
        # Fin du fichier
        lines.append("E")
        
        # Écrire le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        #print(f"Fichier UltraStar créé: {output_path}")
        #print(f"Nombre de notes: {len(words)}")

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name.strip().replace(" ", "_")

def main(id, ARTIST, TITLE, YEAR, MP3, COVER, BPM, VOCALS, INSTRUMENTAL, GAP, LANGUAGE,
    MFA, GENRE, cursor, conn):

    safe_artist = sanitize_filename(ARTIST)
    safe_title = sanitize_filename(TITLE)

    base = "/app/UltraStar"
    target = os.path.join(base, safe_artist, safe_title)
    os.makedirs(target, exist_ok=True)

    # Copier médias (MP3 et JPG)
    for ext in ("*.mp3", "*.jpg"):
        for f in glob.glob(os.path.join(os.path.dirname(MP3), ext)):
            shutil.copy2(f, target)

    output_file = os.path.join(target, f"{safe_artist} - {safe_title}.txt")

    # Configuration
    textgrid_file = MFA
    output_file = os.path.join(target, f"{safe_artist} - {safe_title}.txt")
    bpm = BPM
    
    # Métadonnées (à adapter selon vos fichiers)
    metadata = {
        'title': TITLE,
        'artist': ARTIST,
        'edition': '',
        'genre': GENRE,
        'background': '',
        'cover': f"{safe_artist} - {safe_title} [CO].jpg",
        'mp3': f"{safe_artist} - {safe_title}.mp3",
        'gap': GAP
    }
    
    # Conversion
    converter = TextGridToUltraStar(bpm=bpm)
    
    # print(f"Lecture du fichier TextGrid: {textgrid_file}")
    words = converter.parse_textgrid(textgrid_file)
    # print(f"Mots extraits: {len(words)}")
    
    # print(f"\nCréation du fichier UltraStar...")
    converter.create_ultrastar_file(words, output_file, metadata)
    
    cursor.execute(
        "UPDATE song_list SET Export_Ultrastar='N' WHERE id=?",
        (id,)
    )
    conn.commit()

    print("     🎶 Export UltraStar terminé (version officielle)")

    # print("\n✓ Conversion terminée!")
    # print(f"\nPour améliorer les hauteurs de notes, vous pouvez:")
    # print("1. Utiliser une analyse de fréquence audio (librosa, aubio)")
    # print("2. Ajuster manuellement les valeurs de pitch dans le fichier généré")

if __name__ == "__main__":
    main()