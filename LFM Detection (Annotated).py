# ============================================
# ============== Import modules ==============
# ============================================

import networkx as nx
import matplotlib.pyplot as plt
import random
import community
import csv

# ============================================
# ============= Import Netowrk ===============
# ============================================

# Build Karate Club Network (Comment Out if do not use)
G = nx.karate_club_graph()

# Build Computational Geometry Citation Network (Comment Out if do not use)
G1=nx.read_pajek('/Users/angelica/Documents/College/MATH_437/project/network.net')
G =nx.Graph()

## Remove singleton nodes that are disconnected from the graph
for v in G1.nodes():
    if (G1.degree(v)>0):
         G.add_node(v)

## Add edges that have both ends in the cleaned up graph
or e in G1.edges():
      v1 = e[0]
      v2 = e[1]
      if (v1 in G) and (v2 in G):
          G.add_edge(v1,v2)

## Global Variables          
nodeToDensity = {}
centerPoints = []
partition = {}
color = ['r','b','g','c','y']

# ============================================
# ====== Functions: Basic calculation  =======
# ============================================

def calculateDesensity(nodeA):
    """This function calculates the density of nodes in the network.
    The node density is calculated by the formula: Density = m/(m+k)
    where m is the number of edges inside the subgraph consisting of the neighbors of node i,
    and k is the number of edges going out of the neighborhood.
    It returns the density of the node as a float."""

    # create subgraph of the node and calculate m 
    subgraphOfNode = G.subgraph([nodeA]+G.neighbors(nodeA))
    internalEdgeNum = len(subgraphOfNode.edges())

    # calculate k
    tempList = G.edges(subgraphOfNode.nodes())
    externalEdgeList = [x for x in tempList if x not in subgraphOfNode.edges()]
    externalEdgeNum = len(externalEdgeList)
    
    result = 0
    if externalEdgeNum + internalEdgeNum != 0:
        result = float(internalEdgeNum)/float(externalEdgeNum + internalEdgeNum)
        
    return result

def calculateEdgeDistance(edge):
    """This function calculates edge distance as the inversof ECC:
    # of triangle the edge is in / min(degA-1, degB-1) 
    The function assumes that nodeA and nodeB are connected by an edge.
    The distance score is returned as a float
    """
    # edge AB
    nodeA = edge[0]
    nodeB = edge[1]

    # calculate the number of triangles the edge is in
    NodeA_nbrs = G.neighbors(nodeA)
    NodeB_nbrs = G.neighbors(nodeB)
    intersect = list(set(NodeA_nbrs)&set(NodeB_nbrs))
    numOfTriangle = len(intersect)

    # calculate potential triangel by taking miminum of degree of two nodes
    possibleTriangles = min(G.degree(nodeA),G.degree(nodeB))-1
    if(possibleTriangles == 0):
        result = 0
    else:
        result = float(float(possibleTriangles)/(float(numOfTriangle+1)))
        
    return result

def calculateAlternativeDistance(edge):
    """This function calculates the edge distance in an alternative way.
    The formula is # of triangle the edge is in / (degA+degB-2-#oftriangle).
    The function assumes that nodeA and nodeB are connected by an edge.
    The distance score is returned as a float
    """
    # edge AB
    nodeA = edge[0]
    nodeB = edge[1]

    # calculate the number of triangles the edge is in
    NodeA_nbrs = G.neighbors(nodeA)
    NodeB_nbrs = G.neighbors(nodeB)
    intersect = list(set(NodeA_nbrs) & set(NodeB_nbrs))
    numOfTriangle = len(intersect)

    # calculate potential triangel by taking miminum of degree of two nodes in an alternative way
    possibleTriangles = G.degree(nodeA)+ G.degree(nodeB) - 2 - numOfTriangle
    result = float(float(possibleTriangles) / (float(numOfTriangle + 1)))
    
    return result

# ============================================
# ======= Functions: Detect Community  =======
# ============================================

def calculateNodeDensity ():
    """The function calculates node density for each node in the network. It saves the results in a dictionary."""
    for n in G.nodes():
        value = calculateDesensity(n)
        nodeToDensity[n] = value

def calculateEdge():
    """The function calculates edge distance and save the results in a global dictionary"""
    for e in G.edges():
        value = calculateEdgeDistance(e)
        G[e[0]][e[1]]['distance']=value


def calculateAlternativeEdge():
    """The function calculates alternative edge distance and save the results in a global dictionary"""
    for e in G.edges():
        value = calculateAlternativeDistance(e)
        G[e[0]][e[1]]['distance']=value

def findSeed(r):
    """The function find the centroids for the network in radius r。 The function saves the seed in the partition dictionary as a key."""
    # initialization
    nodeSelected = {}

    # find maximal density within radius r 
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

    #Save the result           
    print("The number of seeds："，len(centerPoints))
    for seed in centerPoints:
        partition[seed] = []


def networkPartition():
    """The function classifies the rest of the nodes in the netowrk into communities led by centroids."""
    # initialization
    finishedNodes = {}

    # include centroid in the community
    for node in centerPoints:
        finishedNodes[node]=0
        partition[node].append(node)

    # classify the rest of the nodes by measuring shortest distance 
    for n in G.nodes():
        if n not in finishedNodes:
            minDistance = 10000000000
            for center in centerPoints:
                try:
                    distance = nx.dijkstra_path_length(G, n, center, 'distance')
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
            finishedNodes[n] = 0

# ============================================
# ============= Script Element  ==============
# ============================================

# detect communities
# the parameter r in findSeed function need to be experiemented on and adjusted based on network characteristics 
calculateNodeDensity()
calculateEdge()
findSeed(10)
networkPartition()

# write the output in csv file
filename = "result.csv"
myfile = open(filename,'w')
wr=csv.writer(myfile,quoting = csv.QUOTE_NONE)
firstRow = ["Node", "Community"]
for seed in partition:
    for node in partition[seed]:
        wr.writerow([node,seed])

