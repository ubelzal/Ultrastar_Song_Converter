# main.py - FastAPI server for Karaoke Quiz Game
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import sqlite3

load_dotenv('.env.quiz')

DB_PATH = os.getenv('DB_PATH', 'database.db')

app = FastAPI()

origins = [
    "*"  # For development, allow all. Restrict in production.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION_TYPES = [
    "audio_normal",         # 1. Extrait normal
    "audio_accelerated",   # 2. Extrait accéléré
    "lyrics",              # 3. Extrait lyrics
    "music_only",          # 4. Musique seule
    "audio_reversed",      # 5. Extrait à l'envers
    "voice_only"           # 6. Voix seule
]

# WebSocket manager for multiplayer
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.current_player: int = 0
        self.num_players: int = 1

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.num_players = len(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.num_players = len(self.active_connections)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def get_current_player(self):
        if self.active_connections:
            return self.active_connections[self.current_player]
        return None

manager = ConnectionManager()



def generate_question(song_data, question_type):
    """
    song_data: dict contenant les infos de la chanson (titre, artiste, mp3, lyrics, etc.)
    question_type: type de question à générer
    Retourne un dict avec les données nécessaires pour le client
    """
    import random
    result = {"type": question_type}
    mp3_path = song_data.get("mp3")
    lyrics = song_data.get("lyrics", "")
    duration = song_data.get("duration", 180)
    # 1. Extrait audio normal
    if question_type == "audio_normal":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15}
    # 2. Extrait audio accéléré
    elif question_type == "audio_accelerated":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15, "speed": 2.0}
    # 3. Extrait lyrics
    elif question_type == "lyrics":
        lines = lyrics.splitlines()
        if len(lines) >= 2:
            idx = random.randint(0, len(lines)-2)
            result["lyrics"] = lines[idx:idx+2]
        else:
            result["lyrics"] = lines
    # 4. Musique seule
    elif question_type == "music_only":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": song_data.get("instrumental"), "start": start, "duration": 15}
    # 5. Audio inversé
    elif question_type == "audio_reversed":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15, "reverse": True}
    # 6. Voix seule
    elif question_type == "voice_only":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": song_data.get("vocals"), "start": start, "duration": 15}
    return result

def select_random_question(song_data):
    question_type = random.choice(QUESTION_TYPES)
    return generate_question(song_data, question_type)

@app.websocket("/ws/quiz")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Le serveur attend une demande de question
            data = await websocket.receive_text()
            if data == "next_question":
                # Connexion à la base pour récupérer une chanson aléatoire
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id, ARTIST, TITLE, MP3, VOCALS, INSTRUMENTAL, LYRICS, YEAR FROM song_list ORDER BY RANDOM() LIMIT 1")
                row = cursor.fetchone()
                conn.close()
                if row:
                    id, artist, title, mp3, vocals, instrumental, lyrics, year = row
                    # TODO: calculer la durée réelle du MP3 si possible
                    song_data = {
                        "id": id,
                        "title": title,
                        "artist": artist,
                        "mp3": mp3,
                        "vocals": vocals,
                        "instrumental": instrumental,
                        "lyrics": lyrics or "",
                        "duration": 180,
                        "year": year
                    }
                    question = select_random_question(song_data)
                    await websocket.send_json({"question": question, "song": {"title": title, "artist": artist}})
                else:
                    await websocket.send_json({"error": "Aucune chanson disponible dans la base."})
            else:
                await manager.broadcast(f"Player says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/questions")
def get_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions LIMIT 10")
    questions = cursor.fetchall()
    conn.close()
    return {"questions": questions}

# Add more endpoints for game logic, player management, etc.
