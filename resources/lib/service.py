import xbmc, xbmcgui
from threading import Thread
from modules.OMDb import OMDbAPI
import json

# logger = xbmc.log
empty_ratings = {
    "metascore": "",
    "tomatoMeter": "",
    "tomatoUserMeter": "",
    "tomatoImage": "",
    "imdbRating": "",
    "tmdbRating": "",
}


class RatingsService(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.omdb_api = OMDbAPI
        self.window = xbmcgui.Window
        self.get_window_id = xbmcgui.getCurrentWindowId
        self.get_infolabel = xbmc.getInfoLabel
        self.get_visibility = xbmc.getCondVisibility
        # self.current_imdb_id = ""

    def listitem_monitor(self):
        while not self.abortRequested():
            if xbmc.getSkinDir() != "skin.fentastic":
                # logger("###skin is not FENtastic###", 2)
                self.waitForAbort(15)
                continue
            api_key = self.get_infolabel("Skin.String(omdb_api_key)")
            if not api_key:
                # logger("###no API key###", 2)
                self.waitForAbort(10)
                continue
            if not self.get_visibility(
                "Window.IsVisible(videos) | Window.IsVisible(home) | Window.IsVisible(11121)"
            ):
                # logger("###Not video or home window###", 2)
                self.waitForAbort(2)
                continue
            if self.get_visibility("Container.Scrolling"):
                # logger("###container is scrolling###", 2)
                self.waitForAbort(0.2)
                continue
            imdb_id = self.get_infolabel("ListItem.IMDBNumber")
            tmdb_rating = self.get_infolabel("ListItem.Rating")
            set_property = self.window(self.get_window_id()).setProperty
            get_property = self.window(self.get_window_id()).getProperty
            cached_ratings = get_property(f"fentastic.cachedRatings.{imdb_id}")
            if not imdb_id or not imdb_id.startswith("tt"):
                for k, v in empty_ratings.items():
                    set_property("fentastic.%s" % k, v)
                # logger("###no valid imdb_id###", 2)
                self.waitForAbort(0.2)
                continue
            if cached_ratings:
                # logger(
                #     f"###Fetched window property cached ratings for {imdb_id}: {cached_ratings}###",
                #     2,
                # )
                result = json.loads(cached_ratings)
                for k, v in result.items():
                    set_property("fentastic.%s" % k, v)
                # logger(f"###Using window property cached ratings for {imdb_id}###", 2)
                self.waitForAbort(0.2)
                continue
            # self.current_imdb_id = imdb_id
            Thread(
                target=self.set_ratings, args=(api_key, imdb_id, tmdb_rating)
            ).start()
            self.waitForAbort(0.2)

    def set_ratings(self, api_key, imdb_id, tmdb_rating):
        set_property = self.window(self.get_window_id()).setProperty
        result = self.omdb_api().fetch_info({"imdb_id": imdb_id}, api_key, tmdb_rating)
        if result:
            set_property(f"fentastic.cachedRatings.{imdb_id}", json.dumps(result))
            # logger(f"###Stored ratings in window property cache for {imdb_id}###", 2)
            for k, v in result.items():
                set_property("fentastic.%s" % k, v)
                # logger("###Set window property cache fentastic.%s to %s###" % (k, v), 2)


xbmc.log("RatingsService Started", 2)
RatingsService().listitem_monitor()
xbmc.log("RatingsService Finished", 2)
