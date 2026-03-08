"""令和6年秋 応用情報技術者試験 午後 問3
エラトステネスの篩による素数列挙アルゴリズム（3段階の改良）

全体手動変換: 擬似言語の配列操作（末尾追加、1-based）と
             整数除算（÷...の商）の変換が必要なため
"""


def prime1(N):
    """図1: 単純な素数判定"""
    primes = []
    d = 2
    l1_count = 0  # (L1)の実行回数カウント
    while d <= N:
        isPrime = True
        t = 2
        while t < d:
            if d % t == 0:
                isPrime = False
            t = t + 1  # (L1)
            l1_count += 1
        if isPrime:
            primes.append(d)
        d = d + 1
    return primes, l1_count


def prime2(N):
    """図2: エラトステネスの篩"""
    primes = []
    isPrime = [False]  # isPrime[0] = False (要素番号1がindex 0に対応)
    c = 2
    d = 2
    l2_count = 0  # (L2)の実行回数カウント
    while c <= N:
        isPrime.append(True)  # isPrime[c] = True (1-based → index c-1... だが要素番号=index+1にするためそのままappend)
        c = c + 1
    # isPrime[k] (1-based) → isPrime[k] (0-based index k, ただし isPrime[0]=Falseで1は非素数)
    # 実際には isPrime のサイズは N+1 (index 0..N) で isPrime[d] を直接参照
    # 初期化後: isPrime = [False, False(未使用), True, True, ..., True] だが
    # 上のコードでは isPrime = [False, True, True, ..., True] (長さ N)
    # isPrime[1]=True(index1) が 2 に対応... ではなく
    # 擬似言語では要素番号1始まりで isPrime[1]=False, isPrime[2]=True, ...
    # Pythonでは0始まりなので isPrime[d] → isPrime[d] (index = d)
    # 修正: index 0 = False, 次に c=2..N で N-1個の True を追加
    # → isPrime = [False, True, True, ..., True] 長さ N
    # → isPrime[d] のアクセスは d をそのままindexに使えるが、長さが N なので d は 0..N-1
    # 擬似言語の isPrime[d] (1-based) = Python の isPrime[d] (0-based) にするには要素を1個ずらす必要

    # やり直し: 擬似言語通りに1-basedで実装
    isPrime = [None]  # index 0 は未使用
    isPrime.append(False)  # isPrime[1] = False
    c = 2
    while c <= N:
        isPrime.append(True)  # isPrime[c] = True
        c += 1

    d = 2
    while d <= N:
        if isPrime[d] == True:  # イ: isPrime[d]がtrueと等しい
            primes.append(d)
            t = d * d
            while t <= N:
                isPrime[t] = False
                t = t + d  # ウ: t + d  (L2)
                l2_count += 1
        d = d + 1
    return primes, l2_count


def prime3(N):
    """図3: 奇数のみ対象の改良版"""
    primes = [2]
    isPrime = []  # 1-based: isPrime[k] は 2k+1 が素数かを表す
    c = 3
    l3_count = 0  # (L3)の実行回数カウント

    # 初期化: c=3,5,7,...,N(以下) に対して True を追加
    while c <= N:
        isPrime.append(True)
        c = c + 2
    # isPrime[0]=True(未使用パディングなし) → 1-basedにするため先頭にダミーを挿入
    isPrime = [None] + isPrime  # isPrime[1] が 3 に対応 (2*1+1=3)

    d = 3
    while d <= N:
        idx = (d - 1) // 2  # エ: (d-1) ÷ 2の商
        if isPrime[idx] == True:
            primes.append(d)
            t = d * d
            while t <= N:
                t_idx = (t - 1) // 2  # オ: (t-1) ÷ 2の商
                isPrime[t_idx] = False
                t = t + 2 * d  # カ: t + 2×d  (L3)
                l3_count += 1
        d = d + 2
    return primes, l3_count


if __name__ == "__main__":
    # 検証
    p1, l1 = prime1(20)
    p2, l2 = prime2(20)
    p3, l3 = prime3(20)

    expected = [2, 3, 5, 7, 11, 13, 17, 19]
    print(f"prime1(20) = {p1}  (L1実行回数: {l1})")
    print(f"prime2(20) = {p2}  (L2実行回数: {l2})")
    print(f"prime3(20) = {p3}  (L3実行回数: {l3})")
    print(f"期待値:      {expected}")
    print(f"一致: prime1={p1==expected}, prime2={p2==expected}, prime3={p3==expected}")
