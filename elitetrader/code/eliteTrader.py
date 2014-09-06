'''
Created on 25 Aug 2014

@author: dusted-ipro
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
#import matplotlib.pyplot as plt
from datetime import datetime
from operator import itemgetter
from math import sqrt


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
            print highSellOut

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
                    print res, highSellPrice, highSysName
                    profit = highSellPrice-res['avgBuy']
                    if profit>highProfit:
                        #highProfit = profit
                        lowBuyPrice = res['avgBuy']
                        lowBuySys = res['_id']
                #print lowBuyPrice, highSellPrice, highProfit, profit
                highProfit = highSellPrice-lowBuyPrice
                print lowBuyPrice, highSellPrice, lowBuySys
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
    aggregate()
    #graphing()
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
