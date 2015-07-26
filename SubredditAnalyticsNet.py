from datetime import datetime
import json
import networkx as nx
from networkx.readwrite import json_graph
import pyLogger

class SubredditAnalyticsNet(object):
    def __init__(self):
        """
        Initialize the class with some basic attributes.
        """
        
        self.logger = pyLogger.logger('SubredditAnalyticsNet', pyLogger.INFO)
        
        self.net = nx.Graph()
        
        self.parentSub = '';
        self.dateStarted = str(datetime.now())
        self.nSubscribers = 0;
        
    def pruneUsersFewerThanN(self,N):
        H = self.net.copy()
        for n in self.net.nodes():
            if self.net.node[n]['type'] == 'subreddit':
                outdeg = self.net.degree(n)
                if outdeg < N:
                    H.remove_node(n)
                    self.logger.logDebug('Pruned node {0} with degree {1}'.format(n, outdeg))

        # Get rid of singletons
        outdeg = H.degree()
        H.remove_nodes_from([n for n in outdeg if outdeg[n] == 0])
        
        self.net = H

    def add_edge(self, pair):
        if ((pair[0], pair[1]) or (pair[1], pair[0])) in self.net.edges():
            self.net.edge[pair[0]][pair[1]]['weight'] = self.net.edge[pair[0]][pair[1]]['weight'] + 1
            self.logger.logDebug('Reinforced Edge {0} <=> {1} ({2})'.format(pair[0], pair[1], self.net.edge[pair[0]][pair[1]]['weight']))
        else:
            self.net.add_edge(pair[0], pair[1], weight=1)
            self.logger.logDebug('Added Edge {0} <=> {1}'.format(pair[0], pair[1]))

    def add_users_node(self, user, subreddits):
        self.net.add_star(['/u/'+user]+subreddits)
        self.net.node['/u/'+user]['type'] = 'user'
        for sub in subreddits:
            self.net.node[sub]['type'] = 'subreddit'

    def add_weighted_edge(self, pair):
        if (pair[0], pair[1]) in self.net.edges():
            self.net.edge[pair[0]][pair[1]]['weight'] = self.net.edge[pair[0]][pair[1]]['weight'] + 1
            self.logger.logDebug('Reinforced Edge {0} <=> {1} ({2})'.format(pair[0], pair[1], self.net.edge[pair[0]][pair[1]]['weight']))
        else:
            self.net.add_edge(pair[0], pair[1], weight=1)
            self.logger.logDebug('Added Edge {0} <=> {1}'.format(pair[0], pair[1]))

    def processNetforSave(self, N, myBot):
        self.logger.logDebug('Processing net for save')
        
        # Remove subs before reorganization
        try:
            usersToPrune = self.sortedSubDegrees()[N-1]
        except IndexError:
            usersToPrune = 0
        self.pruneUsersFewerThanN(usersToPrune)
        
        # Reorganize for save
        self.reorganizeNet()
        
        # Remove nodes from N to end of the list
        sortedSubs = self.subredditsSortedByUsers()
        self.net.remove_nodes_from([item[0] for item in sortedSubs[N:]])

        # Add number of subscribers
        for node in self.net.nodes():
            try:
                self.net.node[node]['subscribers'] = myBot.client.get_subreddit(node).subscribers
            except:
                self.net.node[node]['subscribers'] = -1
        self.nSubscribers = myBot.client.get_subreddit(self.parentSub).subscribers
        
        # Do some housecleaning
        self.setRelativeNUsers()
        self.setRelativeWeights()
        # Remove parallel edges
        self.net = nx.Graph(self.net)
        # Remove self loops
        self.net.remove_edges_from(self.net.selfloop_edges())

    def reorganizeNet(self):
        H = self.net.copy()
        self.net = nx.Graph()
        
        for source in H.nodes():
            if H.node[source]['type'] == 'subreddit':
                predecessors = nx.predecessor(H, source, cutoff = 2)
                for dest in predecessors:
                    if (H.node[dest]['type'] == 'subreddit' and source != dest):
                        for via in predecessors[dest]:
                            self.add_weighted_edge([source,dest])
                    
                self.net.node[source]['nUsers'] = H.degree(source)

    def saveDATAfile(self, totalUsers):
        self.logger.logInfo('Saving data for {0}'.format(self.parentSub))
        outList = json_graph.node_link_data(self.net) # node-link format to serialize
        extraData = dict(nSubscribers = self.nSubscribers,
                         nUsersTotal = totalUsers,
                         dateStarted = self.dateStarted,
                         dateProcessed = str(datetime.now()))
        outList = dict(outList.items() + extraData.items())
        
        json.dump(outList, open('html/JSON/'+self.parentSub+'.json','w'))

    def setRelativeWeights(self):
        maxWeight = max([self.net[e[0]][e[1]]['weight'] for e in self.net.edges()])
        for e in self.net.edges():
            self.net[e[0]][e[1]]['weightRel'] = self.net[e[0]][e[1]]['weight']/float(maxWeight)
        self.logger.logDebug('Set relative weights for edge segments')

    def setRelativeNUsers(self):
        maxUsers = max([self.net.node[item]['nUsers'] for item in self.net.nodes()])
        for item in self.net.nodes():
            self.net.node[item]['nUsersRel'] = self.net.node[item]['nUsers']/float(maxUsers)
        self.logger.logDebug('Set relative number of users for nodes')
        
    def sortedSubDegrees(self):
        subDegrees = [self.net.degree(n) for n in self.net.nodes() if self.net.node[n]['type'] == 'subreddit']
        return sorted(subDegrees,reverse=True)
                                                
    def subredditsSortedByUsers(self):
        outList = [(item, self.net.node[item]['nUsers']) for item in self.net.nodes()]
        outList = sorted(outList, key=lambda outList: outList[1], reverse = True)
        return outList
