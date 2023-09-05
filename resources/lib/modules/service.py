import xbmc


def ratings_service():
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        from modules.OMDb import test_api

        test_api()
        if monitor.waitForAbort(1):
            break
