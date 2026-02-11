# main.py - FastAPI server for Karaoke Quiz Game
import os
import random
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(".env.quiz")
DB_PATH = os.getenv("DB_PATH", "/app/input/database/database.db")

# Création de l'application FastAPI
app = FastAPI(title="Karaoke Quiz Game")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montre les fichiers statiques du frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Types de questions possibles
QUESTION_TYPES = [
    "audio_normal",
    "audio_accelerated",
    "lyrics",
    "music_only",
    "audio_reversed",
    "voice_only"
]

# Gestion des joueurs et scores
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.players: dict = {}  # websocket -> {"name": str, "score": int}

    async def connect(self, websocket: WebSocket, name: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.players[websocket] = {"name": name, "score": 0}
        await self.broadcast_players()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.players:
            del self.players[websocket]

    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except:
                pass

    async def broadcast_players(self):
        players_list = [p["name"] for p in self.players.values()]
        await self.broadcast({"players": players_list, "scores": self.get_scores()})

    def get_scores(self):
        return [{"name": p["name"], "score": p["score"]} for p in self.players.values()]

    def add_score(self, websocket: WebSocket, points: int):
        if websocket in self.players:
            self.players[websocket]["score"] += points

manager = ConnectionManager()

# Génération des questions
def generate_question(song_data, question_type):
    result = {"type": question_type}
    mp3_path = song_data.get("mp3")
    lyrics = song_data.get("lyrics", "")
    duration = song_data.get("duration", 180)

    if question_type == "lyrics":
        lines = lyrics.splitlines()
        result["lyrics"] = lines[:2] if len(lines) >= 2 else lines
    else:
        start = random.randint(0, max(1, duration-15))
        result["audio"] = {"file": mp3_path, "start": start, "duration": 15}
        if question_type == "audio_accelerated":
            result["audio"]["speed"] = 2.0
        elif question_type == "audio_reversed":
            result["audio"]["reverse"] = True
        elif question_type == "music_only":
            result["audio"]["file"] = song_data.get("instrumental")
        elif question_type == "voice_only":
            result["audio"]["file"] = song_data.get("vocals")
    return result

def select_random_question(song_data):
    q_type = random.choice(QUESTION_TYPES)
    return generate_question(song_data, q_type)

# WebSocket pour les joueurs
@app.websocket("/ws/quiz")
async def websocket_quiz(websocket: WebSocket):
    await websocket.accept()
    try:
        # Le client envoie son nom dès la connexion
        name_data = await websocket.receive_text()
        name = name_data.strip() or f"Player{len(manager.players)+1}"
        await manager.connect(websocket, name)

        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "next_question":
                try:
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
                            "song": {"title": title, "artist": artist},
                            "question": question
                        })
                    else:
                        await websocket.send_json({"error": "Aucune chanson disponible."})
                except Exception as e:
                    await websocket.send_json({"error": str(e)})

            elif action == "answer":
                points = 10 if data.get("answer") else 0
                manager.add_score(websocket, points)
                await manager.broadcast_players()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_players()

# Endpoints HTTP
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
    except Exception as e:
        return {"error": f"Impossible de lire la table 'questions': {str(e)}"}

@app.get("/")
def root():
    return {"status": "Karaoke Quiz OK"}
