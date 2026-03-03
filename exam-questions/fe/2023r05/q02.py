def proc1():
    print('A')
    proc3()

def proc2():
    proc3()
    print('B')
    proc1()

def proc3():
    print('C')
