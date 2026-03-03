from ipa_pseudocode.core.array import Array

def transformSparseMatrix(matrix):
    i = None
    j = None
    sparseMatrix = None
    sparseMatrix = Array.from_literal([Array.from_literal([]), Array.from_literal([]), Array.from_literal([])])
    for i in range(1, matrix.rows + 1):
        for j in range(1, matrix.cols + 1):
            if matrix[i, j] != 0:
                sparseMatrix[1].append(i)
                sparseMatrix[2].append(j)
                sparseMatrix[3].append(matrix[i, j])
    return sparseMatrix
