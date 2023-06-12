import xbmc
import sqlite3 as database
import sys


def get_search_input():
    keyboard = xbmc.Keyboard("", "Search", False)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_input = keyboard.getText()
        xbmc.executebuiltin(f"Skin.SetString(SearchInput,{search_input})")
        xbmc.executebuiltin("ActivateWindow(1121)")


def main():
    if "get_search_input" in sys.argv:
        get_search_input()


if __name__ == "__main__":
    main()
