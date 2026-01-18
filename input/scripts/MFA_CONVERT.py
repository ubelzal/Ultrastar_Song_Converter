import re
import unicodedata
import os
import subprocess

def get_mfa_models(language: str):
    language = language.lower()

    if language == "french":
        return "french_mfa", "french_mfa"
    elif language == "english":
        return "english_us_arpa", "english_us_arpa"
    else:
        raise ValueError(f"Langue non supportée: {language}")

def sanitize_filename(name: str) -> str:
    """
    Nettoie le nom pour être sûr qu'il puisse être utilisé comme nom de fichier.
    Conserve les lettres accentuées et remplace les espaces par "_".
    """
    # remplacer les caractères invalides par "_"
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # remplacer les espaces par "_"
    name = name.replace(" ", "_")
    return name

def main(id, WAV: str, MFA: str, LANGUAGE: str,speaker: int, cursor: object, conn: object):

    audio_path = WAV
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.dirname(audio_path)
    wav_file = os.path.join(output_dir, f"{base_name}.wav")

    lyrics_file = os.path.join(output_dir, f"{base_name}.txt")
    lyrics_file = re.sub(r"\s*\[VOC\]", "", lyrics_file)

    TextGrid_file = os.path.join(output_dir, f"{base_name}.TextGrid")
    TextGrid_file = re.sub(r"\s*\[VOC\]", "", TextGrid_file)

    # DOSSIER corpus (wav + txt dedans)
    corpus_dir = os.path.dirname(audio_path)

    dictionary, acoustic_model = get_mfa_models(LANGUAGE)

    speakers = 1  # ou 2, 3, etc.

    mfa_cmd = [
        "mfa",
        "align",
        corpus_dir,
        dictionary,
        acoustic_model,
        output_dir,
        "--clean",
        "--overwrite",
        "--beam", "100",
        "--retry_beam", "400",
        "--output_format", "long_textgrid",
        "--include_original_text",
        "--conservative_alignment"
    ]

    # Ajout conditionnel
    if speakers == 1:
        mfa_cmd.append("--single_speaker")

    subprocess.run(
        mfa_cmd,
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