from Get_Maze import Maze
from Search_path import Try_to_Solve
import multiprocessing

def solve_maze(file_path, algo, queue):
    """
    Hàm giải quyết mê cung với thuật toán và file path được chỉ định.
    Thêm kết quả vào queue để tiến trình chính lấy ra.
    """
    maze = Maze(file_path)
    try:
        path = Try_to_Solve(maze, algo)
        result = (file_path, algo, path)
    except Exception as e:
        result = (file_path, algo, f"Error: {e}\nNo path found")
    queue.put(result)

if __name__ == '__main__':
    # Danh sách các file input và thuật toán cần chạy
    file_paths = [ 'input/input-07.txt']
    algorithms = ['A*', 'UCS','DFS','BFS']

    # Tạo một hàng đợi để lưu trữ kết quả từ các tiến trình
    queue = multiprocessing.Queue()
    processes = []

    # Tạo và khởi chạy tiến trình cho mỗi (file_path, thuật toán) cặp
    for file_path in file_paths:
        for algo in algorithms:
            p = multiprocessing.Process(target=solve_maze, args=(file_path, algo, queue))
            processes.append(p)
            p.start()

    # Đợi tất cả các tiến trình hoàn thành
    for p in processes:
        p.join()

    # Lấy và in kết quả từ queue
    while not queue.empty():
        file_path, algo, result = queue.get()
        print(f'File: {file_path} - Algorithm: {algo}')
        print(f'Result: {result}\n')
