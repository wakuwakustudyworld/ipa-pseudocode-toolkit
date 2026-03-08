"""令和7年春 応用情報技術者試験 午後 問3
スライドパズルの最小解を幅優先探索で求めるプログラム

全体手動変換: クラス(BoardState, Queue, List)やメソッド呼び出しを含むため
"""

import copy
from collections import deque


class BoardState:
    """盤面状態を保持する単方向連結リストの要素"""

    def __init__(self, st=None):
        if st is None:
            self.board = None
            self.space = None
            self.prev = None
        else:
            self.board = copy.deepcopy(st.board)
            self.space = list(st.space)
            self.prev = st


class Queue:
    """キューを実現するクラス"""

    def __init__(self):
        self._data = deque()

    def add(self, st):
        self._data.append(st)

    def isEmpty(self):
        return len(self._data) == 0

    def poll(self):
        return self._data.popleft()

    def peek(self):
        return self._data[0]


class List:
    """探索済み盤面リストを実現するクラス"""

    def __init__(self):
        self._data = []

    def add(self, b):
        self._data.append(copy.deepcopy(b))

    def isEmpty(self):
        return len(self._data) == 0

    def peek(self):
        return self._data[0]

    def contains(self, b):
        return any(b == item for item in self._data)


def createGoal(board_size):
    """ゴールの盤面配列を作成"""
    goal = []
    num = 1
    for r in range(board_size):
        row = []
        for c in range(board_size):
            row.append(num)
            num += 1
        goal.append(row)
    goal[board_size - 1][board_size - 1] = board_size * board_size  # 右下が空白
    return goal


def getSpace(b):
    """空白マスの位置を [行番号, 列番号] で返す（1-based）"""
    for r in range(len(b)):
        for c in range(len(b[r])):
            if b[r][c] == len(b) * len(b):
                return [r + 1, c + 1]  # 1-based
    return None


def checkGoal(b, g):
    """盤面がゴールと一致するか判定"""
    return b == g


def checkSameBoard(b, l):
    """盤面が探索済みリストに存在するか判定"""
    return l.contains(b)


def printResult(st):
    """開始時点からの遷移と移動回数を出力"""
    path = []
    current = st
    while current is not None:
        path.append(current.board)
        current = current.prev
    path.reverse()
    for i, board in enumerate(path):
        print(f"--- 移動 {i} ---")
        size = len(board)
        for r in range(size):
            print(board[r])
    print(f"移動回数: {len(path) - 1}")


def solveNPuzzle(board_size, start_board=None):
    """最小解を求めるプログラム（図7）

    Args:
        board_size: 一辺のマス数
        start_board: 開始時点の盤面（Noneならランダム生成）
    """
    start_state = BoardState()
    goal_board = createGoal(board_size)

    if start_board is not None:
        start_state.board = copy.deepcopy(start_board)
    else:
        # 手動変換: createStart は問題文ではランダム生成だが、テスト用に引数で受け取る
        raise ValueError("start_boardを指定してください")

    start_state.space = getSpace(start_state.board)

    # direction: 駒の移動に伴う空白マスの移動方向
    # [下, 左, 上, 右] = [{1,0}, {0,-1}, {-1,0}, {0,1}]
    direction = [[1, 0], [0, -1], [-1, 0], [0, 1]]

    explore_queue = Queue()
    explore_queue.add(start_state)
    check_list = List()
    check_list.add(start_state.board)

    while explore_queue.isEmpty() == False:  # ア: explore_queue.isEmpty()
        state = explore_queue.poll()  # イ: poll()
        for i in range(len(direction)):
            di = direction[i]
            # ウ: direction[i][1] → di[0] (0-based), エ: board_size
            # オ: direction[i][2] → di[1] (0-based)
            new_row = state.space[0] + di[0]  # 0-based内部表現
            new_col = state.space[1] + di[1]
            if (1 <= new_row <= board_size) and (1 <= new_col <= board_size):
                new_state = BoardState(state)
                new_state.space = [new_row, new_col]
                # 盤面配列は0-basedでアクセス
                r0, c0 = new_row - 1, new_col - 1
                r1, c1 = state.space[0] - 1, state.space[1] - 1
                change_num = new_state.board[r0][c0]
                new_state.board[r0][c0] = board_size * board_size
                new_state.board[r1][c1] = change_num

                if checkGoal(new_state.board, goal_board):  # カ
                    printResult(new_state)
                    return
                if not checkSameBoard(new_state.board, check_list):
                    explore_queue.add(new_state)  # キ: add(new_state)
                    check_list.add(new_state.board)  # ク: add(new_state.board)

    print("ゴールの盤面に至る駒の移動方法がありません")
