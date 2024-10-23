import tkinter as tk
from tkinter import filedialog, messagebox
import time
from PIL import Image, ImageTk
from Search_path import depth_first_search, breadth_first_search, uniform_cost_search, a_star_search, sokoban
# Define the symbols used in the maze
WALL = '#'
FREE = ' '
STONE = '$'
ARES = '@'
SWITCH = '.'
STONE_ON_SWITCH = '*'
ARES_ON_SWITCH = '+'


class MazeGUI:
    def __init__(self, root):
        self.images = None
        self.cell_size = None
        self.root = root
        self.root.title("Ares' Maze Adventure")
        self.maze = []
        self.stone_weights = []
        self.grid_size = (0, 0)
        self.user_moves = []  # Store user moves

        # Create a Canvas to hold the maze
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack()

        # Add control buttons
        self.load_button = tk.Button(self.root, text="Load Maze", command=self.load_maze)
        self.load_button.pack(side=tk.LEFT)

        self.solve_button = tk.Button(self.root, text="Solve", command=self.auto_solve)
        self.solve_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.root, text="Save", command=self.save_output)
        self.save_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_maze)
        self.reset_button.pack(side=tk.LEFT)

        # Drop-down to select search algorithm
        self.algorithms = ["BFS", "DFS", "UCS", "A*"]
        self.selected_algorithm = tk.StringVar(self.root)
        self.selected_algorithm.set(self.algorithms[0])  # Default to BFS
        self.algorithm_menu = tk.OptionMenu(self.root, self.selected_algorithm, *self.algorithms)
        self.algorithm_menu.pack(side=tk.LEFT)

        # Bind keyboard events for manual control
        self.root.bind("<w>", lambda event: self.move_ares(-1, 0, 'u'))  # W key for moving up
        self.root.bind("<s>", lambda event: self.move_ares(1, 0, 'd'))  # S key for moving down
        self.root.bind("<a>", lambda event: self.move_ares(0, -1, 'l'))  # A key for moving left
        self.root.bind("<d>", lambda event: self.move_ares(0, 1, 'r'))  # D key for moving right

        self.maze_data = None  # Store initial state of the maze for reset3

    def load_maze(self):
        # Open file dialog to load the maze input file
        file_path = filedialog.askopenfilename(title="Select Maze Input File")
        if not file_path:
            return

        with open(file_path, 'r') as file:
            # Read stone weights
            self.stone_weights = list(map(int, file.readline().strip().split()))

            # Read the maze layout
            self.maze = [list(line.rstrip()) for line in file.readlines()]
            self.grid_size = (len(self.maze), len(self.maze[0]))

            # Save a copy of the maze for reset functionality
            self.maze_data = [row[:] for row in self.maze]

        self.draw_maze()
        self.user_moves.clear()  # Clear user moves

    def draw_maze(self):
        self.canvas.delete("all")
        self.cell_size = 600 // max(self.grid_size)  # Calculate the size of each grid cell based on the canvas size

        self.images = {
            WALL: ImageTk.PhotoImage(Image.open('IMG/Wall.png').resize((self.cell_size, self.cell_size))),
            FREE: ImageTk.PhotoImage(Image.open('IMG/Nothing.png').resize((self.cell_size, self.cell_size))),
            STONE: ImageTk.PhotoImage(Image.open('IMG/Stone.png').resize((self.cell_size, self.cell_size))),
            ARES: ImageTk.PhotoImage(Image.open('IMG/Ares.png').resize((self.cell_size, self.cell_size))),
            SWITCH: ImageTk.PhotoImage(Image.open('IMG/Goal.png').resize((self.cell_size, self.cell_size))),
            STONE_ON_SWITCH: ImageTk.PhotoImage(Image.open('IMG/Stone.png').resize((self.cell_size, self.cell_size))),
            ARES_ON_SWITCH: ImageTk.PhotoImage(Image.open('IMG/Ares.png').resize((self.cell_size, self.cell_size))),
        }
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                x1, y1 = j * self.cell_size, i * self.cell_size

                # Use images instead of colors
                if cell in self.images:
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.images[cell])

    def move_ares(self, dx, dy, move_char):
        # Find current position of Ares
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                if cell == ARES or cell == ARES_ON_SWITCH:
                    new_x, new_y = i + dx, j + dy

                    # Check boundaries
                    if new_x < 0 or new_x >= self.grid_size[0] or new_y < 0 or new_y >= self.grid_size[1]:
                        return

                    # Get the content of the new cell
                    new_cell = self.maze[new_x][new_y]

                    # Case 1: Free space or switch (Ares can move)
                    if new_cell == FREE or new_cell == SWITCH:
                        self.update_position(i, j, new_x, new_y, ARES_ON_SWITCH if new_cell == SWITCH else ARES)
                        self.user_moves.append(move_char)  # Track the move

                    # Case 2: Stone (Ares can push if space behind it is free)
                    elif new_cell == STONE or new_cell == STONE_ON_SWITCH:
                        stone_new_x, stone_new_y = new_x + dx, new_y + dy

                        # Check if the space behind the stone is free or a switch
                        if self.maze[stone_new_x][stone_new_y] == FREE or self.maze[stone_new_x][stone_new_y] == SWITCH:
                            self.update_position(new_x, new_y, stone_new_x, stone_new_y,
                                                 STONE_ON_SWITCH if self.maze[stone_new_x][
                                                                        stone_new_y] == SWITCH else STONE)
                            self.update_position(i, j, new_x, new_y, ARES)
                            self.user_moves.append(move_char.upper())  # Track the push

                    return  # After moving Ares, stop further iterations

    def update_position(self, old_x, old_y, new_x, new_y, new_value):
        # Reset the old position (restore switch or free space)
        self.maze[old_x][old_y] = FREE if self.maze[old_x][old_y] == ARES else SWITCH

        # Set the new position
        self.maze[new_x][new_y] = new_value

        # Redraw the maze
        self.draw_maze()

    def reset_maze(self):
        # Check if maze_data is available
        if self.maze_data is None:
            print("No maze loaded to reset.")
            return

        # Reset the maze to its initial state
        self.maze = [row[:] for row in self.maze_data]
        self.user_moves.clear()
        self.draw_maze()

    def auto_solve(self):
        # Auto-solve using selected algorithm
        algorithm = self.selected_algorithm.get()
        if algorithm == "BFS":
            solver = BFS(self.maze)
        elif algorithm == "DFS":
            solver = DFS(self.maze)
        elif algorithm == "UCS":
            solver = UCS(self.maze)
        elif algorithm == "A*":
            def mock_heuristic(state):
                return 1  # Dummy heuristic function

            solver = AStar(self.maze, heuristic=mock_heuristic)

        # Solve the maze and get the solution moves
        solution_moves = solver.solve()

        # Simulate Ares' movements in the GUI
        for move in solution_moves:
            if move == 'u':
                self.move_ares(-1, 0, 'u')
            elif move == 'd':
                self.move_ares(1, 0, 'd')
            elif move == 'l':
                self.move_ares(0, -1, 'l')
            elif move == 'r':
                self.move_ares(0, 1, 'r')
            elif move == 'U':
                self.move_ares(-1, 0, 'U')
            elif move == 'D':
                self.move_ares(1, 0, 'D')
            elif move == 'L':
                self.move_ares(0, -1, 'L')
            elif move == 'R':
                self.move_ares(0, 1, 'R')
            self.root.update()
            time.sleep(0.2)  # Delay to animate movement

        self.user_moves.extend(list(solution_moves))  # Save the solution moves

    def save_output(self):
        # Save the user's moves and the solution to an output file
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write("".join(self.user_moves))
            messagebox.showinfo("Save", f"Moves saved to {file_path}")


# Example search algorithms with dummy implementations

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGUI(root)
    root.mainloop()
