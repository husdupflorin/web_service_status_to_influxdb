import os

from ws_status_to_influxdb.config.configmanager import ConfigManager

if os.getenv('ws_status_to_influxdb'):
    config = os.getenv('ws_status_to_influxdb')
else:
    config = 'config.ini'

config = ConfigManager(config)
