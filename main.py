# main.py - FastAPI server for Karaoke Quiz Game
import os
import random
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('.env.quiz')
# DB_PATH = os.getenv('DB_PATH', '/app/input/database/database.db')
DB_PATH = "/app/input/database/database.db"

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Développement, autoriser tous
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Types de questions
QUESTION_TYPES = [
    "audio_normal",
    "audio_accelerated",
    "lyrics",
    "music_only",
    "audio_reversed",
    "voice_only"
]

# Gestion WebSocket pour multi-joueur
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
        for conn in self.active_connections:
            await conn.send_text(message)

    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def get_current_player(self):
        if self.active_connections:
            return self.active_connections[self.current_player]
        return None

manager = ConnectionManager()

# Génération d'une question
def generate_question(song_data: dict, question_type: str) -> dict:
    result = {"type": question_type}
    mp3_path = song_data.get("mp3")
    lyrics = song_data.get("lyrics", "")
    duration = song_data.get("duration", 180)

    if question_type == "audio_normal":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15}
    elif question_type == "audio_accelerated":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15, "speed": 2.0}
    elif question_type == "lyrics":
        lines = lyrics.splitlines()
        if len(lines) >= 2:
            idx = random.randint(0, len(lines)-2)
            result["lyrics"] = lines[idx:idx+2]
        else:
            result["lyrics"] = lines
    elif question_type == "music_only":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": song_data.get("instrumental"), "start": start, "duration": 15}
    elif question_type == "audio_reversed":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15, "reverse": True}
    elif question_type == "voice_only":
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": song_data.get("vocals"), "start": start, "duration": 15}

    return result

def select_random_question(song_data: dict) -> dict:
    question_type = random.choice(QUESTION_TYPES)
    return generate_question(song_data, question_type)

# Endpoints FastAPI

@app.get("/")
def root():
    return {"status": "Karaoke Quiz OK"}

@app.get("/songs")
def get_songs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ARTIST, TITLE FROM song_list LIMIT 10")
        songs = cursor.fetchall()
        conn.close()
        return {"songs": songs}
    except Exception as e:
        return {"error": f"Impossible de lire la table 'song_list': {str(e)}"}


@app.get("/questions")
def get_questions():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions LIMIT 10")
        questions = cursor.fetchall()
        conn.close()
        return {"questions": questions}
    except sqlite3.OperationalError:
        return {"error": "Table 'questions' introuvable dans la base."}

# WebSocket pour les questions
@app.websocket("/ws/quiz")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "next_question":
                # Récupérer une chanson aléatoire
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, ARTIST, TITLE, MP3, VOCALS, INSTRUMENTAL, LYRICS, YEAR "
                    "FROM song_list ORDER BY RANDOM() LIMIT 1"
                )
                row = cursor.fetchone()
                conn.close()
                if row:
                    id, artist, title, mp3, vocals, instrumental, lyrics, year = row
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
                    await websocket.send_json({
                        "question": question,
                        "song": {"title": title, "artist": artist}
                    })
                else:
                    await websocket.send_json({"error": "Aucune chanson disponible"})
            else:
                await manager.broadcast(f"Player says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
