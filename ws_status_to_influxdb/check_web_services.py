import urllib3
import time
import ssl
import sys

from influxdb import InfluxDBClient

from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from requests.exceptions import ConnectTimeout, ConnectionError
from urllib3.exceptions import MaxRetryError

from ws_status_to_influxdb.config import config
from ws_status_to_influxdb.common import log


class WebServiceStatusToInfluxDB:

    def __init__(self):
        self.influxdb_client = self._get_influx_connection()

    def run(self):
        while True:
            self.check_services()
            log.info('Waiting {} seconds until next test'.format(config.delay))
            time.sleep(config.delay)

    def check_services(self):
        """
        Check each service and send the data to influxDB
        """
        if not config.services:
            log.error("No services defined in config file!")
            sys.exit(1)

        results = [{"service": service, "status": self.check_single_service(service, url)}
                   for service, url in config.services.items()]

        self.send_results(results)
        log.info("Data written to influxDB.")

    @staticmethod
    def check_single_service(service, url):
        """
        Check single service if up and running
        :param service: <string> Name to check for service
        :param url: <string> URL to check for service
        :return: <string> with status
        """
        log.debug("Checking {} status on {}".format(service, url))

        if config.verify_ssl:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE
            urllib3.disable_warnings()

        http = urllib3.PoolManager(cert_reqs=cert_reqs)
        try:
            status = 1 if http.request('GET', url).status == 200 else 0
        except MaxRetryError:
            status = 0

        log.info("Status for {} is: {}".format(service, status))
        return status

    # InfluxDB stuff

    def send_results(self, results):
        """
        Send the service:status to influxDB
        :param results: <list> with results
        :return: None
        """
        input_points = [{'measurement': result['service'],
                         'fields': {'status': result['status']}} for result in results]
        log.debug("InfluxDB input points: {}".format(input_points))
        self._write_data_to_influxdb(input_points)

    def _write_data_to_influxdb(self, json_data):
        """
        Writes the provided JSON to the database
        :param json_data: <dict> json data to write to influx DB
        :return: None
        """
        log.debug(json_data)

        try:
            self.influxdb_client.write_points(json_data)
        except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as e:
            if hasattr(e, 'code') and e.code == 404:
                log.error('Database %s Does Not Exist.  Attempting To Create',
                          config.influxdb_database)
                self.influxdb_client.create_database(config.influxdb_database)
                self.influxdb_client.write_points(json_data)
                return

            log.error('Failed To Write To InfluxDB: {}'.format(e))

    @staticmethod
    def _get_influx_connection():
        """
        Create an InfluxDB connection and test to make sure it works.
        We test with the get all users command.  If the address is bad it fails
        with a 404.  If the user doesn't have permission it fails with 401
        :return: <objcet> InfluxDBClient object
        """

        influx = InfluxDBClient(
            config.influxdb_address,
            config.influxdb_port,
            database=config.influxdb_database,
            ssl=config.influxdb_ssl,
            verify_ssl=config.influxdb_verify_ssl,
            username=config.influxdb_user,
            password=config.influxdb_password,
            timeout=5
        )
        try:
            log.debug('Testing connection to InfluxDb using provided credentials')
            influx.get_list_users()
            log.debug('Successful connection to InfluxDb')
        except (ConnectTimeout, InfluxDBClientError, ConnectionError) as e:
            if isinstance(e, ConnectTimeout):
                log.critical('Unable to connect to InfluxDB at the provided address '
                             '({})'.format("config.influxdb_address"))
            elif e.code == 401:
                log.critical('Unable to connect to InfluxDB with provided credentials')
            else:
                log.critical('Failed to connect to InfluxDB for unknown reason')

            sys.exit(1)

        return influx
