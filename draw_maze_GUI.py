import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.filedialog import asksaveasfilename
import numpy as np
from PIL import ImageTk, Image

# Các ký hiệu trong ma trận
WALL = '#'
FREE = ' '
STONE = '$'
ARES = '@'
SWITCH = '.'
STONE_ON_SWITCH = '*'
ARES_ON_SWITCH = '+'

class MazeEditorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Maze Editor")
        self.grid_size = (10, 10)  # Kích thước mặc định
        self.current_item = FREE
        self.maze_map = np.full(self.grid_size, FREE)  # Ma trận trống ban đầu
        self.stone_weights = {}  # Từ điển lưu trọng số của Stone

        # Cấu hình GUI
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack()
        self.item_buttons = {}

        # Các nút item để vẽ
        self.items = {
            "Wall": WALL, "Free": FREE, "Stone": STONE, "Ares": ARES, 
            "Switch": SWITCH, "Stone on Switch": STONE_ON_SWITCH, "Ares on Switch": ARES_ON_SWITCH
        }
        for item, symbol in self.items.items():
            btn = tk.Button(self.root, text=item, command=lambda s=symbol: self.select_item(s))
            btn.pack(side=tk.LEFT)
            self.item_buttons[item] = btn

        # Khung nhập kích thước ma trận
        self.rows_entry = tk.Entry(self.root, width=5)
        self.rows_entry.insert(0, "10")
        self.rows_entry.pack(side=tk.LEFT)
        self.cols_entry = tk.Entry(self.root, width=5)
        self.cols_entry.insert(0, "10")
        self.cols_entry.pack(side=tk.LEFT)
        tk.Button(self.root, text="Create Grid", command=self.create_grid).pack(side=tk.LEFT)

        # Box nhập tên file và nút lưu
        self.file_name_entry = tk.Entry(self.root, width=15)
        self.file_name_entry.insert(0, "maze.txt")
        self.file_name_entry.pack(side=tk.LEFT)
        tk.Button(self.root, text="Save", command=self.save_to_file).pack(side=tk.LEFT)
        
        # Nút xóa
        tk.Button(self.root, text="Clear", command=self.clear_grid).pack(side=tk.LEFT)
        
        # Tạo grid ban đầu và thêm sự kiện
        self.create_grid()
        self.canvas.bind("<Button-1>", self.paint_cell)  # Nhấn chuột trái để vẽ
        self.canvas.bind("<B1-Motion>", self.paint_drag)  # Giữ và rê chuột để vẽ liên tục

    def select_item(self, symbol):
        """Chọn loại item để vẽ"""
        self.current_item = symbol
        # Yêu cầu nhập trọng số nếu là Stone
        if symbol == STONE:
            weight = simpledialog.askinteger("Input", f"Enter weight for {symbol}:", parent=self.root, minvalue=1)
            if weight is not None:
                self.stone_weight = weight
            else:
                self.current_item = FREE  # Nếu không nhập trọng số, trở lại chế độ trống
        else:
            self.stone_weight = None

    def create_grid(self):
        """Tạo ma trận mới với kích thước nhập vào"""
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            self.grid_size = (rows, cols)
            self.maze_map = np.full(self.grid_size, FREE)  # Reset lại ma trận
            self.stone_weights.clear()  # Reset lại trọng số các Stone
            self.draw_grid()  # Vẽ lại giao diện ma trận
        except ValueError:
            messagebox.showerror("Error", "Invalid grid size.")

    def draw_grid(self):
        """Vẽ lại ma trận trên GUI"""
        self.canvas.delete("all")  # Xóa canvas trước khi vẽ mới
        cell_size = min(600 // self.grid_size[0], 600 // self.grid_size[1])
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                x0, y0 = j * cell_size, i * cell_size
                x1, y1 = x0 + cell_size, y0 + cell_size
                color = "white" if self.maze_map[i, j] == FREE else "gray"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black", tags="cell")
                # Hiển thị trọng số cho Stone
                if self.maze_map[i, j] == STONE:
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(self.stone_weights.get((i, j), "")), tags="cell_text")
                else:
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=self.maze_map[i, j], tags="cell_text")
        self.canvas.tag_bind("cell", "<Button-1>", self.paint_cell)

    def paint_cell(self, event):
        """Vẽ item vào ô khi nhấn vào canvas"""
        self.update_cell(event)

    def paint_drag(self, event):
        """Vẽ item khi giữ và rê chuột"""
        self.update_cell(event)

    def update_cell(self, event):
        """Cập nhật trạng thái ô khi vẽ"""
        cell_size = min(600 // self.grid_size[0], 600 // self.grid_size[1])
        col = event.x // cell_size
        row = event.y // cell_size
        if 0 <= row < self.grid_size[0] and 0 <= col < self.grid_size[1]:
            self.maze_map[row, col] = self.current_item  # Cập nhật item vào ma trận
            # Gán trọng số cho Stone
            if self.current_item == STONE and self.stone_weight is not None:
                self.stone_weights[(row, col)] = self.stone_weight
            elif (row, col) in self.stone_weights:
                del self.stone_weights[(row, col)]  # Xóa trọng số nếu item bị đổi
            self.draw_grid()  # Vẽ lại ma trận

    def clear_grid(self):
        """Xóa các item đã vẽ trong ma trận"""
        self.maze_map = np.full(self.grid_size, FREE)
        self.stone_weights.clear()
        self.draw_grid()

    def save_to_file(self):
        """Lưu ma trận vào file txt"""
        file_name = self.file_name_entry.get().strip() or "maze.txt"
        try:
            with open(file_name, 'w') as file:
                # Lưu trọng số của từng Stone theo thứ tự
                weights = [str(self.stone_weights.get((i, j), 0)) for i in range(self.grid_size[0]) for j in range(self.grid_size[1]) if self.maze_map[i, j] == STONE]
                file.write(" ".join(weights) + "\n")  # Dòng trọng số
                # Lưu ma trận
                for row in self.maze_map:
                    file.write("".join(row) + "\n")
            messagebox.showinfo("Saved", f"File saved as {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = MazeEditorGUI(root)
    root.mainloop()
