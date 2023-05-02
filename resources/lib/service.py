# -*- coding: utf-8 -*-
from modules import service_functions
from modules.logger import logger


logger('FENtasticHelper', 'Service Starting')
service_functions.starting_widgets()
service_functions.widget_monitor()
logger('FENtasticHelper', 'Service Finished')
