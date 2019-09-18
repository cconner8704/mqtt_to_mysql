#!/usr/bin/env python
import json
import argparse
import sys
import logging
import MySQLdb
import paho.mqtt.client as mqttClient
import time
import ssl

class Database:
    def __init__(self, host="localhost", user="root", password=None, db=None):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.conn = MySQLdb.connect(self.host, self.user, self.password, self.db)
        try:
            if (self.conn):
                status = "DB init success"
            else:
                status = "DB init failed"
            self.conn.autocommit(True)
            self.cursor = self.conn.cursor()
            logging.info("%s" % status)
        except Exception as e:
            status = "DB init fail %s " % str(e)
            logging.info("%s" % status)

    def reconnect(self)
        self.conn = MySQLdb.connect(self.host, self.user, self.password, self.db)
        try:
            if (self.conn):
                status = "DB reconnect success"
            else:
                status = "DB reconnect failed"
            self.conn.autocommit(True)
            self.cursor = self.conn.cursor()
            logging.info("%s" % status)
        except Exception as e:
            status = "DB reconnect fail %s " % str(e)
            logging.info("%s" % status)


    def insert(self, query):
        try:
            if self.conn is None:
                self.__init__()
            else:
                self.conn.ping(True)
                logging.info("%s" % query)
                self.cursor.execute(query)
        except MySQLdb.OperationalError:
            self.reconnect()
            logging.info("%s" % query)
            self.cursor.execute(query)
        except Exception as e:
            logging.exception("Insert Failed: %s" % e)
            self.conn.rollback()


    def query(self, query):
        try:
            if self.conn is None:
                self.__init__()
            else:
                self.conn.ping(True)
                logging.info("%s" % query)
                self.cursor.execute(query)
        except MySQLdb.OperationalError:
            self.reconnect()
            logging.info("%s" % query)
            self.cursor.execute(query)
        except Exception as e:
            logging.exception("Query Failed: %s" % e)
            self.conn.rollback()
            return False

        return self.cursor.fetchall()


    def __del__(self):
        self.connection.close()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to broker")
        global Connected 
        Connected = True
    else:
        logging.exception("Broker connection failed")

def on_message(client, userdata, message):
   global db
   query = """ %s """ % message.payload.decode()
   logging.debug("Message Recieved running insert: %s" % query)
   db.insert(query)

Connected = False

parser = argparse.ArgumentParser()

parser.add_argument('-P', '--mqttport', action='store', dest='mqttport',
                    default=1883, help='Port for MQTT')

parser.add_argument('-H', '--mqtthost', action='store', dest='mqtthost',
                    default="localhost", help='Host for MQTT')

parser.add_argument('-U', '--mqttuser', action='store', dest='mqttuser',
                    default="user", help='User for MQTT')

parser.add_argument('-W', '--mqttpass', action='store', dest='mqttpass',
                    default="pass", help='Password for MQTT')

parser.add_argument('-T', '--mqtttopic', action='store', dest='mqtttopic',
                    default="testtopic", help='Subscription Topic for MQTT')

parser.add_argument('-c', '--mqttcafile', action='store', dest='mqttcafile',
                    default=None, help='CA File for TLS for MQTT')

parser.add_argument('-d', '--dbhost', action='store', dest='dbhost',
                    default="localhost", help='Host for DB')

parser.add_argument('-p', '--dbport', action='store', dest='dbport',
                    default=3306, help='Port for DB')

parser.add_argument('-u', '--dbuser', action='store', dest='dbuser',
                    default="user", help='User for DB')

parser.add_argument('-w', '--dbpass', action='store', dest='dbpass',
                    default="password", help='Password for DB')

parser.add_argument('-v', '--verbose', action="store", dest='verbose',
                    default="FALSE", help='Enable debug logging')

args = parser.parse_args()

if args.verbose != "FALSE":
    logging_level=logging.DEBUG
    app_debug=True
else:
    logging_level=logging.INFO
    app_debug=False

logging.basicConfig(stream=sys.stdout, level=logging_level)

try:
  logging.debug("dbhost: %s" % args.dbhost)
  logging.debug("dbuser: %s" % args.dbuser)
  logging.debug("dbport: %s" % args.dbport)
  logging.debug("dbpass: %s" % args.dbpass)
  db = Database(host = args.dbhost, user = args.dbuser, password = args.dbpass, db = "mysql")
except Exception as e:
  logging.exception("Failed to connect to database: %s" % e)
  sys.exit(1)


broker_address = args.mqtthost
port = args.mqttport
user = args.mqttuser
password = args.mqttpass
topic = args.mqtttopic
cafile = args.mqttcafile
logging.debug("broker_address: %s" % broker_address)
logging.debug("port: %s" % port)
logging.debug("password: %s" % password)
logging.debug("topic: %s" % topic)
logging.debug("cafile: %s" % cafile)

client = mqttClient.Client(client_id="PythonMysqlApp%s" % topic, clean_session=True)
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message
if cafile is not None and cafile != "None":
  client.tls_set(cafile, tls_version=ssl.PROTOCOL_TLSv1_2)
  client.tls_insecure_set(True)

client.connect(broker_address, port=int(port))

client.subscribe(topic, qos=2)
try:
  client.loop_forever()
except KeyboardInterrupt:
  client.disconnect()
  sys.exit(1)

