def calculateAmountOfPrize(improvement, period):
    prize = None
    if improvement < 100000:
        if period < 7:
            prize = 500
        else:
            prize = 1000
    else:
        if period < 7:
            prize = 2000
        else:
            prize = 5000
    return prize

