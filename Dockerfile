FROM python:3
MAINTAINER Chris Conner chrism.conner@gmail.com

#Install requests, flask and supervisor
RUN pip install requests
RUN pip install paho-mqtt
RUN apt-get update && apt-get install -y supervisor
RUN apt-get install -y libmariadb-dev libmariadb-dev-compat && pip3 install mysqlclient

#Make log dir for supervisor
RUN mkdir -p /var/log/supervisor

#Copy supervisor conf and app
COPY mqtt-to-mysql-supervisord.conf /etc/supervisor/conf.d/mqtt-to-mysql-supervisord.conf
COPY app.py /app.py

#Environment variables
ENV MQTTPORT 1883
ENV MQTTHOST localhost
ENV MQTTUSER user
ENV MQTTPASS pass
ENV MQTTTOPIC testtopic
ENV MQTTCAFILE None
ENV DBHOST localhost
ENV DBPORT 3306
ENV DBUSER user
ENV DBPASS pass
ENV DEBUG FALSE

#Expose ports

CMD ["/usr/bin/supervisord"]
