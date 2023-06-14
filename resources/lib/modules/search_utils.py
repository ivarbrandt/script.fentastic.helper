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

    def remove_all_spaths(self):
        dialog = xbmcgui.Dialog()
        title = "FENtastic"
        prompt = "Are you sure you want to clear all search history? Once cleared, these items cannot be recovered. Proceed?"
        self.fetch_all_spaths()
        if dialog.yesno(title, prompt):
            self.refresh_spaths = True
            self.dbcur.execute("DELETE FROM spath")
            self.dbcur.execute("DELETE FROM sqlite_sequence WHERE name='spath'")
            self.dbcon.commit()
            dialog.ok("FENtastic", "Search history cleared")

    def fetch_all_spaths(self):
        results = self.dbcur.execute(
            "SELECT * FROM spath ORDER BY spath_id DESC"
        ).fetchall()
        return results

    def check_spath_exists(self, spath):
        result = self.dbcur.execute(
            "SELECT spath_id FROM spath WHERE spath = ?", (spath,)
        ).fetchone()
        return result[0] if result else None

    def search_input(self, search_term=None):
        if search_term is None or not search_term.strip():
            prompt = "Search" if xbmcgui.getCurrentWindowId() == 10000 else "New search"
            keyboard = xbmc.Keyboard("", prompt, False)
            keyboard.doModal()
            if keyboard.isConfirmed():
                search_term = keyboard.getText()
                if not search_term or not search_term.strip():
                    return
            else:
                return
        xbmc.executebuiltin(f"Skin.SetString(SearchInput,{search_term})")
        if xbmcgui.getCurrentWindowId() == 10000:
            xbmc.executebuiltin("ActivateWindow(1121)")
        # else:
        #     xbmc.executebuiltin("ReloadSkin()")

        existing_spath = self.check_spath_exists(search_term)
        if existing_spath:
            self.remove_spath_from_database(existing_spath)
        self.add_spath_to_database(search_term)

    def re_search(self):
        search_term = xbmc.getInfoLabel("ListItem.Label")
        print("Here is the search term", search_term)
        self.search_input(search_term)
        # xbmc.executebuiltin("ReloadSkin()")
