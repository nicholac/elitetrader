
from django.shortcuts import render, render_to_response
from pymongo import MongoClient
#from django.utils import simplejson
from operator import itemgetter
import simplejson

# Create your views here.




def home(request):
    responseOut = {}
    allOut = []
    '''make some graphs from the scored profit data
    '''
    client = MongoClient()
    db = client.mydb
    coll = db.emd_profitdata
    #data = coll.find_one()
    #Get the most recent entry
    d = coll.find().sort('procDTG',-1).limit(1)
    #sort data
    data = d.next()
    runDate = data['procDTG']
    sortedProfits = sorted(data['profitData'], key=itemgetter('avgProfit'), reverse=True)
    x = []
    labsX = []
    labs = []
    y = []
    cnt = 0
    td = []
    #Build up list of bar graph numbers - commidities by score
    #for i in data['profitData']:
    for i in sortedProfits:
        #print i
        #print data['profitData']
        allOut.append({'score':i['score'], 'commodity':i['commodity']})
        td.append([i['commodity'], i['systemFrom'], i['systemTo'], i['dist'], i['avgProfit']])
        #allOut.append({'score':i['score'], 'commodity':cnt})
        y.append(i['score'])
        #y.append(i['score'])
        #x.append(cnt)
        #labsX.append(cnt+0.3)
        #labs.append(i['commodity'])
        cnt+=1
    client.disconnect()
    print allOut
    #Build Output
    json_list = simplejson.dumps(allOut)
    responseOut['procDTG']=runDate
    responseOut['allOutput']= json_list
    responseOut['tableData']=td
    responseOut['yvals'] = y
    responseOut['bins']=cnt
    responseOut['page_title']='Trader Results'
    responseOut['proc_pass_msg']= 'Results Below'
    #return responseOut
    #TODO: implement csrf checking
    #responseOut[0](csrf(request))
    return render_to_response('trader_results3.html',responseOut)


