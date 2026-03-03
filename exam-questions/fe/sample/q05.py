words = None

def prob(c1, c2):
    s1 = str(c1)  # 手動変換: 「c1の1文字だけから成る文字列」
    s2 = str(c2)  # 手動変換: 「c2の1文字だけから成る文字列」
    if words.freq(s1 + s2) > 0:
        return words.freq(s1 + s2) / (words.freq(s1) - words.freqE(s1))
    else:
        return 0
