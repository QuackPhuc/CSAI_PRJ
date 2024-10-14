import time
import os
from queue import Queue, PriorityQueue

class SearchAlgorithm:
    def __init__(self, maze):
        self.maze = maze
        self.solution = None
        self.stats = {}
        self.start = self.find_start()  # Tìm vị trí bắt đầu của Ares

    def find_start(self):
        # Tìm vị trí của Ares (ký tự '@') trong mê cung
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                if cell == '@':
                    return (i, j)
        raise ValueError("Start position '@' not found in the maze")

    def is_valid_move(self, x, y):
        # Kiểm tra xem bước đi có hợp lệ không (không vượt biên và không đi vào tường)
        return 0 <= x < len(self.maze) and 0 <= y < len(self.maze[0]) and self.maze[x][y] != '#'

    def solve(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def save(self, filepath=None):
        if self.solution is None:
            print("No solution found yet. Run solve() first.")
            return
        
        # Determine default filename based on the class name
        if filepath is None:
            filepath = f"{self.__class__.__name__.lower()}_solve.txt"
        
        with open(filepath, 'w') as f:
            f.write(f"{self.__class__.__name__}\n")
            f.write(f"Steps: {self.stats['steps']}, Weight: {self.stats['weight']}, "
                    f"Nodes: {self.stats['nodes']}, Time (ms): {self.stats['time']:.2f}, "
                    f"Memory (MB): {self.stats['memory']:.2f}\n")
            f.write(self.solution + "\n")
        
        print(f"Solution saved to {filepath}")


# Breadth-First Search (BFS)
class BFS(SearchAlgorithm):
    def solve(self):
        start_time = time.time()
        queue = Queue()
        queue.put((self.find_start(), []))  # (Position, Path)
        visited = set()
        visited.add(self.find_start())
        node_count = 0
        
        while not queue.empty():
            (x, y), path = queue.get()
            if self.maze[x][y] == '.':  # Goal found
                self.solution = ''.join(path)
                self.stats = {
                    'steps': len(path),
                    'weight': 0,  # No weight consideration for BFS
                    'nodes': node_count,
                    'time': (time.time() - start_time) * 1000,
                    'memory': 0  # Placeholder for memory usage
                }
                return self.solution
            
            node_count += 1
            # Explore neighbors (Up, Down, Left, Right)
            for dx, dy, move in [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_move(new_x, new_y) and (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.put(((new_x, new_y), path + [move]))

        return None  # No solution found

# Depth-First Search (DFS)
class DFS(SearchAlgorithm):
    def solve(self):
        start_time = time.time()
        stack = [(self.find_start(), [])]
        visited = set()
        visited.add(self.find_start())
        node_count = 0
        
        while stack:
            (x, y), path = stack.pop()
            if self.maze[x][y] == '.':  # Goal found
                self.solution = ''.join(path)
                self.stats = {
                    'steps': len(path),
                    'weight': 0,  # No weight consideration for DFS
                    'nodes': node_count,
                    'time': (time.time() - start_time) * 1000,
                    'memory': 0  # Placeholder for memory usage
                }
                return self.solution
            
            node_count += 1
            # Explore neighbors (Up, Down, Left, Right)
            for dx, dy, move in [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_move(new_x, new_y) and (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    stack.append(((new_x, new_y), path + [move]))

        return None  # No solution found

# Uniform Cost Search (UCS)
class UCS(SearchAlgorithm):
    def __init__(self, maze, weights):
        super().__init__(maze)
        self.weights = weights  # Dictionary of weights for stones

    def solve(self):
        start_time = time.time()
        pq = PriorityQueue()
        pq.put((0, self.find_start(), []))  # (Cost, Position, Path)
        visited = {}
        node_count = 0
        
        while not pq.empty():
            cost, (x, y), path = pq.get()
            if self.maze[x][y] == '.':  # Goal found
                self.solution = ''.join(path)
                self.stats = {
                    'steps': len(path),
                    'weight': cost,  # Total weight pushed
                    'nodes': node_count,
                    'time': (time.time() - start_time) * 1000,
                    'memory': 0  # Placeholder for memory usage
                }
                return self.solution

            if (x, y) in visited and visited[(x, y)] <= cost:
                continue
            visited[(x, y)] = cost
            node_count += 1

            # Explore neighbors (Up, Down, Left, Right)
            for dx, dy, move in [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_move(new_x, new_y):
                    # Add weight if pushing stone
                    new_cost = cost + (self.weights.get((new_x, new_y), 1))  # Default weight is 1
                    pq.put((new_cost, (new_x, new_y), path + [move]))

        return None  # No solution found

# A* Search
class AStar(SearchAlgorithm):
    def __init__(self, maze, heuristic):
        super().__init__(maze)
        self.heuristic = heuristic  # Heuristic function

    def solve(self):
        start_time = time.time()
        pq = PriorityQueue()
        pq.put((self.heuristic(self.find_start()), 0, self.find_start(), []))  # (Heuristic + Cost, Cost, Position, Path)
        visited = {}
        node_count = 0
        
        while not pq.empty():
            priority, cost, (x, y), path = pq.get()
            if self.maze[x][y] == '.':  # Goal found
                self.solution = ''.join(path)
                self.stats = {
                    'steps': len(path),
                    'weight': cost,  # Total weight pushed
                    'nodes': node_count,
                    'time': (time.time() - start_time) * 1000,
                    'memory': 0  # Placeholder for memory usage
                }
                return self.solution

            if (x, y) in visited and visited[(x, y)] <= cost:
                continue
            visited[(x, y)] = cost
            node_count += 1

            # Explore neighbors (Up, Down, Left, Right)
            for dx, dy, move in [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_move(new_x, new_y):
                    new_cost = cost + (self.weights.get((new_x, new_y), 1))  # Default weight is 1
                    priority = new_cost + self.heuristic((new_x, new_y))
                    pq.put((priority, new_cost, (new_x, new_y), path + [move]))

        return None  # No solution found

# Helper methods for searching
class MazeHelper:
    @staticmethod
    def find_start(maze):
        for i, row in enumerate(maze):
            for j, cell in enumerate(row):
                if cell == '@':
                    return (i, j)

    @staticmethod
    def is_valid_move(maze, x, y):
        return 0 <= x < len(maze) and 0 <= y < len(maze[0]) and maze[x][y] != '#'

# Example heuristic for A* (Manhattan distance)
def manhattan_distance(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

# Example usage
if __name__ == "__main__":
    mock_maze = [
        ['#', '#', '#', '#', '#'],
        ['#', ' ', ' ', '$', '#'],
        ['#', ' ', '@', ' ', '#'],
        ['#', '.', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#']
    ]

    # BFS Example
    bfs_solver = BFS(mock_maze)
    bfs_solver.solve()
    bfs_solver.save()

