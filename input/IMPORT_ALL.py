from scripts import IMPORT_MP3
import os

DATABASE_LOCATION="/app/input/database/database.db"
pwd = os.getcwd()

# Clear terminal (optionnel)
os.system("clear" if os.name == "posix" else "cls")

def main():

    # Importation des MP3 de YouTube
    IMPORT_MP3.read_from_db(DATABASE_LOCATION)

if __name__ == "__main__":
    main()