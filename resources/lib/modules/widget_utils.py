# -*- coding: utf-8 -*-
import xbmc, xbmcgui
# from modules.logger import logger

def widget_monitor(list_id):
	if len(list_id) != 5: return
	monitor, window = xbmc.Monitor(), xbmcgui.Window(10000)
	while list_id == str(window.getFocusId()) and not monitor.abortRequested():
		cpath_label, cpath_path = xbmc.getInfoLabel('ListItem.Label'), xbmc.getInfoLabel('ListItem.FolderPath')
		monitor.waitForAbort(0.75)
		if xbmc.getInfoLabel('ListItem.FolderPath') != cpath_path or xbmc.getCondVisibility('System.HasActiveModalDialog'): continue
		window.setProperty('fentastic.%s.label' % list_id, cpath_label)
		window.setProperty('fentastic.%s.path' % list_id, cpath_path)
		try: window.getControl(int(list_id + '1')).selectItem(0)
		except: pass
	try: del monitor
	except: pass
	try: del window
	except: pass