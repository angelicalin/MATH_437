#networkx is required to compile
import networkx as nx
import matplotlib.pyplot as plt

import random
import community
import csv

#Fill in file path for the network. Assuming it is a Pajek file. However, networkX can parse many other network format as well

G1=nx.read_pajek('/Users/angelica/Documents/College/MATH_437/project/network.net')
#G = nx.karate_club_graph()
G=nx.Graph()
labelToId = {}
idToLabel = {}
nodeToDensity = {}
centerPoints = []
partition = {}
color = ['r','b','g','c','y']
# #print(G)
# #edgeToDistance = {}
# id = 0
# #print(len(G1.edges()))
# #load in the network
for v in G1.nodes():
    if (G1.degree(v)>0):
         G.add_node(v)
# #     labelToId[v] = id
# #     idToLabel[id] = v
# #     G.add_node(id)
# #     id+=1
for e in G1.edges():
      v1 = e[0]
      v2 = e[1]
      if (v1 in G) and (v2 in G):
# #     id1 = labelToId[v1]
# #     id2 = labelToId[v2]
          G.add_edge(v1,v2)
#G = nx.karate_club_graph()
#print(len(G.nodes()))
def calculateDesensity(nodeA):
    subgraphOfNode = G.subgraph([nodeA]+G.neighbors(nodeA))

    internalEdgeNum = len(subgraphOfNode.edges())
    tempList = G.edges(subgraphOfNode.nodes())
    externalEdgeList = [x for x in tempList if x not in subgraphOfNode.edges()]
    externalEdgeNum = len(externalEdgeList)
    result = 0
    if externalEdgeNum + internalEdgeNum != 0:
        result = float(internalEdgeNum)/float(externalEdgeNum + internalEdgeNum)
    return result



def calculateEdgeDistance(edge):
    """nodeA and nodeB are connected by an edge.
    ntriangle seeks to calculate the number of triangles that contains this edge.
    Then the functions calculates ecc of the edge."""
    nodeA = edge[0]
    nodeB = edge[1]
    NodeA_nbrs = G.neighbors(nodeA)
    NodeB_nbrs = G.neighbors(nodeB)
    intersect = list(set(NodeA_nbrs)&set(NodeB_nbrs))
    numOfTriangle = len(intersect)
    possibleTriangles = min(G.degree(nodeA),G.degree(nodeB))-1
    if(possibleTriangles == 0):
        result = 0
    else:
        result = float(float(possibleTriangles)/(float(numOfTriangle+1)))
    #print(result)
    return result

def calculateAlternativeDistance(edge):
    nodeA = edge[0]
    nodeB = edge[1]
    NodeA_nbrs = G.neighbors(nodeA)
    NodeB_nbrs = G.neighbors(nodeB)
    intersect = list(set(NodeA_nbrs) & set(NodeB_nbrs))
    numOfTriangle = len(intersect)
    possibleTriangles = G.degree(nodeA)+ G.degree(nodeB) - 2 - numOfTriangle
    result = float(float(possibleTriangles) / (float(numOfTriangle + 1)))
    return result


def calculateNodeDensity ():
    for n in G.nodes():
        value = calculateDesensity(n)
        nodeToDensity[n] = value

def calculateEdge():
    for e in G.edges():
        value = calculateEdgeDistance(e)
        G[e[0]][e[1]]['distance']=value


def calculateAlternativeEdge():
    for e in G.edges():
        value = calculateAlternativeDistance(e)
        G[e[0]][e[1]]['distance']=value

def findSeed(r):
    nodeSelected = {}


    while len(nodeSelected) != len(G.nodes()) :
        maxNodeClustering = 0
        maxNode = G.nodes()[0]
        for k in [x for x in nodeToDensity if x not in nodeSelected]:
            if nodeToDensity[k]>maxNodeClustering:
                maxNode = k
                maxNodeClustering = nodeToDensity[k]
        centerPoints.append(maxNode)
        notSelected = [x for x in nodeToDensity if x not in nodeSelected]
        for k in notSelected:
            try:
                if nx.dijkstra_path_length(G, maxNode, k, 'distance')<=r:
                    nodeSelected[k]=0
            except nx.exception.NetworkXNoPath:
                pass
    print(len(centerPoints))
    for seed in centerPoints:
        partition[seed] = []


