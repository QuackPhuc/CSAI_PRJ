import time
import tracemalloc
from multiprocessing import Process, Pipe
from Search_path import Node, FIFOQueue, SokobanProblem

def bfs_direction(problem, conn):
    # Initialize the BFS queue and starting node
    frontier = FIFOQueue()
    initial_node = Node(problem.initial_state)
    frontier.append(initial_node)
    explored = set()
    total_nodes = 1
    
    while frontier:
        node = frontier.pop()
        
        # Check if the goal is reached
        if problem.goal_test(node.State):
            conn.send((node, total_nodes))
            conn.close()
            return
        
        # Mark the node as explored
        explored.add(node.State)
        
        # Expand nodes in all directions for full BFS exploration
        for child in node.all_legit_child(problem):
            if child.State not in explored and child not in frontier:
                frontier.append(child)
                total_nodes += 1

    conn.send((None, total_nodes))  # If no solution is found
    conn.close()

def bfs2(problem):
    # Set up pipes for communication with each process
    processes = []
    parent_conns = []
    
    for _ in range(4):  # Start 4 parallel processes
        parent_conn, child_conn = Pipe()
        parent_conns.append(parent_conn)
        process = Process(target=bfs_direction, args=(problem, child_conn))
        processes.append(process)
    
    # Start profiling for time and memory
    tracemalloc.start()
    t1 = time.time()
    
    # Start all processes
    for process in processes:
        process.start()

    # Collect results
    solutions = []
    total_generated_nodes = 0
    for parent_conn in parent_conns:
        result = parent_conn.recv()
        if result[0] is not None:
            solutions.append(result)
        total_generated_nodes += result[1]  # Accumulate total nodes

    # Join all processes
    for process in processes:
        process.join()
    
    t2 = time.time()
    peak_memory = tracemalloc.get_traced_memory()[1] / (2 ** 20)  # Peak memory in MB
    tracemalloc.stop()

    # Select the best solution based on path cost
    if solutions:
        best_solution = min(solutions, key=lambda x: x[0].Path_cost)
        best_node, _ = best_solution
        path = best_node.path_to_cur_state()[:-1]
        path.reverse()
        
        result = {
            'path': path,
            'total step': len(path),
            'total generated nodes': total_generated_nodes,
            'total cost': best_node.Path_cost,
            'peak memory usage': peak_memory,
            'Time consume': (t2 - t1) * 10  # Time in ms
        }
    else:
        result = {
            'path': None,
            'total step': 0,
            'total generated nodes': total_generated_nodes,
            'total cost': 0,
            'peak memory usage': peak_memory,
            'Time consume': (t2 - t1) * 10  # Time in ms
        }
    
    return result

# Example usage
if __name__ == '__main__':
    from Get_Maze import Maze  # Import Maze from your module
    input_maze = Maze("input-01.txt")
    sokoban_prob = SokobanProblem(input_maze)
    result = bfs2(sokoban_prob)
    print(result)
