import re
from pathlib import Path

class TextGridToUltrastar:
    def __init__(self, bpm, gap_ms):
        self.bpm = bpm
        self.gap_ms = gap_ms
        
    def time_to_beat(self, time_seconds):
        """Convertit un temps en secondes en beats UltraStar
        
        Formule UltraStar: beat = ((time_ms - GAP) * BPM) / 15000
        """
        time_ms = time_seconds * 1000.0
        adjusted_ms = time_ms - self.gap_ms
        beats = (adjusted_ms * self.bpm) / 15000.0
        return int(round(beats))
    
    def parse_textgrid(self, filepath):
        """Parse un fichier TextGrid et extrait les tiers words et phones"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire la tier "words"
        words_section = re.search(r'name = "words".*?intervals: size = (\d+)(.*?)(?=item \[|$)', 
                                  content, re.DOTALL)
        
        # Extraire la tier "phones"
        phones_section = re.search(r'name = "phones".*?intervals: size = (\d+)(.*?)(?=item \[|$)', 
                                   content, re.DOTALL)
        
        if not words_section:
            raise ValueError("Tier 'words' non trouvée dans le fichier TextGrid")
        if not phones_section:
            raise ValueError("Tier 'phones' non trouvée dans le fichier TextGrid")
        
        # Parser les intervalles
        interval_pattern = r'intervals \[\d+\]:\s*xmin = ([\d.]+)\s*xmax = ([\d.]+)\s*text = "(.*?)"'
        
        words_intervals = re.findall(interval_pattern, words_section.group(2), re.DOTALL)
        phones_intervals = re.findall(interval_pattern, phones_section.group(2), re.DOTALL)
        
        # Créer les listes de mots et phones
        words = []
        for xmin, xmax, text in words_intervals:
            text = text.strip()
            if text:
                words.append({
                    'xmin': float(xmin),
                    'xmax': float(xmax),
                    'text': text
                })
        
        phones = []
        for xmin, xmax, text in phones_intervals:
            text = text.strip()
            if text:
                phones.append({
                    'xmin': float(xmin),
                    'xmax': float(xmax),
                    'text': text
                })
        
        return words, phones
    
    def group_phones_by_words(self, words, phones):
        """Groupe les phones par mots en fonction de leur timing"""
        word_phone_groups = []
        
        for word in words:
            word_phones = []
            word_text_parts = []
            
            # Trouver tous les phones qui appartiennent à ce mot
            for phone in phones:
                # Un phone appartient à un mot si il est dans sa plage temporelle
                # (avec une petite tolérance)
                if (phone['xmin'] >= word['xmin'] - 0.01 and 
                    phone['xmax'] <= word['xmax'] + 0.01):
                    word_phones.append(phone)
            
            if word_phones:
                # Regrouper les phones en syllabes basiques
                # Pour simplifier, on groupe par petits clusters de phones
                syllables = self.group_phones_into_syllables(word_phones, word['text'])
                word_phone_groups.append({
                    'word': word['text'],
                    'syllables': syllables,
                    'xmin': word['xmin'],
                    'xmax': word['xmax']
                })
        
        return word_phone_groups
    
    def group_phones_into_syllables(self, phones, word_text):
        """Regroupe les phones en syllabes"""
        syllables = []
        
        # Stratégie simple : regrouper 2-4 phones ensemble
        # ou utiliser les pauses naturelles entre phones
        i = 0
        while i < len(phones):
            syllable_phones = []
            syllable_start = phones[i]['xmin']
            syllable_end = phones[i]['xmax']
            
            # Prendre 2-3 phones pour former une syllabe
            # (ajuster selon la complexité souhaitée)
            phones_in_syllable = min(3, len(phones) - i)
            
            for j in range(phones_in_syllable):
                if i + j < len(phones):
                    syllable_phones.append(phones[i + j])
                    syllable_end = phones[i + j]['xmax']
            
            # Extraire une approximation du texte pour cette syllabe
            syllable_text = self.extract_syllable_text(
                word_text, i, phones_in_syllable, len(phones)
            )
            
            syllables.append({
                'xmin': syllable_start,
                'xmax': syllable_end,
                'text': syllable_text,
                'phones': syllable_phones
            })
            
            i += phones_in_syllable
        
        return syllables
    
    def extract_syllable_text(self, word_text, syllable_index, phones_count, total_phones):
        """Extrait approximativement le texte d'une syllabe à partir du mot"""
        # Stratégie simple : diviser le mot proportionnellement
        word_len = len(word_text)
        
        if total_phones <= 1:
            return word_text
        
        # Calculer la position approximative dans le mot
        chars_per_phone = word_len / total_phones
        start_pos = int(syllable_index * chars_per_phone)
        end_pos = int((syllable_index + phones_count) * chars_per_phone)
        
        # S'assurer qu'on ne dépasse pas
        start_pos = min(start_pos, word_len)
        end_pos = min(end_pos, word_len)
        
        if end_pos <= start_pos:
            end_pos = start_pos + 1
        
        syllable = word_text[start_pos:end_pos]
        
        # Si c'est vide, prendre au moins un caractère
        if not syllable and word_text:
            syllable = word_text[0] if syllable_index == 0 else word_text[-1]
        
        return syllable if syllable else word_text
    
    def estimate_pitch(self, syllable_index, total_syllables):
        """Estime une hauteur de note (pitch) basique
        Pitch 0 = C4 (Midi Note 60)
        """
        # Pattern mélodique plus varié
        base_pitches = [0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0, -2]
        return base_pitches[syllable_index % len(base_pitches)]
    
    def convert(self, textgrid_path, output_path, metadata=None):
        """Convertit un fichier TextGrid en format UltraStar"""
        words, phones = self.parse_textgrid(textgrid_path)
        word_phone_groups = self.group_phones_by_words(words, phones)
        
        # Métadonnées par défaut
        if metadata is None:
            metadata = {}
        
        title = metadata.get('title', 'Sans titre')
        artist = metadata.get('artist', 'Artiste inconnu')
        genre = metadata.get('genre', 'Generique')
        
        # Générer le fichier UltraStar
        output_lines = []
        output_lines.append(f"#TITLE:{title}")
        output_lines.append(f"#ARTIST:{artist}")
        output_lines.append(f"#GENRE:{genre}")
        output_lines.append(f"#BPM:{self.bpm}")
        output_lines.append(f"#GAP:{self.gap_ms}")
        
        if 'mp3' in metadata:
            output_lines.append(f"#MP3:{metadata['mp3']}")
        if 'cover' in metadata:
            output_lines.append(f"#COVER:{metadata['cover']}")
        
        output_lines.append("")
        
        # Convertir chaque syllabe en note UltraStar
        syllable_counter = 0
        prev_end_beat = 0
        
        for word_group in word_phone_groups:
            for syllable in word_group['syllables']:
                start_beat = self.time_to_beat(syllable['xmin'])
                end_beat = self.time_to_beat(syllable['xmax'])
                duration = end_beat - start_beat
                
                if duration <= 0:
                    duration = 1
                
                pitch = self.estimate_pitch(syllable_counter, 
                                           sum(len(wg['syllables']) for wg in word_phone_groups))
                
                # Format UltraStar: NoteType StartBeat Length Pitch Text 
                # Important: ajouter un espace après le texte
                output_lines.append(f": {start_beat} {duration} {pitch} {syllable['text']} ")
                
                prev_end_beat = end_beat
                syllable_counter += 1
            
            # Ajouter une fin de phrase après chaque mot si gap significatif
            if word_group != word_phone_groups[-1]:  # Pas le dernier mot
                next_word = word_phone_groups[word_phone_groups.index(word_group) + 1]
                next_start = self.time_to_beat(next_word['xmin'])
                gap_beats = next_start - prev_end_beat
                
                # Si gap > 0.3 seconde (environ 6+ beats à 300 BPM)
                if gap_beats > 6:
                    output_lines.append(f"- {prev_end_beat}")
        
        output_lines.append("E")
        
        # Écrire le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"Conversion terminée : {output_path}")
        print(f"- {len(word_phone_groups)} mots traités")
        print(f"- {syllable_counter} syllabes générées")
        return output_path


