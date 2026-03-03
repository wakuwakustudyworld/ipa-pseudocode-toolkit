from ipa_pseudocode.core.array import Array2D

def edgesToMatrix(edgeList, nodeNum):
    adjMatrix = Array2D(nodeNum, nodeNum, init=0)
    i = None
    u = None
    v = None
    for i in range(1, len(edgeList) + 1):
        u = edgeList[i][1]
        v = edgeList[i][2]
        adjMatrix[u, v] = 1
        adjMatrix[v, u] = 1
    return adjMatrix
