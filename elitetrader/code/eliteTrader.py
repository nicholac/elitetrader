'''
Created on 25 Aug 2014

@author: dusted-ipro
'''

'''
Distances between systems:
26 Draconis,-39.000000,24.906250,-0.656250
Acihaut,-18.500000,25.281250,-4.000000
Aganippe,-11.562500,43.812500,11.625000
Asellus Primus,-23.937500,40.875000,-1.343750
Aulin,-19.687500,32.687500,4.750000
Aulis,-16.468750,44.187500,-11.437500
BD+47 2112,-14.781250,33.468750,-0.406250
BD+55 1519,-16.937500,44.718750,-16.593750
Bolg,-7.906250,34.718750,2.125000
Chi Herculis,-30.750000,39.718750,12.781250
CM Draco,-35.687500,30.937500,2.156250
Dahan,-19.750000,41.781250,-3.187500
DN Draconis,-27.093750,21.625000,0.781250
DP Draconis,-17.500000,25.968750,-11.375000
Eranin,-22.843750,36.531250,-1.187500
G 239-25,-22.687500,25.812500,-6.687500
GD 319,-19.375000,43.625000,-12.750000
h Draconis,-39.843750,29.562500,-3.906250
Hermitage,-28.750000,25.000000,10.437500
i Bootis,-22.375000,34.843750,4.000000
Ithaca,-8.093750,44.937500,-9.281250
Keries,-18.906250,27.218750,12.593750
Lalande 29917,-26.531250,22.156250,-4.562500
LFT 1361,-38.781250,24.718750,-0.500000
LFT 880,-22.812500,31.406250,-18.343750
LFT 992,-7.562500,42.593750,0.687500
LHS 2819,-30.500000,38.562500,-13.437500
LHS 2884,-22.000000,48.406250,1.781250
LHS 2887,-7.343750,26.781250,5.718750
LHS 3006,-21.968750,29.093750,-1.718750
LHS 3262,-24.125000,18.843750,4.906250
LHS 417,-18.312500,18.187500,4.906250
LHS 5287,-36.406250,48.187500,-0.781250
LHS 6309,-33.562500,33.125000,13.468750
LP 271-25,-10.468750,31.843750,7.312500
LP 275-68,-23.343750,25.062500,15.187500
LP 64-194,-21.656250,32.218750,-16.218750
LP 98-132,-26.781250,37.031250,-4.593750
Magec,-32.875000,36.156250,15.500000
Meliae,-17.312500,49.531250,-1.687500
Morgor,-15.250000,39.531250,-2.250000
Nang Ta-khian,-18.218750,26.562500,-6.343750
Naraka,-34.093750,26.218750,-5.531250
Opala,-25.500000,35.250000,9.281250
Ovid,-28.062500,35.156250,14.812500
Pi-fang,-34.656250,22.843750,-4.593750
Rakapila,-14.906250,33.625000,9.125000
Ross 1015,-6.093750,29.468750,3.031250
Ross 1051,-37.218750,44.500000,-5.062500
Ross 1057,-32.312500,26.187500,-12.437500
Styx,-24.312500,37.750000,6.031250
Surya,-38.468750,39.250000,5.406250
Tilian,-21.531250,22.312500,10.125000
WISE 1647+5632,-21.593750,17.718750,1.750000
Wyrd,-11.625000,31.531250,-3.937500
'''

"""
'''
Example mongo aggregation:
which station has the greatest demand level?
db.emd.aggregate([{$match:{type:"marketquote"}},{$group:{_id:"$message.stationName",total:{$sum:"$message.demandLevel"}}},{$sort:{total:-1}}])


Which station has the highest total sell prices - normalised for count of messages containing that station:
db.emd.aggregate([{$match:{type:"marketquote"}},{$group:{_id:"$message.stationName",total:{$sum:"$message.sellPrice"}, totalStats:{$sum:1}}},{$project:{_id:1, normed:{$divide:["$total","$totalStats"]}}},{$sort:{normed:-1}}])

In that station, which item has the highest sell price, normalised for message count:
db.emd.aggregate([{$match:{"message.stationName":"LHS 417 (Gernhardt Camp)"}},{$group:{_id:"$message.itemName",total:{$sum:"$message.sellPrice"}, totalStats:{$sum:1}}},{$project:{_id:1, normed:{$divide:["$total","$totalStats"]}}},{$sort:{normed:-1}}])

So which station has the lowest buy price for this commodity?
db.emd.aggregate([{$match:{"message.itemName":"palladium"}},{$group:{_id:"$message.stationName", total:{$sum:"$message.buyPrice"},totalStats:{$sum:1}}},{$project:{_id:1, normed:{$divide:["$total","$totalStats"]}}},{$sort:{normed:1}}])

Find most traded commodity:
db.emd.aggregate([{$match:{"type":"marketquote"}},{$group:{_id:"$message.itemName",total:{$sum:1}}},{$sort:{total:-1}}])
'''


Example Python EMDR client.
"""
import zlib
import zmq
# You can substitute the stdlib's json module, if that suits your fancy
import simplejson
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
from operator import itemgetter
from math import sqrt
'''
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
        print data['message']['stationName'][0:data['message']['stationName'].find(' (')]
        #Loop through and find a matching system
        for sys in systems:
            if data['message']['stationName'][0:data['message']['stationName'].find(' (')] == sys[0]:
                data['system'] = {'name':sys[0], 'coordX':float(sys[1]), 'coordY':float(sys[2]), 'coordZ':float(sys[3])}
                print 'Matched'
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
'''

