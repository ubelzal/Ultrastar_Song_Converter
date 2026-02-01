# start.sh for Karaoke Quiz Game
#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env.quiz | xargs)

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000
