import configparser
import os


class ConfigManager:

    def __init__(self, config):
        """
        Configuration file manager
        :param config: <string> patch to the config file.
        """
        config_file = os.path.join(os.getcwd(), config)
        if os.path.isfile(config_file):
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
        else:
            raise ValueError('ERROR: Unable to load config file: {}'.format(config_file))

        self._load_config_values()

    def _load_config_values(self):

        # General
        self.delay = self.config['GENERAL'].getint('Delay', fallback=30)
        self.verify_ssl = self.config['GENERAL'].getboolean("Verify_SSL", fallback=False)

        # InfluxDB
        self.influxdb_address = self.config['INFLUXDB']['Address']
        self.influxdb_port = self.config['INFLUXDB'].getint('Port', fallback=8086)
        self.influxdb_database = self.config['INFLUXDB'].get('Database', fallback='servicestatus')
        self.influxdb_user = self.config['INFLUXDB'].get('Username', fallback='')
        self.influxdb_password = self.config['INFLUXDB'].get('Password', fallback='')
        self.influxdb_ssl = self.config['INFLUXDB'].getboolean('SSL', fallback=False)
        self.influxdb_verify_ssl = self.config['INFLUXDB'].getboolean('Verify_SSL', fallback=True)

        # Logging
        self.logging_level = self.config['LOGGING'].get('Level', fallback='debug')
        self.logging_level = self.logging_level.upper()

        # Services
        self.services = dict(self.config.items('SERVICES'))
