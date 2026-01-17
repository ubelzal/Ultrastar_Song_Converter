#!/usr/bin/env python3
"""
Convertisseur TextGrid vers SignStar/UltraStar
Convertit des fichiers de transcription TextGrid en fichiers .txt au format SignStar
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class Word:
    """Représente un mot avec ses timings"""
    def __init__(self, xmin: float, xmax: float, text: str):
        self.xmin = xmin
        self.xmax = xmax
        self.text = text
        self.duration = xmax - xmin

class Phoneme:
    """Représente un phonème avec ses timings"""
    def __init__(self, xmin: float, xmax: float, text: str):
        self.xmin = xmin
        self.xmax = xmax
        self.text = text

class TextGridParser:
    """Parse un fichier TextGrid et extrait les mots et phonèmes"""
    
    @staticmethod
    def parse_tier(content: str, tier_name: str) -> List:
        """Parse un tier spécifique et retourne une liste d'intervalles"""
        items = []
        lines = content.split('\n')
        
        in_tier = False
        current_item = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Détecter le tier recherché
            if f'name = "{tier_name}"' in line:
                in_tier = True
                continue
            
            # Sortir du tier si on arrive à un nouveau tier
            if in_tier and 'class = "IntervalTier"' in line and i > 0:
                in_tier = False
            
            if not in_tier:
                continue
            
            # Extraire xmin
            if 'xmin =' in line:
                match = re.search(r'xmin\s*=\s*([\d.]+)', line)
                if match:
                    current_item['xmin'] = float(match.group(1))
            
            # Extraire xmax
            elif 'xmax =' in line:
                match = re.search(r'xmax\s*=\s*([\d.]+)', line)
                if match:
                    current_item['xmax'] = float(match.group(1))
            
            # Extraire text
            elif 'text =' in line:
                match = re.search(r'text\s*=\s*"([^"]*)"', line)
                if match:
                    text = match.group(1).strip()
                    if text and 'xmin' in current_item and 'xmax' in current_item:
                        if tier_name == 'words':
                            items.append(Word(
                                current_item['xmin'],
                                current_item['xmax'],
                                text
                            ))
                        else:  # phones
                            items.append(Phoneme(
                                current_item['xmin'],
                                current_item['xmax'],
                                text
                            ))
                    current_item = {}
        
        return items
    
    @staticmethod
    def parse(content: str) -> Tuple[List[Word], List[Phoneme]]:
        """Parse le contenu TextGrid et retourne les mots et phonèmes"""
        words = TextGridParser.parse_tier(content, 'words')
        phonemes = TextGridParser.parse_tier(content, 'phones')
        return words, phonemes

