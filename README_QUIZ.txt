docker build -f Dockerfile.quiz -t karaoke-quiz .

docker stop karaoke-quiz

docker rm karaoke-quiz

docker run -d --name karaoke-quiz -p 8000:8000 karaoke-quiz

docker ps

# interactif mode
docker exec -it karaoke-quiz bash

