import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from Get_Maze import Maze
import os
from Search_path import run_solver
import multiprocessing

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
        self.is_paused = False
        self.solve_process = None
        self.solve_result = None
        self.pipe = None
        self.GUI_WIDTH = 600
        self.GUI_HEIGHT = 600

        self.root.protocol("WM_DELETE_WINDOW", self.On_closing)

        self.canvas = tk.Canvas(self.root, width=self.GUI_WIDTH, height=self.GUI_HEIGHT)
        self.canvas.pack()

        self.load_button = tk.Button(self.root, text="Load Maze", command=self.Toggle_load)
        self.load_button.pack(side=tk.LEFT)

        self.solve_button = tk.Button(self.root, text="Solve", command=self.Toggle_solve)
        self.solve_button.pack(side=tk.LEFT)

        self.algorithms = ["BFS", "DFS", "UCS", "A*"]
        self.selected_algorithm = tk.StringVar(self.root)
        self.selected_algorithm.set(self.algorithms[0])  # Default to BFS
        self.algorithm_menu = tk.OptionMenu(self.root, self.selected_algorithm, *self.algorithms)
        self.algorithm_menu.pack(side=tk.LEFT)

        self.start_button = tk.Button(self.root, text="Start", command=self.Toggle_play)
        self.start_button.pack(side=tk.LEFT)

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
                                    fill="black",
                                    font='Helvetica 15 bold')

    def update_status_labels(self):
        # Update the labels showing steps taken and pushed weight
        self.steps_label.config(text=f"Steps Taken: {self.steps_taken}")
        self.weight_label.config(text=f"Pushed Weight: {self.pushed_weight}")
        self.able_to_solve_label.config(text=f'Solution status: {self.solution_stt}')

    def Toggle_load(self):
        if self.maze is None:
            self.Load_maze()
            self.load_button.config(text="Reload Maze")
        else:
            reload = True
            if self.solve_process and self.solve_process.is_alive():
                reload = self.confirm_stop_solving()
            if reload:
                self.maze = None
                self.maze_map = []
                self.maze_path = None
                self.current_move_index = 0
                self.solution = []
                self.solution_stt = ' '
                self.steps_taken = 0
                self.pushed_weight = 0
                self.is_paused = False
                self.solve_process = None
                self.solve_result = None
                self.pipe = None
                self.selected_algorithm.set(self.algorithms[0])

                # reset button
                self.start_button.config(text="Start")
                self.solve_button.config(text="Solve")
                self.load_button.config(text="Load Maze")

                self.update_status_labels()
                self.Load_maze()

    def load_maze_map(self):
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

    def Load_maze(self):
        self.canvas.delete('all')
        self.maze_path = askopenfilename(initialdir=app_root_folder)

        self.maze = Maze(self.maze_path)
        self.load_maze_map()
        self.draw_maze() 
        
        self.current_move_index = 0
        self.steps_taken = 0
        self.pushed_weight = 0
        self.solution_stt = ' '
        self.update_status_labels()

    def draw_maze(self):
        self.root.title(f'{self.maze_path.split("/")[-1]}')
        self.grid_size = (self.maze.nrows, self.maze.ncols)
        cell_size = min(self.GUI_WIDTH, self.GUI_HEIGHT) // max(self.grid_size)

        self.images = {
            WALL: ImageTk.PhotoImage(Image.open('IMG/Wall.png').resize((cell_size, cell_size))),
            FREE: ImageTk.PhotoImage(Image.open('IMG/Nothing.png').resize((cell_size, cell_size))),
            STONE: ImageTk.PhotoImage(Image.open('IMG/Stone.png').resize((cell_size, cell_size))),
            ARES: ImageTk.PhotoImage(Image.open('IMG/Ares.png').resize((cell_size, cell_size))),
            SWITCH: ImageTk.PhotoImage(Image.open('IMG/Switch.png').resize((cell_size, cell_size))),
            STONE_ON_SWITCH: ImageTk.PhotoImage(Image.open('IMG/Stone_Switch.png').resize((cell_size, cell_size))),
            ARES_ON_SWITCH: ImageTk.PhotoImage(Image.open('IMG/Ares_Switch.png').resize((cell_size, cell_size))),
        }

        for i in range(self.maze.nrows):
            for j in range(self.maze.ncols):
                cell_type = self.maze_map[i][j]
                if cell_type in [STONE, STONE_ON_SWITCH]:
                    self.make_cell(j, i, cell_size, cell_type, box_weight=self.maze.Stones_Weight[self.maze.Stones.index((i, j))])
                else:
                    self.make_cell(j, i, cell_size, cell_type)


    def restart(self):
        self.current_move_index = 0
        self.steps_taken = 0
        self.pushed_weight = 0
        self.is_paused = False
        self.update_status_labels()

        self.canvas.delete('all')
        self.start_button.config(text="Start")
        
        self.maze = Maze(self.maze_path)
        self.load_maze_map()
        self.draw_maze()
        self.Pause()


    def Toggle_solve(self):
        if self.solve_process and self.solve_process.is_alive():
            self.confirm_stop_solving()
        else:
            self.start_solving()

    def start_solving(self):
        if not self.maze_path:
            messagebox.showwarning("Warning", "Please load a maze first.")
            return
        
        self.restart()
        self.solve_button.config(text="Stop Solving")
        self.solution_stt = "Solving..."
        self.update_status_labels()

        parent_conn, child_conn = multiprocessing.Pipe()
        self.pipe = parent_conn
        self.solve_process = multiprocessing.Process(target=run_solver, args=(self.maze_path, self.selected_algorithm.get(), child_conn))
        self.solve_process.start()

        self.root.after(100, self.check_solver)

    def check_solver(self):
        if self.pipe and self.pipe.poll():
            result = self.pipe.recv()
            if result and result['path'] is not None:
                self.solution_stt = 'Have Solution'
                self.solution = result['path']
                self.current_move_index = 0
            else:
                self.solution_stt = 'No Solution'
            self.update_status_labels()
            self.solve_button.config(text="Solve")
            self.solve_process = None
        elif self.solve_process and self.solve_process.is_alive():
            self.root.after(100, self.check_solver)

    def confirm_stop_solving(self):
        response = messagebox.askyesno("Confirm Stop", "Do you really want to stop solving?")
        if response:
            self.kill_solve()
            self.solve_button.config(text="Solve")
        return response

    def kill_solve(self):
        if self.solve_process and self.solve_process.is_alive():
            self.solve_process.terminate()
            self.solution_stt = "Solver Terminated"
            self.update_status_labels()
            self.solve_process = None

    def move_ares(self, move):
        move_char = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1),
                     'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        dx, dy = move_char[move]
        
        i, j = self.maze.Ares[0], self.maze.Ares[1]
        new_x, new_y = i + dx, j + dy

        if new_x < 0 or new_x >= self.grid_size[0] or new_y < 0 or new_y >= self.grid_size[1]:
            return
        
        new_cell = self.maze_map[new_x][new_y]
        if new_cell == FREE:
            self.update_position(i, j, new_x, new_y, ARES)
            self.maze.Ares = (new_x, new_y)
        elif  new_cell == SWITCH:
            self.update_position(i, j, new_x, new_y, ARES_ON_SWITCH)
            self.maze.Ares = (new_x, new_y)
        elif new_cell == STONE or new_cell == STONE_ON_SWITCH:
            stone_new_x, stone_new_y = new_x + dx, new_y + dy

            if self.maze_map[stone_new_x][stone_new_y] == FREE or self.maze_map[stone_new_x][stone_new_y] == SWITCH:
                if self.maze_map[stone_new_x][stone_new_y] == SWITCH:
                    self.update_position(new_x, new_y, stone_new_x, stone_new_y, STONE_ON_SWITCH)
                else:
                    self.update_position(new_x, new_y, stone_new_x, stone_new_y, STONE)
                
                self.pushed_weight += self.maze.Stones_Weight[self.maze.Stones.index((new_x, new_y))]

                self.maze.Stones = list(self.maze.Stones)
                self.maze.Stones[self.maze.Stones.index((new_x, new_y))] = (stone_new_x, stone_new_y)
                self.maze.Stones = tuple(self.maze.Stones)

                if self.maze_map[new_x][new_y] == SWITCH:
                    self.update_position(i, j, new_x, new_y, ARES_ON_SWITCH)
                else:
                    self.update_position(i, j, new_x, new_y, ARES)
                self.maze.Ares = (new_x, new_y)

        self.draw_maze()            
        self.steps_taken += 1
        return

    def update_position(self, old_x, old_y, new_x, new_y, new_value):
        if self.maze_map[old_x][old_y] == ARES:
            self.maze_map[old_x][old_y] = FREE 
        elif self.maze_map[old_x][old_y] == ARES_ON_SWITCH:
            self.maze_map[old_x][old_y] = SWITCH
        elif self.maze_map[old_x][old_y] == STONE:
            self.maze_map[old_x][old_y] = FREE
        else:
            self.maze_map[old_x][old_y] = SWITCH

        self.maze_map[new_x][new_y] = new_value

    def Play_solution(self):
        if self.solution_stt == 'No Solution' or self.is_paused:
            return
        if self.solution is None or self.current_move_index >= len(self.solution):
            return
        if self.solve_process and self.solve_process.is_alive():
            self.restart()
            return
        
        self.move_ares(self.solution[self.current_move_index])
        self.update_status_labels()
        self.root.after(1000, self.Play_solution)
        self.current_move_index += 1

    def Toggle_play(self):
        if self.solution_stt == 'No Solution' or self.solution_stt == ' ' or self.current_move_index >= len(self.solution):
            return
        if self.solve_process and self.solve_process.is_alive():
            return
        if self.current_move_index == 0 or self.is_paused:
            self.start_button.config(text="Pause")
            self.Start()
        else:
            self.start_button.config(text="Start")
            self.Pause()

    def Start(self):
        self.is_paused = False
        self.Play_solution()

    def Pause(self):
        self.is_paused = True

    def On_closing(self):
        if self.solve_process and self.solve_process.is_alive():
            self.solve_process.terminate()
        self.root.destroy()


if __name__ == '__main__':
    root_window = tk.Tk()
    app = MazeGUI(root_window)
    root_window.mainloop()
