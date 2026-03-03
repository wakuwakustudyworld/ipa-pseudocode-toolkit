def simRatio(s1, s2):
    i = None
    cnt = 0
    if len(s1) != len(s2):
        return -1
    for i in range(1, len(s1) + 1):
        if s1[i] == s2[i]:
            cnt = cnt + 1
    return cnt / len(s1)
