import tkinter as tk
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename
from Get_Maze import Maze
from Search_path import SokobanProblem, Try_to_Solve
import threading
import os
import time
import tracemalloc

app_root_folder = os.getcwd()

WALL = '#'
FREE = ' '
STONE = '$'
ARES = '@'
SWITCH = '.'
STONE_ON_SWITCH = '*'
ARES_ON_SWITCH = '+'

class MazeGUI:
    def __init__(self, root: tk.Tk):
        self.solution = []
        self.cells = dict()
        self.root = root
        self.root.title("Ares' Maze Adventure")
        self.maze = None
        self.maze_map = []
        self.maze_path = None
        self.chosen_Solution = 'bfs'
        self.grid_size = ()
        self.steps_taken = 0
        self.pushed_weight = 0
        self.solution_stt = ' '
        self.is_paused = False  # Track whether playback is paused
        self.stop_thread = False
        self.solving_thread = None  # Track the solving thread

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize canvas and UI components
        self.canvas = tk.Canvas(self.root, width=800, height=800)
        self.canvas.pack()

        self.load_button = tk.Button(self.root, text="Load Maze", command=self.Load_maze)
        self.load_button.pack(side=tk.LEFT)

        self.solve_button = tk.Button(self.root, text="Solve", command=self.start_solving_thread)
        self.solve_button.pack(side=tk.LEFT)

        self.algorithms = ["BFS", "DFS", "UCS", "A*"]
        self.selected_algorithm = tk.StringVar(self.root)
        self.selected_algorithm.set(self.algorithms[0])  # Default to BFS
        self.algorithm_menu = tk.OptionMenu(self.root, self.selected_algorithm, *self.algorithms)
        self.algorithm_menu.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.Pause)
        self.pause_button.pack(side=tk.LEFT)

        self.restart_button = tk.Button(self.root, text="Restart", command=self.restart)
        self.restart_button.pack(side=tk.LEFT)

        self.steps_label = tk.Label(self.root, text=f"Steps Taken: {self.steps_taken}")
        self.steps_label.pack(side=tk.LEFT)

        self.weight_label = tk.Label(self.root, text=f"Pushed Weight: {self.pushed_weight}")
        self.weight_label.pack(side=tk.LEFT)

        self.able_to_solve_label = tk.Label(self.root, text=f"Solution status: {self.solution_stt}")
        self.able_to_solve_label.pack(side=tk.LEFT)

        self.current_move_index = 0
        self.images = dict()
        self.cells_with_image = dict()

    def make_cell(self, x, y, cell_size, cell_type, box_weight=None):
        background_image = self.images[cell_type.upper()]
        self.canvas.create_image(x * cell_size, y * cell_size, anchor=tk.NW, image=background_image)
        if box_weight is not None:
            self.canvas.create_text((x + 0.5) * cell_size, (y + 0.5) * cell_size, text=str(box_weight),
                                    fill="black", font='Helvetica 15 bold')

    def update_status_labels(self):
        self.steps_label.config(text=f"Steps Taken: {self.steps_taken}")
        self.weight_label.config(text=f"Pushed Weight: {self.pushed_weight}")
        self.able_to_solve_label.config(text=f'Solution status: {self.solution_stt}')

    def Load_maze(self):
        self.canvas.delete('all')
        self.maze_path = askopenfilename(initialdir=app_root_folder)
        self.maze = Maze(self.maze_path)

        self.maze_map = [["" for _ in range(self.maze.ncols)] for _ in range(self.maze.nrows)]
        for i in range(self.maze.nrows):
            for j in range(self.maze.ncols):
                if (i, j) == self.maze.Ares:
                    self.maze_map[i][j] = ARES
                elif (i, j) in self.maze.Stones:
                    self.maze_map[i][j] = STONE
                elif (i, j) in self.maze.Switches:
                    self.maze_map[i][j] = SWITCH
                elif (i, j) in self.maze.Walls:
                    self.maze_map[i][j] = WALL
                else:
                    self.maze_map[i][j] = FREE

        self.draw_maze()
        self.current_move_index = 0
        self.steps_taken = 0
        self.pushed_weight = 0
        self.solution_stt = ' '
        self.is_paused = False
        self.update_status_labels()

    def draw_maze(self):
        self.root.title(f'{self.maze_path.split("/")[-1]}')
        self.grid_size = (self.maze.nrows, self.maze.ncols)
        cell_size = 800 // max(self.grid_size)

        self.images = {
            'WALL': ImageTk.PhotoImage(Image.open('IMG/Wall.png').resize((cell_size, cell_size))),
            'FREE': ImageTk.PhotoImage(Image.open('IMG/Nothing.png').resize((cell_size, cell_size))),
            'STONE': ImageTk.PhotoImage(Image.open('IMG/Stone.png').resize((cell_size, cell_size))),
            'ARES': ImageTk.PhotoImage(Image.open('IMG/Ares.png').resize((cell_size, cell_size))),
            'SWITCH': ImageTk.PhotoImage(Image.open('IMG/Switch.png').resize((cell_size, cell_size))),
            'STONE_ON_SWITCH': ImageTk.PhotoImage(Image.open('IMG/Stone_Switch.png').resize((cell_size, cell_size))),
            'ARES_ON_SWITCH': ImageTk.PhotoImage(Image.open('IMG/Ares_Switch.png').resize((cell_size, cell_size))),
        }

        # Draw maze components
        for y, x in self.maze.Walls:
            self.make_cell(x, y, cell_size, 'WALL')
        for i, (y, x) in enumerate(self.maze.Stones):
            cell_type = 'STONE_ON_SWITCH' if (y, x) in self.maze.Switches else 'STONE'
            self.make_cell(x, y, cell_size, cell_type, self.maze.Stones_Weight[i])
        for y, x in self.maze.Switches:
            if (x, y) not in self.maze.Stones:
                self.make_cell(x, y, cell_size, 'SWITCH')
        y, x = self.maze.Ares
        ares_cell_type = 'ARES_ON_SWITCH' if (x, y) in self.maze.Switches else 'ARES'
        self.make_cell(x, y, cell_size, ares_cell_type)

    def reset(self):
        self.current_move_index = 0
        self.solution_stt = ' '
        self.steps_taken = 0
        self.pushed_weight = 0
        self.is_paused = False
        self.update_status_labels()
        self.Load_maze()

    def restart(self):
        self.stop_thread = True
        self.reset()
        self.solution = []
        self.update_status_labels()

    def start_solving_thread(self):
        # Disable solve button while solving
        self.solve_button.config(state=tk.DISABLED)
        # Đặt lại cờ `stop_thread` trước khi bắt đầu tiến trình mới
        self.stop_thread = False
        # Start solving in a separate thread
        self.solving_thread = threading.Thread(target=self.Solve)
        self.solving_thread.start()

    def Solve(self):
        if self.stop_thread:
            return
        
        tts = Try_to_Solve(self.maze, self.selected_algorithm.get())
        if tts['path'] is None:
            self.solution_stt = 'No Solution'
        else:
            self.solution_stt = 'Have Solution'
            self.solution = tts['path']
            self.is_paused = False  # Reset pause state
            self.Play_solution()
        # Re-enable solve button and update UI
        self.solve_button.config(state=tk.NORMAL)
        self.update_status_labels()
    
    def move_ares(self, move):
        if move == 'u':
            dx, dy = -1, 0
        elif move == 'd':
            dx, dy = 1, 0
        elif move == 'l':
            dx, dy = 0, -1
        elif move == 'r':
            dx, dy = 0, 1
        elif move == 'U':
            dx, dy = -1, 0
        elif move == 'D':
            dx, dy = 1, 0
        elif move == 'L':
            dx, dy = 0, -1
        elif move == 'R':
            dx, dy = 0, 1
        
        # Current position of Ares
        i, j = self.maze.Ares[0], self.maze.Ares[1]
        new_x, new_y = i + dx, j + dy

        if new_x < 0 or new_x >= self.grid_size[0] or new_y < 0 or new_y >= self.grid_size[1]:
            return

        # Get the content of the new cell
        new_cell = self.maze_map[new_x][new_y]

        # Case 1: Free space or switch (Ares can move)
        if new_cell == FREE or new_cell == SWITCH:
            self.update_position(i, j, new_x, new_y, ARES_ON_SWITCH if new_cell == SWITCH else ARES)
            self.maze.Ares = (new_x, new_y)

        # Case 2: Stone (Ares can push if space behind it is free)
        elif new_cell == STONE or new_cell == STONE_ON_SWITCH:
            stone_new_x, stone_new_y = new_x + dx, new_y + dy

            # Check if the space behind the stone is free or a switch
            if self.maze_map[stone_new_x][stone_new_y] == FREE or self.maze_map[stone_new_x][stone_new_y] == SWITCH:
                self.update_position(new_x, new_y, stone_new_x, stone_new_y,
                                                    STONE_ON_SWITCH if self.maze_map[stone_new_x][
                                                                            stone_new_y] == SWITCH else STONE)
                
                self.pushed_weight += self.maze.Stones_Weight[self.maze.Stones.index((new_x, new_y))]

                self.maze.Stones = list(self.maze.Stones)
                self.maze.Stones[self.maze.Stones.index((new_x, new_y))] = (stone_new_x, stone_new_y)
                self.maze.Stones = tuple(self.maze.Stones)

                self.update_position(i, j, new_x, new_y, ARES)
                self.maze.Ares = (new_x, new_y)
                    
        self.steps_taken += 1    
        return

    def update_position(self, old_x, old_y, new_x, new_y, new_value):
        if self.maze_map[old_x][old_y] == ARES:
            self.maze_map[old_x][old_y] = FREE 
        else:
            self.maze_map[old_x][old_y] = SWITCH

        self.maze_map[new_x][new_y] = new_value
        self.draw_maze()

    def Play_solution(self):
        if self.is_paused or self.current_move_index >= len(self.solution):
            return
        
        self.move_ares(self.solution[self.current_move_index])
        self.update_status_labels()
        self.root.after(500, self.Play_solution)
        self.current_move_index += 1

    def Pause(self):
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.Play_solution()
    
    def on_closing(self):
        # Đặt cờ `stop_thread` để dừng các tiến trình phụ
        self.stop_thread = True
        if self.solving_thread and self.solving_thread.is_alive():
            self.solving_thread.join()  # Đợi luồng hoàn tất nếu còn đang chạy
        self.root.destroy()  # Đóng hoàn toàn giao diện

if __name__ == '__main__':
    root_window = tk.Tk()
    app = MazeGUI(root_window)
    root_window.mainloop()
