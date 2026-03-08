def printStars(num):
    cnt = 0
    starColor = 'SC1'
    while cnt < num:
        if starColor == 'SC1':
            print('☆')
            starColor = 'SC2'
        else:
            print('★')
            starColor = 'SC1'
        cnt += 1

