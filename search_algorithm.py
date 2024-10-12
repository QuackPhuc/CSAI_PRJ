import time
import os

class SearchAlgorithm:
    def __init__(self, maze):
        self.maze = maze
        self.solution = None
        self.stats = {}

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

class BFS(SearchAlgorithm):
    def solve(self):
        start_time = time.time()
        # Implement BFS here, this is just a mockup example
        # Let's assume the solution found is moving up and right only
        self.solution = "uurr"
        self.stats['steps'] = len(self.solution)
        self.stats['weight'] = 100  # Mocked weight
        self.stats['nodes'] = 500  # Mocked nodes generated
        self.stats['time'] = (time.time() - start_time) * 1000  # Time in ms
        self.stats['memory'] = 10.0  # Mocked memory usage in MB
        return self.solution

class DFS(SearchAlgorithm):
    def solve(self):
        start_time = time.time()
        # Implement DFS here
        self.solution = "ddll"
        self.stats['steps'] = len(self.solution)
        self.stats['weight'] = 150  # Mocked weight
        self.stats['nodes'] = 800  # Mocked nodes generated
        self.stats['time'] = (time.time() - start_time) * 1000
        self.stats['memory'] = 12.0  # Mocked memory usage in MB
        return self.solution

class UCS(SearchAlgorithm):
    def solve(self):
        start_time = time.time()
        # Implement UCS here
        self.solution = "udlr"
        self.stats['steps'] = len(self.solution)
        self.stats['weight'] = 200  # Mocked weight
        self.stats['nodes'] = 1000  # Mocked nodes generated
        self.stats['time'] = (time.time() - start_time) * 1000
        self.stats['memory'] = 15.0  # Mocked memory usage in MB
        return self.solution

class AStar(SearchAlgorithm):
    def __init__(self, maze, heuristic):
        super().__init__(maze)
        self.heuristic = heuristic  # Heuristic function

    def solve(self):
        start_time = time.time()
        # Implement A* Search here using the heuristic
        self.solution = "rlud"
        self.stats['steps'] = len(self.solution)
        self.stats['weight'] = 250  # Mocked weight
        self.stats['nodes'] = 1200  # Mocked nodes generated
        self.stats['time'] = (time.time() - start_time) * 1000
        self.stats['memory'] = 18.0  # Mocked memory usage in MB
        return self.solution

# Example usage
if __name__ == "__main__":
    # Load a maze (this is mocked as an empty grid here)
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

    # DFS Example
    dfs_solver = DFS(mock_maze)
    dfs_solver.solve()
    dfs_solver.save("dfs_custom_solution.txt")  # Custom filepath

    # UCS Example
    ucs_solver = UCS(mock_maze)
    ucs_solver.solve()
    ucs_solver.save()

    # A* Example with a mock heuristic function
    def mock_heuristic(state):
        return 1  # Mock heuristic function
    astar_solver = AStar(mock_maze, heuristic=mock_heuristic)
    astar_solver.solve()
    astar_solver.save()