def silverTrade():
    client = MongoClient()
    db = client.mydb
    coll = db.emd
    #Find the systems with the highest sell price for silver - across entire dataset
    #db.emd.aggregate([{$match:{"message.itemName":"silver"}},
    #{$group:{_id:"$message.stationName",totalsellprice:{$sum:"$message.sellPrice"}, totalHits:{$sum:1}}},
    #{$project:{_id:1, avgSell:{$divide:["$totalsellprice","$totalHits"]}}},
    #{$sort:{avgSell:-1}}])
    out = coll.aggregate([{"$match":{"message.itemName":"silver", "message.sellPrice":{"$gt":0}}},
                          {"$group":{"_id":"$message.stationName","totalsellprice":{"$sum":"$message.sellPrice"}, "totalHits":{"$sum":1}}},
                          {"$project":{"_id":1, "avgSell":{"$divide":["$totalsellprice","$totalHits"]}}},
                          {"$sort":{"avgSell":-1}}])

    #get system name and sell price for highest
    highSysName = out['result'][0]['_id']
    highSellPrice = out['result'][0]['avgSell']

    #Now get average buy prices for silver in all systems - sort by lowest first
    out = coll.aggregate([{"$match":{"message.itemName":"silver", "message.buyPrice":{"$gt":0}}},
      {"$group":{"_id":"$message.stationName","totalbuyprice":{"$sum":"$message.buyPrice"}, "totalHits":{"$sum":1}}},
      {"$project":{"_id":1, "avgBuy":{"$divide":["$totalbuyprice","$totalHits"]}}},
      {"$sort":{"avgSell":-1}}])

    #Print out price differential (profit) between each before distance weighting
    for res in out['result']:
        profit = highSellPrice-res['avgBuy']
        print 'From:' +highSysName+' To:' + res['_id'] + ' Profit:'+str(profit)
    client.disconnect()

def computeDistMatrix():
    '''Computes distance between systems and stores in mongo
    Really this should be a mongo job
    '''
    client = MongoClient()
    db = client.mydb
    coll = db.emd_dists
    out = []
    mat = {}
    #out data: {fromsys:'',
    #            tosys:{draconis:222.567,
    #                    ibootis:666.543,
    #                    }
    #            }
    #load in the system data
    systems = []
    fh = open(r'/Users/dusted-ipro/Documents/elitesystems.txt', 'r')
    for line in fh.readlines():
        out = line.rstrip('\n').split(',')
        systems.append(out)
    fh.close()
    #print systems
    for sys in systems:
        #calc distance from this sys to every other one
        mat['fromSys']=sys[0]
        mat['toSys']={}
        for thisSys in systems:
            d = distance(float(sys[1]), float(sys[2]), float(sys[3]), float(thisSys[1]), float(thisSys[2]), float(thisSys[3]))
            mat['toSys'][thisSys[0]]=d
        #dump to mongo
        pid = coll.insert(mat.copy())
        print pid
        mat={}
    print 'Done'
    client.disconnect()

    return


def distance(x1, y1, z1, x2, y2, z2):
    '''Distance between systems - direct distance
    '''
    dX = x1-x2
    dY = y1-y2
    dZ = z1-z2
    dist = sqrt((dX**2)+(dY**2)+(dZ**2))
    return dist

