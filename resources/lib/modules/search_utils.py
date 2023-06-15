# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcvfs
import sqlite3 as database
from modules import xmls
from threading import Thread

# from modules.logger import logger

settings_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/"
)

spath_database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.fentastic.helper/spath_cache.db"
)

search_history_xml = "script-fentastic-search_history"

default_xmls = {
    "search_history": (search_history_xml, xmls.default_history, "SearchHistory")
}


default_path = "addons://sources/video"


class SPaths:
    def __init__(self, spaths=None):
        self.connect_database()
        if spaths is None:
            self.spaths = []
        else:
            self.spaths = spaths
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
            self.make_default_xml()

    def fetch_all_spaths(self):
        results = self.dbcur.execute(
            "SELECT * FROM spath ORDER BY spath_id DESC"
        ).fetchall()
        return results

    def make_search_history_xml(self, active_spaths):
        if not self.refresh_spaths:
            return
        if not active_spaths:
            self.make_default_xml()

        xml_file = "special://skin/xml/%s.xml" % (search_history_xml)

        final_format = xmls.media_xml_start.format(main_include="SearchHistory")
        for _, spath in active_spaths:
            body = xmls.history_xml_body
            body = body.format(spath=spath)
            final_format += body
        final_format += xmls.media_xml_end
        self.write_xml(xml_file, final_format)

    def write_xml(self, xml_file, final_format):
        with xbmcvfs.File(xml_file, "w") as f:
            f.write(final_format)
        xbmc.executebuiltin("ReloadSkin()")

    def make_default_xml(self):
        item = default_xmls["search_history"]
        final_format = item[1].format(includes_type=item[2])
        xml_file = "special://skin/xml/%s.xml" % item[0]
        with xbmcvfs.File(xml_file, "w") as f:
            f.write(final_format)
        xbmc.executebuiltin("ReloadSkin()")

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
        self.fetch_all_spaths()
        self.make_search_history_xml(self.fetch_all_spaths())

    def re_search(self):
        search_term = xbmc.getInfoLabel("ListItem.Label")
        print("Here is the search term", search_term)
        self.search_input(search_term)
        # xbmc.executebuiltin("ReloadSkin()")