def networkPartition():
    finishedNodes = {}
    for node in centerPoints:
        finishedNodes[node]=0
        partition[node].append(node)
    for n in G.nodes():
        #print(n)
        if n not in finishedNodes:

            minDistance = 10000000000

            for center in centerPoints:
                try:
                    distance = nx.dijkstra_path_length(G, n, center, 'distance')
                    #print(distance)
                    if distance < minDistance:
                        minDistance = distance
                        minCenter = center
                except nx.exception.NetworkXNoPath:
                    pass
            try:
                path = nx.dijkstra_path(G, minCenter, n, 'distance')
                for node in [x for x in path if (x not in finishedNodes)]:
                    partition[minCenter].append(node)
                for node in path:
                    finishedNodes[node] = 0
            except (nx.exception.NetworkXNoPath, UnboundLocalError):
                pass
            #partition[minCenter].append(n)
            finishedNodes[n] = 0





calculateNodeDensity()
calculateEdge()
findSeed(10)
networkPartition()
#print(partition)
# pos = nx.spring_layout(G)
#
# labels={}
# for i in range (len(G.nodes())):
#     labels[i] = i+1
# i = 0
# for group in partition:
#     nx.draw_networkx_nodes(G,pos,partition[group])
#     nx.draw_networkx_nodes(G,pos,[group],node_shape='s')
#     i= i+1
# nx.draw_networkx_edges(G,pos)
# nx.draw_networkx_labels(G,pos)
#plt.show()
filename = "result.csv"
myfile = open(filename,'w')
wr=csv.writer(myfile,quoting = csv.QUOTE_NONE)
firstRow = ["Node", "Community"]
print(partition)
for seed in partition:
    for node in partition[seed]:
        wr.writerow([node,seed])


# def runrun(alVal, time, iterationThreshold):
#     print("")
#     alpha = alVal
#     j=0
#     communities = detectAllCommunities(iterationThreshold)
#     communityCount = len(communities)
#
#     dictionaryT = idToLabel.copy()
#     for key in dictionaryT.keys():
#         dictionaryT[key] = []
#     for i in communities:
#         print("Community",j)
#         print(len(i.nodes()))
#         #print(i.nodes())
#         final = "["
#         for v in i.nodes():
#
#             final += (idToLabel[v] + ", ")
#         print(final + "]")
#
#         for v in i.nodes():
#             #lab = idToLabel[v]
#             dictionaryT[v] += [j]
#         j += 1
#
#     filename = "dolphin" + str(time) +"Alpha" +str(alpha)+ ".csv"
#     myfile = open(filename, 'w')
#     wr = csv.writer(myfile,quoting = csv.QUOTE_NONE)
#     firstRow = ["ID", "Label"]
#
#     for i in range(communityCount):
#         firstRow+=["Com"+str(i+1)]
#     wr.writerow(firstRow)
#     overLaps = ""
#     for key in dictionaryT:
#         valueList = dictionaryT[key]
#         resultString = [key,key]
#         if len(valueList)>=2:
#             overLaps += (str(key)+", ")
#         for i in range(communityCount):
#             if i in valueList:
#                 resultString+=[str(1)]
#             else:
#                 resultString+=[str(0)]
#         wr.writerow(resultString)
#     if (len(overLaps)!=0):
#         print("Overlaps: ", overLaps)
#
#
# def modularityTest():
#     part = community.best_partition(G)
#     communityIndex = 0
#     partitionList = {}
#     while (True):
#
#         changed = False
#         list = []
#         for k,v in part.items():
#             if v==communityIndex:
#                 changed = True
#                 list += [idToLabel[k] + ", "]
#         if (not changed):
#             break
#         print("mod", communityIndex)
#         print(list)
#         communityIndex+=1
#