def aggregate():
    '''look at the data and find systems closest to each other that have the highest price differential between market items
    '''
    #Pre process the system distance matrix?
    #Aggregate:
    #Get all items,
    #Get first item
    #Find system with highest sell price:
    #db.emd.find({"message.itemName":"performanceenhancers"}).sort({"message.sellPrice":-1}).limit(1)
    #find system with lowest buy price

    #Find distance between these systems
    client = MongoClient()
    db = client.mydb
    coll = db.emd
    distColl  = db.emd_dists
    outColl = db.emd_profitdata
    commodities = []
    profit = 0
    highProfit = 0
    aggProfits = []
    lowBuyPrice = 0
    lowBuySys = ''
    #Get a list of all commodities
    out = coll.aggregate([{"$group":{"_id":"$message.itemName"}}])
    for res in out['result']:
        commodities.append(res['_id'])

    #Loop through commodities finding best matches for profit routes
    for comm in commodities:
        highProfit = 0
        print 'Doing: '+comm
        highSellOut = coll.aggregate([{"$match":{"message.itemName":comm, "message.sellPrice":{"$gt":0}}},
                              {"$group":{"_id":"$message.stationName","totalsellprice":{"$sum":"$message.sellPrice"}, "totalHits":{"$sum":1}}},
                              {"$project":{"_id":1, "avgSell":{"$divide":["$totalsellprice","$totalHits"]}}},
                              {"$sort":{"avgSell":-1}}])

        if highSellOut['result']!=[]:
            #print highSellOut

            #get system name and sell price for highest
            highSysName = highSellOut['result'][0]['_id']
            #Convert to without station
            highSysName = highSysName[0:highSysName.find(' (')]
            highSellPrice = highSellOut['result'][0]['avgSell']

            #Now get average buy prices for this commodity in all systems - sort by lowest first
            out = coll.aggregate([{"$match":{"message.itemName":comm, "message.buyPrice":{"$gt":0}}},
              {"$group":{"_id":"$message.stationName","totalbuyprice":{"$sum":"$message.buyPrice"}, "totalHits":{"$sum":1}}},
              {"$project":{"_id":1, "avgBuy":{"$divide":["$totalbuyprice","$totalHits"]}}},
              {"$sort":{"avgBuy":1}}])
            if out['result']!=[]:

                #Get the highest profit route
                for res in out['result']:
                    profit = highSellPrice-res['avgBuy']
                    if profit>highProfit:
                        #highProfit = profit
                        lowBuyPrice = res['avgBuy']
                        lowBuySys = res['_id']
                #print lowBuyPrice, highSellPrice, highProfit, profit
                highProfit = highSellPrice-lowBuyPrice

                #Find distance between these routes
                #print lowBuySys
                f = distColl.find({"fromSys":lowBuySys[0:lowBuySys.find(' (')]})
                o = f.next()
                #print o
                dist = o['toSys'][highSysName]
                #Do some basic scoring - weight profit and distance
                score = highProfit*(dist**-1)
                #Dump to output
                profs = {'systemFrom':lowBuySys, 'systemTo':highSysName, 'dist':dist, 'score':score, 'avgProfit':highProfit, 'commodity':comm, 'avgBuy':lowBuyPrice, 'avgSell':highSellPrice}
                aggProfits.append(profs.copy())
                del profs
                highProfit = 0

    #Sort by the most profitable scoring route
    sortedProfits = sorted(aggProfits, key=itemgetter('score'))
    #build our output for mongo
    outData = {'procDTG':datetime.now(), 'profitData':sortedProfits}
    pid = outColl.insert(outData)
    #for i in sortedProfits:
        #print i
    client.disconnect()
    print 'Done'

    return

def graphing():
    '''make some graphs from the scored profit data
    '''
    client = MongoClient()
    db = client.mydb
    coll = db.emd_profitdata
    data = coll.find_one()
    x = []
    labsX = []
    labs = []
    y = []
    cnt = 0
    #Build up list of bar graph numbers
    for i in data['profitData']:
        #print i
        #print data['profitData']
        y.append(i['score'])
        x.append(cnt)
        labsX.append(cnt+0.3)
        labs.append(i['commodity'])
        cnt+=1
    print labs
    client.disconnect()
    bar = plt.bar(x, y, 0.3,
                 color='b',
                 label='Commodities by Profit Score (weighted by travel distance)')

    plt.xticks(labsX, labs, rotation=90)
    plt.legend()
    #plt.tight_layout()
    plt.show()


    return



if __name__ == '__main__':
    #main()
    #silverTrade()
    #aggregate()
    graphing()
    #computeDistMatrix()
    '''Other Ideas:
    do distance matrix in numpy
    make a sliding time window - user selectable
    precompute all this continuously - and store in mongo ready for user access
    What about actual route possibilities oper ship type / jump distance?
    '''







'''
    x = []
    y = []
    z = []
    i = 0
    #All depends what the baseline is for prices:
    startBuy = 1000
    startSell = 1000
    #TODO: Next figure out how to loop through stations comparing to our baseline station
    #now presume we are in i Bootis and find all the price differences
    for rec in out:
        #Only calculate the profit between fake start system and tilian
        if rec['message']['stationName']=='Ithaca (Hume Depot)':
            profit = rec['message']['sellPrice']-startBuy
            y.append(profit)
        #x.append(rec['message']['timestamp'])
            x.append(i)
        #diff = rec['message']['sellPrice']-rec['message']['buyPrice']
        #extract the ones where sell is higher than buy
        #y.append(diff)
        #y.append(int(rec['message']['sellPrice']))
        #z.append(int(rec['message']['buyPrice']))
        i+=1
    fig, axes = plt.subplots(nrows=2)
    axes[0] = fig.add_subplot(111)
    #tgt pos
    axes[0].xcorr(x,y, normed=True)
    #axes[0].plot(x,z, 'bo-')
    #print min(y), max(y), min(z), max(z), i
    plt.show()

    #Launch Pos
    #axes[0].plot([launchPos[0]],[launchPos[1]],[launchPos[2]], 'bo-')
    '''
