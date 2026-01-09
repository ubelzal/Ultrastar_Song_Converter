import os
import re
import sqlite3
import subprocess
import time
from tqdm import tqdm
from yt_dlp import YoutubeDL

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

def load_MP3(id,YoutubeID: str, TITLE: str, ARTIST: str, MP3, cursor, conn ):

    safe_name = sanitize_filename(TITLE or f"song_{id}")
    safe_title = sanitize_filename(TITLE or f"song_{id}")
    safe_artist = sanitize_filename(ARTIST)

    #import subprocess Download MP3
    if YoutubeID and safe_artist and safe_title:
        song_dir = os.path.join("/app/output", safe_artist, safe_title)
        os.makedirs(song_dir, exist_ok=True)

        mp3_path = os.path.join(song_dir, f"{safe_title}.mp3")

        if not os.path.exists(mp3_path):

            youtube_url = f"https://www.youtube.com/watch?v={YoutubeID}"
            output_template = os.path.join(song_dir, f"{safe_title}.%(ext)s")

            download_audio(youtube_url,output_template)                 

        if os.path.exists(mp3_path):
            relative_mp3_path = os.path.relpath(mp3_path)

            if not MP3:
                cursor.execute(
                    "UPDATE song_list SET MP3 = ? WHERE id = ?",
                    (relative_mp3_path, id)
                )
                conn.commit()
  

            time.sleep(0.25)


def download_audio(youtube_url, output_template):

    pbar = tqdm(
        total=100,
        unit="%",
        desc="     Téléchargement",
        ncols=80
    )

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)

            if total:
                percent = downloaded / total * 100
                pbar.n = percent
                pbar.refresh()

        elif d['status'] == 'finished':
            pbar.n = 100
            pbar.refresh()
            pbar.close()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])