"""令和7年秋 応用情報技術者試験 午後 問3
動的計画法による最長共通部分列（LCS）の長さを求めるアルゴリズム

全体手動変換: 0-based配列、二次元配列の初期化を含むため
"""


def calculate_lcsl(S, T):
    """図4: 動的計画法を用いて最長共通部分列の長さを求めるプログラム"""
    s = len(S)
    t = len(T)
    # lcsl は (s+1) x (t+1) の二次元配列
    lcsl = [[None] * (t + 1) for _ in range(s + 1)]

    for n in range(s + 1):
        lcsl[n][0] = 0
    for k in range(t + 1):
        lcsl[0][k] = 0

    for n in range(1, s + 1):
        for k in range(1, t + 1):
            if S[n - 1] == T[k - 1]:  # (1) x_n = y_k
                lcsl[n][k] = lcsl[n - 1][k - 1] + 1  # ウ
            elif lcsl[n][k - 1] > lcsl[n - 1][k]:  # (2) LCSL(n,k-1) > LCSL(n-1,k)
                lcsl[n][k] = lcsl[n][k - 1]  # エ
            else:
                lcsl[n][k] = lcsl[n - 1][k]  # オ

    return lcsl[s][t]  # カ


def calculate_lcsl_with_table(S, T):
    """テーブル全体を返すデバッグ版"""
    s = len(S)
    t = len(T)
    lcsl = [[0] * (t + 1) for _ in range(s + 1)]

    for n in range(1, s + 1):
        for k in range(1, t + 1):
            if S[n - 1] == T[k - 1]:
                lcsl[n][k] = lcsl[n - 1][k - 1] + 1
            elif lcsl[n][k - 1] > lcsl[n - 1][k]:
                lcsl[n][k] = lcsl[n][k - 1]
            else:
                lcsl[n][k] = lcsl[n - 1][k]

    return lcsl


if __name__ == "__main__":
    # 設問1: {"A","C","B","C","D","C"} と {"C","D","B","D","C","A"}
    S1 = ["A", "C", "B", "C", "D", "C"]
    T1 = ["C", "D", "B", "D", "C", "A"]
    result1 = calculate_lcsl(S1, T1)
    print(f"設問1: LCS長 = {result1}  (期待: 4)")

    # 図3の検証: X={"A","B","C","B","D","A","B"}, Y={"B","D","C","A","B","A"}
    X = ["A", "B", "C", "B", "D", "A", "B"]
    Y = ["B", "D", "C", "A", "B", "A"]
    table = calculate_lcsl_with_table(X, Y)

    print("\n図3 LCSL(n, k) の値:")
    header = ["n\\k"] + [str(k) for k in range(len(Y) + 1)]
    print(f"{'':>4}", end="")
    for k in range(len(Y) + 1):
        yk = "-" if k == 0 else Y[k - 1]
        print(f" {k}({yk})", end="")
    print()

    for n in range(len(X) + 1):
        xn = "-" if n == 0 else X[n - 1]
        print(f"{n}({xn})", end="")
        for k in range(len(Y) + 1):
            print(f"    {table[n][k]}", end="")
        print()

    print(f"\nア = LCSL(3,4) = {table[3][4]}  (期待: 2)")
    print(f"イ = LCSL(7,5) = {table[7][5]}  (期待: 4)")
    print(f"最長共通部分列の長さ = {table[7][6]}  (期待: 4)")
