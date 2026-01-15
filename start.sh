docker compose run --rm karaoke python /app/input/IMPORT_ALL.py

docker compose -f docker-compose-mfa.yml run --rm mfa python /data/input/MFA.py
