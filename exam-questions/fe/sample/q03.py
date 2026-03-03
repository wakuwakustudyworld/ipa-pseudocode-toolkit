listHead = None

def append(qVal):
    global listHead
    prev = None
    curr = None
    curr = ListElement(qVal)
    if listHead is None:
        listHead = curr
    else:
        prev = listHead
        while prev.next is not None:
            prev = prev.next
        prev.next = curr
