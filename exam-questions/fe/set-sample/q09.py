from ipa_pseudocode.core.array import Array

tree = Array.from_literal([Array.from_literal([2, 3]), Array.from_literal([4, 5]), Array.from_literal([6, 7]), Array.from_literal([8, 9]), Array.from_literal([10, 11]), Array.from_literal([12, 13]), Array.from_literal([14]), Array.from_literal([]), Array.from_literal([]), Array.from_literal([]), Array.from_literal([]), Array.from_literal([]), Array.from_literal([]), Array.from_literal([])])

def order(n):
    if len(tree[n]) == 2:
        order(tree[n][1])
        print(n)
        order(tree[n][2])
    elif len(tree[n]) == 1:
        order(tree[n][1])
        print(n)
    else:
        print(n)
