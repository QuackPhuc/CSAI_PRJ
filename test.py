from collections import deque


# Define the BFS function
def bfs_2d_grid(grid, start_x, start_y, goal_x, goal_y):
    # Directions for moving in 4 possible ways: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Grid size
    rows = len(grid)
    cols = len(grid[0])

    # Queue to manage the BFS: stores current position and path taken to reach it
    queue = deque([((start_x, start_y), [(start_x, start_y)])])

    # Set of visited cells to avoid revisiting
    visited = set()
    visited.add((start_x, start_y))

    # While there are cells to explore
    while queue:
        (x, y), path = queue.popleft()

        # If the goal is reached, return the path
        if (x, y) == (goal_x, goal_y):
            print(f"Goal reached at: ({x}, {y})")
            return path

        # Explore all 4 possible directions
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            # Check if the new position is within the grid and not yet visited
            if 0 <= new_x < rows and 0 <= new_y < cols and (new_x, new_y) not in visited:
                if grid[new_x][new_y] == 0:  # Ensure the cell is traversable
                    queue.append(((new_x, new_y), path + [(new_x, new_y)]))
                    visited.add((new_x, new_y))

    # If the goal was not reached
    print("Goal not reachable")
    return None


# Example grid
grid = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0]
]

# Starting point (row 0, column 0) and goal point (row 4, column 4)
start_x, start_y = 0, 0
goal_x, goal_y = 4, 4

# Run BFS and get the path
path = bfs_2d_grid(grid, start_x, start_y, goal_x, goal_y)

# If a path is found, print it
if path:
    print("Path to goal:", path)
