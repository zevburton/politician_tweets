import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt
import numpy as np
from string import Template
import re
import os
import shutil

G = nx.read_gml("bipartisanscoredgraph.gml")

def nx_ovito_dump(G, t, out_dir_path, edges=False, dim=2):
    if G.number_of_nodes()<=1000:
        pos=nx.spring_layout(G)
    else:
        pos=nx.circular_layout(G)
        pos=nx.random_layout(G)
    state = nx.get_node_attributes(G, 'state')
    state = list(state.values())
    statenames, stateindices = np.unique(state, return_inverse=True)
    party = nx.get_node_attributes(G, 'party')
    party = list(party.values())
    partynames, partyindices = np.unique(party, return_inverse=True)
    score = nx.get_node_attributes(G, 'score')
    score = list(score.values())
    degree = nx.get_node_attributes(G, 'degree')
    degree = list(degree.values())
    betweenness = nx.get_node_attributes(G, 'betweenness')
    betweenness = list(betweenness.values())
    closeness = nx.get_node_attributes(G, 'closeness')
    closeness = list(closeness.values())
    X = []
    for key in pos.keys():
        X.append([pos[key][0], pos[key][1], 0, 0, 0, 0, 0, 0, 0])
    for k in range(0,len(X)-1):
        if(dim==2):
            X[k][2]=0
        if(dim==3):
            X[k][2]=np.random.uniform(0,max(pos[key][0],pos[key][1]),1)[0]
        X[k][3] = stateindices[k]
        X[k][4] = partyindices[k]
        X[k][5] = score[k]
        X[k][6] = degree[k]
        X[k][7] = betweenness[k]
        X[k][8] = closeness[k]
    X = np.array(X)
        #STRING TEMPLATE TO BUILD REQUIRED FILE FORMAT
    my_template = Template(
"""ITEM: TIMESTEP
$t
ITEM: NUMBER OF ATOMS
$N
$INFO
"""
    )
    #BUILD HEADER
    INFO="ITEM: ATOMS id x y z type"

    if(X.shape[1]>4):
        k=1
        for i in range(4,X.shape[1]):
            INFO+=" v"+str(k); 
            k+=1
    INFO+="\n"

    #LOOP OVER ROWS
    for i in range(0,X.shape[0]):
        #LOOP OVER COLUMNS
        INFO+=str(i)+" "
        for j in range(0,X.shape[1]):
            INFO+=str(round(X[i,j],4))+" "
        INFO+="\n"

    #POPULATE TEMPLATE
    out=my_template.substitute({
    't' : t,
    'INFO' : INFO,
    'N' : X.shape[0]
    }
    )

    #print(out)
    # #SAVE SNAPSHOT
    with open(out_dir_path+"/"+str(t)+'.dump', 'w') as f:
        f.write(out)


    my_template = Template(
"""ITEM: TIMESTEP
$t
ITEM: NUMBER OF ENTRIES
$N
ITEM: ENTRIES index c_1[1] c_1[2] c_1[3] c_2[1] c_2[2] 
$INFO
"""
    )
    
    if(edges==True):
        x=0
        node_list=[]
        for node in G.nodes():
            mapping = {node:x}
            G = nx.relabel_nodes(G, mapping)
            node_list.append(node)
            x+=1
        edgelist = nx.generate_edgelist(G)
        E = []
        for line in edgelist:
            line = re.sub('{}', '', line)
            split = line.split()
            E.append([split[0],split[1]])
        E = np.array(E)
        INFO=""
        for i in range(0,E.shape[0]):
            INFO+=str(i)+" 1 "+str(E[i,0])+" "+str(E[i,1])+" 1.0 1.0 \n"
        out=my_template.substitute({
        't' : t,
        'INFO' : INFO,
        'N' : E.shape[0]
        }
        )
        #print(out)
        with open(out_dir_path+"/"+str(t)+'.bond.dump', 'w') as f:
            f.write(out)
def create_folder(out_dir_path):
    if(os.path.exists(out_dir_path)):
        shutil.rmtree(out_dir_path)
    os.mkdir(out_dir_path)

def save_graph(graph,file_name):
    #initialze Figure
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)
    nx.draw_networkx_labels(graph,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name,bbox_inches="tight")
    pylab.close()
    del fig

#CREATE FOLDER 
output_folder="results-1"
create_folder(output_folder)

nx_ovito_dump(G,1,output_folder,edges=True,dim=2)
#Assuming that the graph g has nodes and edges entered
#save_graph(G,"full_graph.pdf")