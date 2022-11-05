from collections import defaultdict
from pymongo import MongoClient
import time

def get_layer_evolution(pkg):
    client=MongoClient("localhost",27017)
    db=client["SC"]
    edges=db["edge"]
    evol=db["evolution"]
    if evol.find_one({"pkg":pkg}):
        return evol.find_one({"pkg":pkg})["evolution_data"]
    t={}
    layer=defaultdict(set)
    for edge in edges.find({"pkg":pkg}):
        if edge["timestamp"]>"1585670399":
            continue
        timestamp=edge["timestamp"]
        if timestamp < t.get(edge["from"],"9999999999"):
            t[edge["from"]]=timestamp
        
        layer[edge["layer"]].add(edge["from"])

    ma="1585670399"  #2020.3.31 23:59:59    
    mi=min(t.values())

    interval=(int(ma)-int(mi))//15

    res=defaultdict(list)
    max_layer=max(layer.keys())
    for timestamp in range(int(mi),int(ma)+1,interval):
        for layer_idx in range(1,max_layer+1):
            res[layer_idx].append(len(list(filter(lambda e: int(t[e])<=timestamp,list(layer[layer_idx])))))

    date=[]
    for times in range(int(mi),int(ma)+1,interval):
        timeArray = time.localtime(times)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        date.append(otherStyleTime.split()[0])
    
    series=[]
    legend=[]
    for i in res:
        series.append({"name":"Layer "+str(i),"type": "line","stack": "Total","areaStyle": {},"emphasis": {
              "focus": "series"},"data":res[i]})
        legend.append("Layer "+str(i))
    
    # series[-1]["label"]={"show":True,"position": "top"}

    
    evol.insert_one({"pkg":pkg,"evolution_data":{"date":date,"series":series,"legend":legend}}) 
    return {"date":date,"series":series,"legend":legend}

# print(get_layer_evolution("torch"))



    





