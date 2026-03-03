def change(n):
    count = 0
    rest = n
    while rest >= 0:
        count = count + rest // 5 + 1
        rest = rest - 10
    return count
