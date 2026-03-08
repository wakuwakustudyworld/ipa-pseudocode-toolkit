from ipa_pseudocode.core.array import Array, Array2D


def distance(N, INF, edge, GOAL, dist, done):
    """ダイクストラ法による最短距離の算出と最短経路の出力

    手動変換: 関数の引数としてN, INF, edge, GOAL, dist, doneを受け取る形に変更
              （元の擬似言語では外部から与えられる前提）
    """
    viaNode = Array(N, init=0)
    j = None
    curNode = None
    minDist = None
    k = None
    dist[1] = 0
    while True:
        minDist = INF
        for k in range(1, N + 1):
            if done[k] == 0 and dist[k] < minDist:  # 手動変換: 複合条件
                minDist = dist[k]
                curNode = k
        done[curNode] = 1
        if curNode == GOAL:
            # 図4: 最短経路の出力
            j = GOAL
            print(GOAL)
            while j > 1:
                print(viaNode[j])
                j = viaNode[j]
            return dist[curNode]
        for k in range(1, N + 1):
            if dist[curNode] + edge[curNode, k] < dist[k] and done[k] == 0:  # 手動変換: 複合条件
                dist[k] = dist[curNode] + edge[curNode, k]
                viaNode[k] = curNode
