import xbmc, xbmcvfs
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import sqlite3 as database
import requests
import json

settings_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/"
)
ratings_database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/ratings_cache.db"
)


def make_session(url="https://"):
    session = requests.Session()
    session.mount(url, requests.adapters.HTTPAdapter(pool_maxsize=100))
    return session


url = "http://www.omdbapi.com/?apikey=%s&i=%s&tomatoes=True&r=xml"
session = make_session("http://www.omdbapi.com/")


class OMDbAPI:
    def __init__(self):
        self.connect_database()

    def connect_database(self):
        if not xbmcvfs.exists(settings_path):
            xbmcvfs.mkdir(settings_path)
        self.dbcon = database.connect(ratings_database_path, timeout=20)
        self.dbcon.execute(
            """
        CREATE TABLE IF NOT EXISTS ratings (
            imdb_id TEXT PRIMARY KEY,
            ratings TEXT,
            last_updated TIMESTAMP
        );
        """
        )
        self.dbcur = self.dbcon.cursor()

    def insert_or_update_ratings(self, imdb_id, ratings):
        self.dbcur.execute("SELECT imdb_id FROM ratings WHERE imdb_id=?", (imdb_id,))
        entry = self.dbcur.fetchone()
        ratings_data = json.dumps(ratings)
        if entry:
            self.dbcur.execute(
                """
            UPDATE ratings 
            SET ratings=?, last_updated=?
            WHERE imdb_id=?
            """,
                (ratings_data, datetime.now(), imdb_id),
            )
        else:
            self.dbcur.execute(
                """
            INSERT INTO ratings (imdb_id, ratings, last_updated)
            VALUES (?, ?, ?)
            """,
                (imdb_id, ratings_data, datetime.now()),
            )
        self.dbcon.commit()

    def get_cached_ratings(self, imdb_id):
        self.dbcur.execute(
            "SELECT imdb_id, ratings, last_updated FROM ratings WHERE imdb_id=?",
            (imdb_id,),
        )
        entry = self.dbcur.fetchone()
        if entry:
            _, ratings_data, last_updated = entry
            ratings = json.loads(ratings_data)
            if datetime.now() - datetime.strptime(
                last_updated, "%Y-%m-%d %H:%M:%S.%f"
            ) < timedelta(days=7):
                return ratings
        return None

    def fetch_info(self, meta, api_key):
        imdb_id = meta.get("imdb_id")
        if not imdb_id or not api_key:
            return {}
        cached_ratings = self.get_cached_ratings(imdb_id)
        if cached_ratings:
            return cached_ratings
        data = self.get_result(imdb_id, meta)
        self.insert_or_update_ratings(imdb_id, data)
        return data

    def get_result(self, imdb_id, api_key):
        api_key = xbmc.getInfoLabel("Skin.String(omdb_api_key)")
        if not api_key:
            xbmc.log("No OMDb API key set in the skin settings.", level=xbmc.LOGERROR)
            return {}
        url = (
            f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}&tomatoes=True&r=xml"
        )
        xbmc.log(
            "Fetching fresh ratings for IMDb ID {} from the OMDb API.".format(imdb_id),
            level=xbmc.LOGDEBUG,
        )
        response = session.get(url)
        if response.status_code != 200:
            xbmc.log(
                f"Error fetching data from OMDb for IMDb ID {imdb_id}. Status code: {response.status_code}"
            )
            return {}
        root = ET.fromstring(response.content)
        movie_data = root.find("movie")
        if movie_data is None:
            return {}
        data = {
            "metascore": movie_data.get("metascore") + "%"
            if movie_data.get("metascore")
            else None,
            "tomatoMeter": movie_data.get("tomatoMeter") + "%"
            if movie_data.get("tomatoMeter")
            else None,
            "tomatoUserMeter": movie_data.get("tomatoUserMeter") + "%"
            if movie_data.get("tomatoUserMeter")
            else None,
            "tomatoImage": movie_data.get("tomatoImage"),
            "imdbRating": movie_data.get("imdbRating"),
        }
        return data


def test_api():
    xbmc.log("test_api function triggered!", level=xbmc.LOGDEBUG)
    api_key = xbmc.getInfoLabel("Skin.String(omdb_api_key)")
    imdb_id = xbmc.getInfoLabel("ListItem.IMDBNumber")
    if not api_key:
        xbmc.log("No OMDb API key set in the skin settings.", level=xbmc.LOGERROR)
        return {}
    if not imdb_id or not imdb_id.startswith("tt"):
        xbmc.log(
            "Could not retrieve a valid IMDb ID from the focused item.",
            level=xbmc.LOGDEBUG,
        )
        return {}
    omdb_api_instance = OMDbAPI()
    result = omdb_api_instance.fetch_info({"imdb_id": imdb_id}, api_key)
    xbmc.log(f"Ratings for IMDb ID {imdb_id}: {result}", level=xbmc.LOGDEBUG)
    return result
