def matrix_size(matrix):
    return matrix.shape[0] * matrix[1]


def find_biggest_matrix(matrices):
    biggest_matrix = {
        'i': 0,
        'matrix': matrices[0]
    }
    for i in range(len(matrices)):
        if matrix_size(matrices[i]) > matrix_size(biggest_matrix['s']):
            biggest_matrix = {
                'i': i,
                'matrix': matrices[i]
            }
    return biggest_matrix
