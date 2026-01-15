#!/bin/bash

# docker compose run --rm karaoke python bash
docker compose -p karaoke run --rm karaoke python IMPORT_ALL.py

#docker compose -f docker-compose-mfa.yml run --rm mfa python /data/input/MFA.py
docker compose -p mfa -f docker-compose-mfa.yml run --rm mfa python MFA.py
