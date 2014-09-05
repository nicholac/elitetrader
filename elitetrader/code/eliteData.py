'''
Created on 29 Aug 2014

@author: dusted-ipro
'''


import zlib
import zmq
# You can substitute the stdlib's json module, if that suits your fancy
import simplejson
from pymongo import MongoClient
#import matplotlib.pyplot as plt
from datetime import datetime

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    client = MongoClient()
    db = client.mydb
    coll = db.emd
    #load in the system data
    systems = []
    fh = open(r'/Users/dusted-ipro/Documents/elitesystems.txt', 'r')
    for line in fh.readlines():
        out = line.rstrip('\n').split(',')
        systems.append(out)

    # Connect to the first publicly available relay.
    subscriber.connect('tcp://firehose.elite-market-data.net:9500')
    # Disable filtering.
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    i = 0
    #while True:
    while i<1000000:
        # Receive raw market JSON strings.
        market_json = zlib.decompress(subscriber.recv())
        # Un-serialize the JSON data to a Python dict.
        market_data = simplejson.loads(market_json)
        # Dump the market data to stdout. Or, you know, do more fun
        # things here.
        #print market_data
        #fh.write(market_data)
        #pid = coll.insert(market_data)
        #Search for a matching system name
        data = dict(market_data)
        #print data['message']['stationName'][0:data['message']['stationName'].find(' (')]
        #Loop through and find a matching system
        for sys in systems:
            if data['message']['stationName'][0:data['message']['stationName'].find(' (')] == sys[0]:
                data['system'] = {'name':sys[0], 'coordX':float(sys[1]), 'coordY':float(sys[2]), 'coordZ':float(sys[3])}
                #print 'Matched'
                break
        #make a real date
        s = data['message']['timestamp']
        dt = datetime.strptime(s[0:19], "%Y-%m-%dT%H:%M:%S")
        data['message']['realDate'] = dt
        pid = coll.insert(data)
        i+=1
        #coll.update({'_id':pid},{"$set":{"systemName":sysName, "coordX":x, "coordY":y, "coordZ":z}})
        print i
    client.disconnect()

if __name__ == '__main__':
    main()