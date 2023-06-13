# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcvfs
import sqlite3 as database

settings_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/"
)

spath_database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/spath_cache.db"
)

default_path = "addons://sources/video"


class SPaths:
    def __init__(self):
        self.connect_database()
        self.refresh_spaths = False

    def connect_database(self):
        if not xbmcvfs.exists(settings_path):
            xbmcvfs.mkdir(settings_path)
        self.dbcon = database.connect(spath_database_path, timeout=20)
        self.dbcon.execute(
            "CREATE TABLE IF NOT EXISTS spath (spath_id INTEGER PRIMARY KEY AUTOINCREMENT, spath text)"
        )
        self.dbcur = self.dbcon.cursor()

    def add_spath_to_database(self, spath):
        self.refresh_spaths = True
        self.dbcur.execute(
            "INSERT INTO spath (spath) VALUES (?)",
            (spath,),
        )
        self.dbcon.commit()

    def remove_spath_from_database(self, spath_id):
        self.refresh_spaths = True
        self.dbcur.execute("DELETE FROM spath WHERE spath_id = ?", (spath_id,))
        self.dbcon.commit()

    def delete_all_spaths(self):
        self.refresh_spaths = True
        self.dbcur.execute("DELETE FROM spath")
        self.dbcur.execute("DELETE FROM sqlite_sequence WHERE name='spath'")
        self.dbcon.commit()

    def fetch_all_spaths(self):
        results = self.dbcur.execute(
            "SELECT * FROM spath ORDER BY spath_id DESC"
        ).fetchall()
        return results

    def check_spath_exists(self, spath):
        result = self.dbcur.execute(
            "SELECT * FROM spath WHERE spath = ?", (spath,)
        ).fetchone()
        return result is not None

    def search_input(self):
        prompt = "Search" if xbmcgui.getCurrentWindowId() == 10000 else "New search"
        keyboard = xbmc.Keyboard("", prompt, False)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            search_input = keyboard.getText()
            xbmc.executebuiltin(f"Skin.SetString(SearchInput,{search_input})")
            if xbmcgui.getCurrentWindowId() == 10000:
                xbmc.executebuiltin("ActivateWindow(1121)")
            if not self.check_spath_exists(search_input):
                self.add_spath_to_database(search_input)