class SignStarConverter:
    """Convertit les mots en format SignStar"""
    
    def __init__(self, bpm: float = 300, gap: float = 5000, time_offset: float = 0):
        self.bpm = bpm
        self.gap = gap
        self.time_offset = time_offset  # Offset en secondes à ajouter au timing TextGrid
        self.beat_duration = 60000 / bpm  # durée d'un beat en ms
    
    def time_to_beat(self, time_seconds: float) -> int:
        """Convertit un temps en secondes en beat"""
        # Ajouter l'offset au temps TextGrid
        adjusted_time = time_seconds + self.time_offset
        time_ms = adjusted_time * 1000
        # Ajouter le GAP puis convertir en beats
        beat = (time_ms + self.gap) / self.beat_duration
        return round(beat)
    
    def duration_to_beats(self, duration_seconds: float) -> int:
        """Convertit une durée en secondes en nombre de beats"""
        duration_ms = duration_seconds * 1000
        beats = round(duration_ms / self.beat_duration)
        return max(1, beats)  # minimum 1 beat
    
    def estimate_pitch_from_phonemes(self, word: Word, phonemes: List[Phoneme], 
                                     index: int, total_words: int) -> List[Tuple[Phoneme, int]]:
        """
        Estime la hauteur pour chaque phonème du mot
        Retourne une liste de (phoneme, pitch)
        """
        # Trouver les phonèmes qui correspondent à ce mot
        word_phonemes = [p for p in phonemes 
                        if p.xmin >= word.xmin and p.xmax <= word.xmax + 0.01]
        
        if not word_phonemes:
            # Pas de phonèmes, utiliser une estimation simple
            pitch = self.estimate_pitch_simple(index, total_words, word)
            return [(None, pitch)]
        
        # Estimer le pitch de base pour ce mot
        base_pitch = self.estimate_pitch_simple(index, total_words, word)
        
        # Varier légèrement selon le phonème
        result = []
        for i, phoneme in enumerate(word_phonemes):
            # Voyelles = pitch plus haut, consonnes = pitch plus bas
            vowels = ['a', 'e', 'i', 'o', 'u', 'y']
            
            if any(v in phoneme.text.lower() for v in vowels):
                pitch = base_pitch + (i % 3)  # Varier légèrement
            else:
                pitch = base_pitch - 1
            
            result.append((phoneme, max(-1, min(14, pitch))))
        
        return result
    
    def estimate_pitch_simple(self, index: int, total_words: int, word: Word) -> int:
        """Estimation simple de la hauteur de note"""
        cycle = index // 10
        position = index % 10
        
        if position < 3:
            base_pitch = 1 + (cycle % 3)
        elif position < 6:
            base_pitch = 4 + (cycle % 5)
        elif position < 8:
            base_pitch = 8 + (cycle % 3)
        else:
            base_pitch = 6 + (cycle % 4)
        
        # Ajustement selon la durée
        if word.duration > 0.5:
            base_pitch += 2
        elif word.duration < 0.15:
            base_pitch -= 1
        
        return max(-1, min(14, base_pitch))
    
    def should_add_phrase_break(self, index: int, word: Word, next_word: Word = None) -> bool:
        """Détermine si on doit ajouter une fin de phrase"""
        # Fin de phrase tous les 4-6 mots
        if (index + 1) % 5 == 0:
            return True
        
        # Si pause longue entre deux mots (> 0.5s)
        if next_word and (next_word.xmin - word.xmax) > 0.5:
            return True
        
        return False
    
    def split_word_by_phonemes(self, word: Word, phonemes: List[Phoneme]) -> List[Tuple[str, float, float]]:
        """
        Divise un mot en syllabes/parties basé sur les phonèmes
        Retourne une liste de (texte, xmin, xmax)
        """
        # Trouver les phonèmes du mot
        word_phonemes = [p for p in phonemes 
                        if p.xmin >= word.xmin - 0.01 and p.xmax <= word.xmax + 0.01]
        
        if not word_phonemes:
            return [(word.text, word.xmin, word.xmax)]
        
        # Grouper les phonèmes en syllabes (approximatif)
        syllables = []
        current_syllable = []
        current_text = []
        
        vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'É›', 'É"', 'É'', 'Ã¸', 'Å"', 'É'Ìƒ', 'É›Ìƒ', 'É"Ìƒ', 'É™']
        
        for phoneme in word_phonemes:
            current_syllable.append(phoneme)
            current_text.append(phoneme.text)
            
            # Si c'est une voyelle et qu'on a des consonnes après, créer une syllabe
            is_vowel = any(v in phoneme.text.lower() for v in vowels)
            
            if is_vowel and len(current_syllable) > 0:
                # Vérifier si le prochain phonème est une consonne
                next_idx = word_phonemes.index(phoneme) + 1
                if next_idx < len(word_phonemes):
                    next_phoneme = word_phonemes[next_idx]
                    next_is_vowel = any(v in next_phoneme.text.lower() for v in vowels)
                    
                    if not next_is_vowel:
                        # On peut clore la syllabe
                        xmin = current_syllable[0].xmin
                        xmax = current_syllable[-1].xmax
                        syllables.append((''.join(current_text), xmin, xmax))
                        current_syllable = []
                        current_text = []
        
        # Ajouter la dernière syllabe
        if current_syllable:
            xmin = current_syllable[0].xmin
            xmax = current_syllable[-1].xmax
            syllables.append((''.join(current_text), xmin, xmax))
        
        # Si pas de syllabes générées, retourner le mot entier
        if not syllables:
            return [(word.text, word.xmin, word.xmax)]
        
        # Mapper approximativement les syllabes phonétiques au texte du mot
        # (simplifié - on garde juste le découpage temporel)
        return syllables
    
    def convert(self, words: List[Word], phonemes: List[Phoneme], 
                metadata: Dict[str, str], use_phonemes: bool = True) -> str:
        """Convertit la liste de mots en format SignStar"""
        output = []
        
        # En-tête avec métadonnées
        output.append(f"#TITLE:{metadata.get('title', 'Sans titre')}")
        output.append(f"#ARTIST:{metadata.get('artist', 'Artiste inconnu')}")
        
        if 'edition' in metadata:
            output.append(f"#EDITION:{metadata['edition']}")
        if 'genre' in metadata:
            output.append(f"#GENRE:{metadata['genre']}")
        if 'language' in metadata:
            output.append(f"#LANGUAGE:{metadata['language']}")
        if 'year' in metadata:
            output.append(f"#YEAR:{metadata['year']}")
        
        if 'background' in metadata:
            output.append(f"#BACKGROUND:{metadata['background']}")
        if 'cover' in metadata:
            output.append(f"#COVER:{metadata['cover']}")
        
        output.append(f"#MP3:{metadata.get('mp3', 'audio.mp3')}")
        output.append(f"#BPM:{self.bpm}")
        output.append(f"#GAP:{int(self.gap)}")
        
        # Conversion des notes
        for i, word in enumerate(words):
            # Diviser le mot en parties basées sur les phonèmes si disponibles
            if use_phonemes and phonemes:
                parts = self.split_word_by_phonemes(word, phonemes)
            else:
                parts = [(word.text, word.xmin, word.xmax)]
            
            # Créer une note pour chaque partie
            for part_text, part_xmin, part_xmax in parts:
                start_beat = self.time_to_beat(part_xmin)
                duration = part_xmax - part_xmin
                length = self.duration_to_beats(duration)
                
                # Estimer le pitch
                pitch = self.estimate_pitch_simple(i, len(words), word)
                
                # Type de note
                note_type = ':'
                if i % 15 == 7:  # Note dorée occasionnelle
                    note_type = '*'
                
                output.append(f"{note_type} {start_beat} {length} {pitch} {part_text}")
            
            # Fin de phrase
            next_word = words[i + 1] if i < len(words) - 1 else None
            if next_word and self.should_add_phrase_break(i, word, next_word):
                phrase_end_beat = self.time_to_beat(word.xmax)
                output.append(f"- {phrase_end_beat}")
        
        # Fin de fichier
        output.append("E")
        
        return '\n'.join(output)

def calculate_time_offset(textgrid_path: Path, reference_signstar_path: Path, 
                          bpm: float, gap: float) -> float:
    """
    Calcule l'offset temporel en comparant un fichier TextGrid avec un SignStar de référence
    """
    print("\n🔍 Calcul de l'offset temporel...")
    
    # Lire le TextGrid
    with open(textgrid_path, 'r', encoding='utf-8') as f:
        textgrid_content = f.read()
    
