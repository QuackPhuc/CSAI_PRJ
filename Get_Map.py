import numpy as np


def get_Map(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    max_len = max(len(line.strip()) for line in lines)
    array = [list(line.strip().ljust(max_len)) for line in lines]
    return np.array(array[1:])

class MAP:
    def __init__(self, file):
        self.map =
Map = get_Map('input.txt')
print(Map.shape)
