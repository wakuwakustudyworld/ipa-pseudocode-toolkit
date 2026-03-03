listHead = None

def delNode(pos):
    global listHead
    prev = None
    i = None
    if pos == 1:
        listHead = listHead.next
    else:
        prev = listHead
        for i in range(2, pos - 1 + 1):
            prev = prev.next
        prev.next = prev.next.next
