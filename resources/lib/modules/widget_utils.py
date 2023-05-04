# -*- coding: utf-8 -*-
import xbmc, xbmcgui
# from modules.logger import logger

info_label, info_folderpath, label_prop, path_prop, list_check = 'ListItem.Label', 'ListItem.FolderPath', 'fentastic.%s.label', 'fentastic.%s.path', ('19', '22')
short_wait, long_wait = 0.75, 2.0

info_label, info_folderpath, active_modal = 'ListItem.Label', 'ListItem.FolderPath', 'System.HasActiveModalDialog'
label_prop, path_prop, list_check = 'fentastic.%s.label', 'fentastic.%s.path', ('19', '22')
short_wait, long_wait = 0.75, 2.0

def starting_widgets():
	window = xbmcgui.Window(10000)
	window.setProperty('fentastic.starting_widgets', 'finished')
	from modules.cpath_maker import CPaths, files_get_directory
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
				list_id = '%s01%s' % ('19' if widget_type == 'movie' else '22', widget_number)
				try: first_item = files_get_directory(active_widget['cpath_path'])[0]
				except: continue
				if not first_item: continue
				cpath_label, cpath_path = first_item['label'], first_item['file']
				window.setProperty(label_prop % list_id, cpath_label)
				window.setProperty(path_prop % list_id, cpath_path)
		except: pass
	try: del window
	except: pass

def widget_monitor():
	window = xbmcgui.Window(10000)
	if not window.getProperty('fentastic.widget_monitor_running') == 'true':
		window.setProperty('fentastic.widget_monitor_running', 'true')
		monitor = xbmc.Monitor()
		abort_requested, wait_for_abort = monitor.abortRequested, monitor.waitForAbort
		while window.getProperty('fentastic.widget_monitor') == 'true' and not abort_requested():
			list_id = str(window.getFocusId())
			cpath_label, cpath_path = xbmc.getInfoLabel(info_label), xbmc.getInfoLabel(info_folderpath)
			wait_for_abort(short_wait)
			if xbmc.getCondVisibility(active_modal): continue
			if len(list_id) != 5 or list_id != str(window.getFocusId()) or xbmc.getInfoLabel(info_folderpath) != cpath_path: continue
			window.setProperty(label_prop % list_id, cpath_label)
			window.setProperty(path_prop % list_id, cpath_path)
			try: window.getControl(int(list_id + '1')).selectItem(0)
			except: pass
		try: del monitor
		except: pass
		window.setProperty('fentastic.widget_monitor_running', 'false')
	try: del window
	except: pass