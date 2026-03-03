def calcCosineSimilarity(vector1, vector2):
    similarity = None
    numerator = None
    denominator = None
    temp = 0
    i = None
    numerator = 0
    for i in range(1, len(vector1) + 1):
        numerator = numerator + vector1[i] * vector2[i]
    for i in range(1, len(vector1) + 1):
        temp = temp + vector1[i] ** 2
    denominator = temp ** 0.5
    temp = 0
    for i in range(1, len(vector2) + 1):
        temp = temp + vector2[i] ** 2
    denominator = denominator * temp ** 0.5
    similarity = numerator / denominator
    return similarity
