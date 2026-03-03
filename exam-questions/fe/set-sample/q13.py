def search(data, target):
    low = None
    high = None
    middle = None
    low = 1
    high = len(data)
    while low <= high:
        middle = (low + high) // 2
        if data[middle] < target:
            low = middle
        elif data[middle] > target:
            high = middle
        else:
            return middle
    return -1
