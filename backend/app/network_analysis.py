import networkx as nx
from pymongo import MongoClient
client=MongoClient("localhost",27017)
db=client["SC"]
sc_tree=db["sc_tree"]
edge=db["edge"]

net_m=db["net_m"]

def get_edges(pkg,timestamp):
    edges = []
    for d in edge.find({"pkg":pkg}):
        if d["timestamp"] <= timestamp:
            edges.append((d["from"],d["to"]))
    return edges

def get_net_metrics(pkg,timestamp):
    if net_m.find_one({"pkg":pkg,"timestamp":timestamp}):
        return net_m.find_one({"pkg":pkg,"timestamp":timestamp})["res"]
    edges=get_edges(pkg,timestamp)
    
    G = nx.Graph()
    G.add_edges_from(edges)

    G2 =nx.DiGraph()#有向图
    G2.add_edges_from(edges)
    #print(G.number_of_nodes())
    b = nx.betweenness_centrality(G, k=None, normalized=False, weight=None, endpoints=False, seed=None)
    # c = nx.closeness_centrality(G)
    d = nx.degree_centrality(G)

    res_1 = dict()
    for k in b.keys():
        res_1[k] = [b[k]]
    for k in d.keys():
        res_1[k].append(d[k]*(len(G)-1))
        res_1[k].append(k)

    pr = nx.pagerank(G2)
    in_degree=G2.in_degree()
    
    for i in in_degree:
        pr[i[0]]=[i[1],pr[i[0]],i[0]]
    net_m.insert_one({"pkg":pkg,"timestamp":timestamp,"res":{"between_degree":list(res_1.values()),"indegree_pagerank":list(pr.values())}})
    return  {"between_degree":list(res_1.values()),"indegree_pagerank":list(pr.values())}

#print(get_net_metrics("torch","1585670399"))

