#!/usr/bin/python
import socket
import json
import sys
import requests

def my_help():
    print("\
         ./kafka_consumers.py discovery - use for discovery consumers and partitions\n\
         ./kafka_consumers.py consumer_status {#CONSUMER}\n\
         ./kafka_consumers.py consumer_tottallag {#CONSUMER}\n\
         ./kafka_consumers.py consumer_offsets {#CONSUMER} start|end {#PARTITION} {#TOPIC}\n\
         ./kafka_consumers.py consumer_offsets_partition_status  {#CONSUMER} {#PARTITION} {#TOPIC}\n\
         ./kafka_consumers.py consumer_offsets_partition_current_lag {#CONSUMER} {#PARTITION} {#TOPIC}\n\
         ./kafka_consumers.py consumer_lag {#CONSUMER} start|end {#PARTITION} {#TOPIC}")

host1 = socket.gethostbyname(socket.gethostname())
url = ('http://'+host1+':8000/v3/kafka/local/consumer/')
Dict = {'NOTFOUND': 0, 'OK': 1, 'WARN': 2, 'ERR': 3, 'STOP': 4, 'STALL': 5}
if len(sys.argv) <= 1:
    my_help()
else:
    try:
        if sys.argv[1] == "discovery":
            r = requests.get(url)
            python_obj = r.json()
            result = {}
            result["data"] = []
            for consumers in python_obj["consumers"]:
                r1 = requests.get(url+consumers+'/lag')
                if r1.json()["status"]["group"] == consumers:
                   #print(r1.json()["status"]["group"])
                   for p in r1.json()["status"]["partitions"]:
                    result["data"].append({
                       "{#CONSUMER}": consumers,
                       "{#PARTITION}": p["partition"],
                       "{#TOPIC}": p["topic"]
                    })
                else:
                   print("Issues")
            json_data = json.dumps(result)
            print(json_data)
        elif sys.argv[1] == "discovery_consumers":
            r = requests.get(url)
            python_obj = r.json()
            result = {}
            result["data"] = []
            for consumers in python_obj["consumers"]:
                result["data"].append({
                  "{#CONSUMER}": consumers
                })
            json_data = json.dumps(result)
            print(json_data)
        elif sys.argv[1] == "consumer_status" and len(sys.argv) == 3:
            r1 = requests.get(url+sys.argv[2]+'/status')
            print(Dict.get(r1.json()["status"]["status"]))
        elif sys.argv[1] == "consumer_tottallag" and len(sys.argv) == 3:
            r1 = requests.get(url+sys.argv[2]+'/status')
            print(r1.json()["status"]["totallag"])
        elif sys.argv[1] == "consumer_offsets" and len(sys.argv) == 6:
            r1 = requests.get(url+sys.argv[2]+'/lag')
            for p in r1.json()["status"]["partitions"]:
                if p["partition"] == int(sys.argv[4]) and p["topic"] == sys.argv[5]:
                    lag_status = p[sys.argv[3]]
                    print(lag_status["offset"])
        elif sys.argv[1] == "consumer_lag" and len(sys.argv) == 6:
            r1 = requests.get(url+sys.argv[2]+'/lag')
            for p in r1.json()["status"]["partitions"]:
                if p["partition"] == int(sys.argv[4]) and p["topic"] == sys.argv[5] and p[sys.argv[3]] != None:
                    lag_status = p[sys.argv[3]]
                    print(lag_status["lag"])
        elif sys.argv[1] == "consumer_offsets_partition_status" and len(sys.argv) == 5:
            r1 = requests.get(url+sys.argv[2]+'/lag')
            for p in r1.json()["status"]["partitions"]:
                if p["partition"] == int(sys.argv[3]) and p["topic"] == sys.argv[4]:
                    print(Dict.get(p["status"]))
        elif sys.argv[1] == "consumer_offsets_partition_current_lag" and len(sys.argv) == 5:
            r1 = requests.get(url+sys.argv[2]+'/lag')
            for p in r1.json()["status"]["partitions"]:
                if p["partition"] == int(sys.argv[3]) and p["topic"] == sys.argv[4]:
                    print((p["current_lag"]))
        else:
            my_help()
    except ValueError:
        my_help()