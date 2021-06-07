**Check status of list of web services and send them to influxDB**
------------------------------

![Screenshot](https://i.imgur.com/CrBLyhC.png)


This tool does a simple check to see if a web service is accessible on the provided URL and sends the status to influxDB 
You can see an example dashboard on how this can look in Grafana.

## Configuration within config.ini

```text
[GENERAL]
Delay      = <delay between runs, in seconds>
Verify_SSL = <defaults to false, so it won't throw erros if you have slef signed ceritificates>
```

```text
[INFLUXDB]
Address   = <influxDB server address. Hostname or IP>
Port      = <influxDB port to connect to.  8086 in most cases>
Database  = <database to write collected stats to. If does not exists, it will be created>
Username  = <user that has access to the database>
Password  = <password for above user>
```
```text
[SERVICES]
# Specify as many services you want as key = value pair. Some examples below:
Plex = http://10.13.14.200:32400/web
Heimdall = http://10.13.14.200:8080
Nextcloud = https://10.13.14.200:5443
Duplicati = http://10.13.14.200:8200
Portainer = http://10.13.14.200:9000
```

```text
[LOGGING]
# Valid Options: critical, error, warning, info, debug
Level = info
```

## Usage withour docker

> Make sure you run it with Python 3.8

1. Before you can run it you need to install the required packages run:
- `pip3 install -r requirements.txt`

2. Enter your desired information in `config.ini` file

3. Run ` python3 ws_status_to_influxdb.py`

**Can I use a custom configuration file name?**

If you want to use a config file by a different name set an ENV Variable called `ws_status_to_influxdb`.  The value you set will be the config file that's used. 
  
## Usage with docker


1. Make a directory to hold the config.ini file. Navigate to that directory and download the sample config.ini from this repo.
```bash
mkdir ws_status_to_influxdb
curl -o ws_status_to_influxdb/config.ini https://raw.githubusercontent.com/husdupflorin/web_service_status_to_influxdb/master/config.ini
cd ws_status_to_influxdb
```

2. Modify the config as per your needs
```bash
vi config.ini
```

3. Run the container, pointing to the directory with the config file. This should now pull the image from Docker hub.
 ```bash
docker run -d \
--name="service_checker_influxdb" \
-v /root/web_service_status_to_influxdb/config.ini:/src/config.ini \
--restart="always" \
husdupflorin/web_service_status_to_influxdb
```

### Example query in Grafana:

> Now that we have the data in infuxDB, we can configure our grafana dashboard! You can import `example.json` dashboard file for a starting point.

Using this query you'll get the status for the `heimdall` service:

-   `SELECT "status" FROM "heimdall" WHERE $timeFilter`

In the grafana dashboard it should be used with a `stat` panel with the following settings:
-   thesholds: `0 - red` / `1 - green`
-   value mapping: `0: DOWN` / `1:UP`

![Screenshot](https://i.imgur.com/YU5lwjy.png)