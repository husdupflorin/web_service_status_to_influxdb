import argparse

from ws_status_to_influxdb.check_web_services import WebServiceStatusToInfluxDB

parser = argparse.ArgumentParser(description="A tool that checks the services you want and sends "
                                             "thir status to InfluxDB")
args = parser.parse_args()
collector = WebServiceStatusToInfluxDB()
collector.run()
