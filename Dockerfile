FROM python:alpine
MAINTAINER Husdup Florin <husdup.florin@gmail.com>

VOLUME /src/
COPY ws_status_to_influxdb.py requirements.txt config.ini /src/
ADD ws_status_to_influxdb /src/ws_status_to_influxdb
WORKDIR /src

RUN pip install -r requirements.txt

CMD ["python", "-u", "/src/ws_status_to_influxdb.py"]
