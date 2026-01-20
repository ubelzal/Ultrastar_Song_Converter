# import pylast
import json
# import musicbrainzngs
from SPARQLWrapper import SPARQLWrapper, JSON

# Application name	UltraStarGenreTool
# API key	f0932cc1077866388abf874dac1a697b
# Shared secret	44fa30fa234973c4b3caf574582de276
# Registered to	ubelzal

def main(id, ARTIST: str, TITLE: str, TAGS: str, cursor: object, conn: object):
    
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    artist = ARTIST

    artist = artist.replace('"', '\\"')
    
    sparql.setTimeout(5)
    
    query = f"""
    SELECT DISTINCT ?genreLabel WHERE {{
      ?artist rdfs:label "{artist}"@fr .
      ?artist wdt:P31 wd:Q5 .
      ?artist wdt:P106 wd:Q639669 .
      ?artist wdt:P136 ?genre .
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "fr,en" .
      }}
    }}
    LIMIT 1
    """

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    genres = [r["genreLabel"]["value"] for r in results["results"]["bindings"]]
    # print(genres)

    tags_json = json.dumps(genres, ensure_ascii=False)

    cursor.execute(
        "UPDATE song_list SET TAGS = ? WHERE id = ?",
        (tags_json, id)
    )
    conn.commit()

    print(f"     🏷️  Tags importé !")


# def main_old(id, ARTIST: str, TITLE: str, TAGS: str, cursor: object, conn: object):

#     API_KEY = "f0932cc1077866388abf874dac1a697b"
#     API_SECRET = "44fa30fa234973c4b3caf574582de276"

#     network = pylast.LastFMNetwork(
#         api_key=API_KEY,
#         api_secret=API_SECRET
#     )

#     track = network.get_track(
#         ARTIST,
#         TITLE
#     )

#     tags = track.get_top_tags(limit=5)
#     genres = [tag.item.name for tag in tags]

#     tags_json = json.dumps(genres, ensure_ascii=False)

#     if not TAGS:
#         cursor.execute(
#             "UPDATE song_list SET TAGS = ? WHERE id = ?",
#             (tags_json, id)
#         )
#         conn.commit()

#     print(f"     🏷️  Tags importé !")


if __name__ == "__main__":
    main()