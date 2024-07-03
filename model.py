import copy

import networkx as nx
from database.DAO import DAO
class Model:
    def __init__(self):
        self._graph = nx.Graph()

        self._generi = DAO.getGenere()
        self._canzoni = []

        self._bestPath = []
        self._bestLen = 0


    def buildGraph(self, genere):
        self._canzoni = DAO.getCanzoni(genere.GenreId)

        self._graph.clear()
        self._graph.add_nodes_from(self._canzoni)

        for u in self._graph.nodes:
            for v in self._graph.nodes:
                if u != v:

                    peso = abs(DAO.getPeso(u.TrackId, v.TrackId)[0])

                    if peso:
                        self._graph.add_edge(u, v, weight=peso)



    def getNumNodes(self):
        return len(self._graph.nodes)


    def getNumEdges(self):
        return len(self._graph.edges)


    def getDeltaMassimo(self):
        deltaMax = 0
        bestEdges = []

        for edge in self._graph.edges:
            pesoEdge = self._graph[edge[0]][edge[1]]['weight']

            if pesoEdge > deltaMax:
                deltaMax = pesoEdge
                bestEdges = [edge]

            elif pesoEdge == deltaMax:
                bestEdges.append(edge)

        return bestEdges, deltaMax


    def getPercorso(self, c0, bytes):
        self._bestPath = []
        self._bestLen = 0

        # inizializzo il parziale con la canzone scelta dall'utente, così è sicuro
        # contenuta nel percorso
        parziale = [c0]

        # calcolo le componenti connesse di c0 così non devo calcolarle ad ogni iterazione
        connesse = nx.node_connected_component(self._graph, c0)


        self._ricorsione(parziale, bytes, connesse)

        return self._bestPath, self._bestLen


    def _ricorsione(self, parziale, bytes, connesse):

        # 1.    controllo che la lunghezza del parziale sia maggiore della migliore trovata finora
        #       e nel caso aggiorno il miglior percorso e la miglior lunghezza, ma non esco dalla ricorsione
        #       perchè potenzialmente posso aumentare ancora il numero di canzoni del percorso
        if len(parziale) > self._bestLen:
            self._bestPath = copy.deepcopy(parziale)
            self._bestLen = len(parziale)

        # 2.    verifico che tutti i nodi siano presenti tra le componenti connesse di c0
        for nodo in connesse:
        # 3.    verifico che il numero di bytes totale (compreso della nuova canzone da aggiungere
        #       al percorso) sia inferiore a quello impostato dall'utente
            if (self.getTotBytes(parziale) + nodo.Bytes) > bytes:
                return

            else:
                if nodo not in parziale:
                    parziale.append(nodo)
                    self._ricorsione(parziale, bytes, connesse)
                    parziale.pop()
        return


    def getTotBytes(self, parziale):
        totBytes = 0

        for nodo in parziale:
            totBytes += nodo.Bytes

        return totBytes


    def getPeso(self, n1, n2):
        return self._graph[n1][n2]["weight"]

