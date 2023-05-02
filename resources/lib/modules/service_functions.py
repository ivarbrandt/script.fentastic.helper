# -*- coding: utf-8 -*-
import xbmc, xbmcgui
from modules.cpath_maker import CPaths, files_get_directory
from modules.logger import logger

window, get_infolabel, getCurrentWindowId = xbmcgui.Window(10000), xbmc.getInfoLabel, xbmcgui.getCurrentWindowId
info_label, info_folderpath, label_prop, path_prop, stacked_prop = 'ListItem.Label', 'ListItem.FolderPath', 'FENtastic.%s.label', 'FENtastic.%s.path', 'FENtastic_stacked_list_id'
not_home_wait, home_wait = 2.0, 0.75

def starting_widgets():
	for item in ('movie.widget', 'tvshow.widget'):
		try:
			active_cpaths = CPaths(item).fetch_current_cpaths()
			if not active_cpaths: continue
			widget_type = item.split('.')[0]
			for count in range(1,11):
				active_widget = active_cpaths.get(count, {})
				if not active_widget: continue
				if not 'Stacked' in active_widget['cpath_label']: continue
				cpath_setting = active_widget['cpath_setting']
				if not cpath_setting: continue
				try: widget_number = cpath_setting.split('.')[2]
				except: continue
				list_id = '%s01%s' % ('7' if widget_type == 'movie' else '8', widget_number)
				first_item = files_get_directory(active_widget['cpath_path'])[0]
				if not first_item: continue
				cpath_label, cpath_path = first_item['label'], first_item['file']
				window.setProperty(label_prop % list_id, cpath_label)
				window.setProperty(path_prop % list_id, cpath_path)
		except: pass

def widget_monitor():
	monitor = xbmc.Monitor()
	abort_requested = monitor.abortRequested
	while not abort_requested():
		while getCurrentWindowId() != 10000: monitor.waitForAbort(not_home_wait)
		list_id = window.getProperty(stacked_prop)
		cpath_label, cpath_path = get_infolabel(info_label), get_infolabel(info_folderpath)
		monitor.waitForAbort(home_wait)
		if '' in (list_id, cpath_label, cpath_path) or len(list_id) != 4 or get_infolabel(info_folderpath) != cpath_path: continue
		window.setProperty(label_prop % list_id, cpath_label)
		window.setProperty(path_prop % list_id, cpath_path)
		window.getControl(int(list_id + '1')).selectItem(0)
	try: del monitor
	except: pass