# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import sqlite3 as database


def search_input():
    prompt = "Search" if xbmcgui.getCurrentWindowId() == 10000 else "New search"
    keyboard = xbmc.Keyboard("", prompt, False)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_input = keyboard.getText()
        xbmc.executebuiltin(f"Skin.SetString(SearchInput,{search_input})")
        if xbmcgui.getCurrentWindowId() == 10000:
            xbmc.executebuiltin("ActivateWindow(1121)")
