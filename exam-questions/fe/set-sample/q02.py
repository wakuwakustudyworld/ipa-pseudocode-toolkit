def fizzBuzz(num):
    result = None
    if num % 15 == 0:
        result = '3 と 5 で割り切れる'
    elif num % 3 == 0:
        result = '3 で割り切れる'
    elif num % 5 == 0:
        result = '5 で割り切れる'
    else:
        result = '3 でも 5 でも割り切れない'
    return result