# Exemple d'utilisation
if __name__ == "__main__":
   
    # Configuration
    BPM = 300
    GAP_MS = 5000
    
    # Créer le convertisseur
    converter = TextGridToUltrastar(bpm=BPM, gap_ms=GAP_MS)
    
    # Métadonnées de la chanson
    metadata = {
        'title': 'Au pays de Candy',
        'artist': 'Dominique Poulain',
        'genre': 'Generique',
        'mp3': 'Dominique_Poulain - Au_pays_de_Candy.mp3',
        'cover': 'Dominique_Poulain - Au_pays_de_Candy [CO].jpg',
        'GAP': GAP_MS,
        'BPM': BPM
    }
    
    # Chemins des fichiers
    input_file = "/app/output/Dominique_Poulain/Au_pays_de_Candy/Dominique_Poulain - Au_pays_de_Candy.TextGrid"
    output_file = "/app/output/Dominique_Poulain/Au_pays_de_Candy/Dominique_Poulain - Au_pays_de_Candy.txt"
    
    # Effectuer la conversion
    try:
        converter.convert(input_file, output_file, metadata)
        print("✓ Fichier converti avec succès!")
    except FileNotFoundError:
        print(f"Erreur: Fichier '{input_file}' non trouvé")
    except Exception as e:
        print(f"Erreur lors de la conversion: {e}")