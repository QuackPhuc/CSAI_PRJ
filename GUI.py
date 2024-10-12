import tkinter as tk
from tkinter import filedialog

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
        self.root = root
        self.root.title("Ares' Maze Adventure")
        self.maze = []
        self.stone_weights = []
        self.grid_size = (0, 0)
        
        # Create a Canvas to hold the maze
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack()
        
        # Add buttons for control
        self.load_button = tk.Button(self.root, text="Load Maze", command=self.load_maze)
        self.load_button.pack(side=tk.LEFT)
        
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_maze)
        self.reset_button.pack(side=tk.LEFT)
        
        # Bind keyboard events to control Ares' movement
        self.root.bind("<w>", lambda event: self.move_ares(-1, 0))  # W key for moving up
        self.root.bind("<s>", lambda event: self.move_ares(1, 0))   # S key for moving down
        self.root.bind("<a>", lambda event: self.move_ares(0, -1))  # A key for moving left
        self.root.bind("<d>", lambda event: self.move_ares(0, 1))   # D key for moving right
        
        self.maze_data = None  # To store initial state of the maze for reset
    
    def load_maze(self):
        # Open file dialog to load the maze input file
        file_path = filedialog.askopenfilename(title="Select Maze Input File")
        if not file_path:
            return
        
        with open(file_path, 'r') as file:
            # Read stone weights
            self.stone_weights = list(map(int, file.readline().strip().split()))
            
            # Read the maze layout
            self.maze = [list(line.strip()) for line in file.readlines()]
            self.grid_size = (len(self.maze), len(self.maze[0]))
            
            # Save a copy of the maze for reset functionality
            self.maze_data = [row[:] for row in self.maze]
        
        self.draw_maze()
    
    def draw_maze(self):
        self.canvas.delete("all")
        cell_size = 600 // max(self.grid_size)  # Calculate the size of each grid cell based on the canvas size
        
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                color = self.get_color_for_cell(cell)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')
                
                if cell == ARES or cell == ARES_ON_SWITCH:
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="A", fill="white")
                elif cell == STONE or cell == STONE_ON_SWITCH:
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="S", fill="black")
    
    def get_color_for_cell(self, cell):
        if cell == WALL:
            return "black"
        elif cell == FREE:
            return "white"
        elif cell == STONE or cell == STONE_ON_SWITCH:
            return "brown"
        elif cell == ARES or cell == ARES_ON_SWITCH:
            return "blue"
        elif cell == SWITCH:
            return "green"
        return "white"
    
    def move_ares(self, dx, dy):
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
                    
                    # Case 2: Stone (Ares can push if space behind it is free)
                    elif new_cell == STONE or new_cell == STONE_ON_SWITCH:
                        stone_new_x, stone_new_y = new_x + dx, new_y + dy
                        
                        # Check if the space behind the stone is free or a switch
                        if self.maze[stone_new_x][stone_new_y] == FREE or self.maze[stone_new_x][stone_new_y] == SWITCH:
                            self.update_position(new_x, new_y, stone_new_x, stone_new_y, 
                                                STONE_ON_SWITCH if self.maze[stone_new_x][stone_new_y] == SWITCH else STONE)
                            self.update_position(i, j, new_x, new_y, ARES)
                    
                    return  # After moving Ares, stop further iterations

    def update_position(self, old_x, old_y, new_x, new_y, new_value):
        # Reset the old position (restore switch or free space)
        self.maze[old_x][old_y] = FREE if self.maze[old_x][old_y] == ARES else SWITCH
        
        # Set the new position
        self.maze[new_x][new_y] = new_value
        
        # Redraw the maze
        self.draw_maze()
    
    def reset_maze(self):
        # Reset the maze to its initial state
        self.maze = [row[:] for row in self.maze_data]
        self.draw_maze()

# Main loop to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGUI(root)
    root.mainloop()
