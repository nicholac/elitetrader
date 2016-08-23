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
from py2neo import neo4j, node, rel

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    client = MongoClient()
    db = client.mydb
    coll = db.emd
    #load in the system data
    systems = []
    fh = open(r'elitesystems.txt', 'r')
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

def neoLoad():
    '''Loads systems data  from mongo to Neo
    delete all neo data:
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r

    alice, bob, rel = graph_db.create(
    {"name": "Alice"}, {"name": "Bob"},
    (0, "KNOWS", 1, {"since": 2006})
    )

    query = neo4j.CypherQuery(graph_db, qs)
    results = query.execute(name='Rahul')
    print results

    #Create an index
    index = graph_db.get_or_create_index(neo4j.Node, "index_name")
    #Create a new node
    new_node = batch.create(node({"key":"value"}))
    #Add it to the index
    batch.add_indexed_node(index, "key", "value", new_node)
    #Find our node like this
    new_node_ref = index.get("key", "value")
    '''
    #Init mongo
    client = MongoClient()
    db = client.mydb
    coll = db.emd_dists

    #Init the neo db
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    #Get the data from mongo
    data = coll.find()
    nodeCnt1 = 0
    nodeCnt2 = 1
    sysNodes = []
    #Firstly build all system nodes & store in a dictionary for later use
    s = coll.find_one()
    systemNames = []
    for system in s['toSys']:
        #sysNode = graph_db.create(node({"sysName": system}))
        qs = 'CREATE (n:system { name : {name} })'
        query = neo4j.CypherQuery(graph_db, qs)
        results = query.execute(name=system)
        #append our system names
        systemNames.append(system)

    #Now run through systems, query neo for fromNode, query mongo for system dests and insert relationship
    for sys in systemNames:
        print 'Doing: '+sys
        #Neo Query
        q ='MATCH (m:system {name:\"'+sys+'\"}) RETURN (m)'
        query = neo4j.CypherQuery(graph_db, q)
        neoOut = query.execute()
        fromSysNode = neoOut.data[0][0]
        #Mongo Query
        data = coll.find({'fromSys':sys})
        toSysDists = data.next()
        #Loop through the connections and build relationships
        for toSys in toSysDists['toSys'].items():
            print 'Building: '+toSys[0]
            #get the to node
            q ='MATCH (m:system {name:\"'+toSys[0]+'\"}) RETURN (m)'
            query = neo4j.CypherQuery(graph_db, q)
            neoOut = query.execute()
            toSysNode = neoOut.data[0][0]
            #Make relationship
            r = graph_db.create(rel(fromSysNode, 'jump', toSysNode, {'range':toSys[1]}))

    print 'Done'

    client.disconnect()
    del graph_db

    return



if __name__ == '__main__':
    #main()
    neoLoad()
