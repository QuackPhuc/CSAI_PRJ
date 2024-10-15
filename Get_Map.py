import numpy as np
from collections import defaultdict
import itertools

Predefine = {
    "Wall": "#",
    "Stone": "$",
    "Ares": "@",
    "Switch": ".",
    "Ares on Switch": "+",
    "Stone on Switch": "*"
}


def same_x_pair(cordinates_list: list):
    grouped_pairs = defaultdict(list)
    for pair in cordinates_list:
        grouped_pairs[pair[0]].append(pair)
    grouped_pairs = dict(grouped_pairs)
    pairs = []
    for k, v in grouped_pairs.items():
        pairs += (list(itertools.combinations(v, 2)))

    return pairs


def same_y_pair(cordinates_list: list):
    grouped_pairs = defaultdict(list)
    for pair in cordinates_list:
        grouped_pairs[pair[1]].append(pair)
    grouped_pairs = dict(grouped_pairs)
    pairs = []
    for k, v in grouped_pairs.items():
        pairs += (list(itertools.combinations(v, 2)))

    return pairs


def get_Map(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    max_len = max(len(line.strip()) for line in lines)
    array = [list(line.strip().ljust(max_len)) for line in lines]
    return np.array(array[1:])


class Maze:
    def __init__(self, file_path):
        self.Ares = None
        self.Walls = None
        self.Stones = None
        self.Stones_Weight = None
        self.taboo_cells = []
        self.Switches = None
        self.nrows = None
        self.ncols = None
        self.Init_from_file(file_path)

    def Init_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
        lines = [line.rstrip() for line in lines]

        self.nrows = len(lines) - 1
        self.ncols = max(len(line) for line in lines)

        maze = np.array([list(line.ljust(self.ncols)) for line in lines][1:])

        self.Ares = list(zip(*np.where(maze == '@')))
        self.Ares += list(zip(*np.where(maze == '+')))

        self.Walls = list(zip(*np.where(maze == "#")))

        self.Stones = list(zip(*np.where(maze == "$")))
        self.Stones += list(zip(*np.where(maze == "*")))

        self.Switches = list(zip(*np.where(maze == ".")))
        self.Switches += list(zip(*np.where(maze == "*")))

        self.Stones_Weight = np.fromstring(lines[0], dtype=int, sep=" ")
        # Mark all outsider by X
        for i in range(maze.shape[0]):
            j = 0
            while maze[i, j] != "#":
                maze[i, j] = "X"
                j += 1
            j = self.ncols - 1
            while maze[i, j] != "#":
                maze[i, j] = "X"
                j -= 1
        corners = []
        U_shape = []
        for y in range(self.nrows):
            for x in range(self.ncols):
                if maze[y, x] == 'X':  # Check if Outsider
                    continue
                if (y, x) not in self.Walls and (y, x) not in self.Switches:  # Find all Invalid Corners
                    if (((y - 1, x) in self.Walls and (y, x - 1) in self.Walls) or
                            ((y - 1, x) in self.Walls and (y, x + 1) in self.Walls) or
                            ((y + 1, x) in self.Walls and (y, x - 1) in self.Walls) or
                            ((y + 1, x) in self.Walls and (y, x + 1) in self.Walls)
                    ):
                        corners.append((y, x))
                        maze[y, x] = "T"  # T stands for Taboos

        for x, y in corners:
            if int(maze[x - 1, y] == "#") + int(maze[x + 1, y] == "#") + int(maze[x, y - 1] == "#") + int(
                    maze[x, y + 1] == "#") >= 3 and (x, y) not in self.Switches:
                U_shape.append((x, y))

        # All Taboo cells in U_shape case
        for x, y in U_shape:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (x + dx, y + dy) in self.Walls or (x + dx, y + dy) in self.Switches:
                    continue
                while (x, y) not in self.Walls and (x, y) not in self.Switches and (x + dy, y + dx) in self.Walls and (
                        x - dy, y - dx) in self.Walls:
                    maze[x, y] = 'T'
                    x += dx
                    y += dy

        x_pairs = same_x_pair(corners)
        for c1, c2 in x_pairs:
            if maze[c1[0], c1[1]:c2[1]].__contains__("#") or maze[c1[0], c1[1]:c2[1]].__contains__(".") \
                    or maze[c1[0],c1[1]:c2[1]].__contains__("*"):
                continue
            if np.unique(maze[c1[0] - 1, c1[1]:c2[1]]).size == 1 and \
                    maze[c1[0] - 1, c1[1]: c2[1]].__contains__('#'):
                maze[c1[0], c1[1]:c2[1]] = 'T'
                continue
            if np.unique(maze[c1[0] + 1, c1[1]:c2[1]]).size == 1 and \
                    maze[c1[0] + 1, c1[1]: c2[1]].__contains__('#'):
                maze[c1[0], c1[1]:c2[1]] = 'T'
                continue

        y_pairs = same_y_pair(corners)
        for c1, c2 in y_pairs:
            if maze[c1[0]:c2[0], c1[1]].__contains__("#") or maze[c1[0]:c2[0], c1[1]].__contains__(".") \
                    or maze[c1[0]:c2[0], c1[1]].__contains__("*"):
                continue
            if np.unique(maze[c1[0]:c2[0], c1[1]-1]).size == 1 and \
                    maze[c1[0]:c2[0], c1[1]-1].__contains__('#'):
                maze[c1[0]:c2[0], c1[1]] = 'T'
                continue
            if np.unique(maze[c1[0]:c2[0], c1[1]+1]).size == 1 and \
                    maze[c1[0]:c2[0], c1[1]+1].__contains__('#'):
                maze[c1[0]:c2[0], c1[1]] = 'T'
                continue

        np.savetxt('Maze.txt', X=maze, fmt='%s')
        self.taboo_cells = list(zip(*np.where(maze == 'T')))


obj = Maze('input.txt')
