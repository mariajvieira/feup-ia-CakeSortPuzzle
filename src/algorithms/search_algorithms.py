
import heapq
from collections import deque
from src.algorithms.heuristics import (
    free_slots_heuristic,
    missing_slices_heuristic,
    clustered_slices_heuristic,
    estimated_moves_heuristic,
    combined_custom_heuristic
)


class Node:
    
    def __init__(self, state, parent=None, action=None, cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth
    
    def __lt__(self, other):
        return self.cost < other.cost


def get_successors(node):
    successors = []
    state = node.state
    
    for x in range(state.board.rows):
        for y in range(state.board.cols):
            if state.board.is_empty(x, y):
                for plate_index in range(len(state.avl_plates.visible_plates)):
                    new_state = state.clone()
                    
                    success, _ = new_state.place_plate(x, y, plate_index)
                    if success:
                        action = (x, y, plate_index)
                        cost = node.cost + 1 
                        depth = node.depth + 1
                        successor = Node(new_state, node, action, cost, depth)
                        successors.append(successor)
    
    return successors


def is_goal(node):
    return node.state.win or (node.state.avl_plates.is_exhausted() and not node.state.board.is_full())


def get_solution_path(node):
    path = []
    current = node
    
    while current.parent is not None:
        path.append(current.action)
        current = current.parent
    
    path.reverse()
    
    return path


def bfs(initial_state):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    queue = deque([initial_node])
    visited = set()
    
    while queue:
        node = queue.popleft()
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        if is_goal(node):
            return True, get_solution_path(node)
        
        for successor in get_successors(node):
            queue.append(successor)
    
    return False, None


def dfs(initial_state, depth_limit=None):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    if depth_limit is None:
        depth_limit = initial_state.avl_plates.total_plate_limit * 2
    
    stack = [initial_node]
    visited = set()
    
    while stack:
        node = stack.pop()
        
        if node.depth >= depth_limit:
            continue
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        if is_goal(node):
            return True, get_solution_path(node)
        
        successors = get_successors(node)
        
        import random
        random.shuffle(successors)
        
        for successor in successors:
            stack.append(successor)
    
    return False, None


def ids(initial_state, max_depth=None):
    import time
    start_time = time.time()
    
    if max_depth is None:
        max_depth = initial_state.avl_plates.total_plate_limit
    
    initial_node = Node(initial_state)
    if is_goal(initial_node):
        return True, []
    
    best_solution = None
    
    for depth_limit in range(1, max_depth + 1):
        print(f"IDS: buscando na profundidade {depth_limit}")
        stack = [initial_node]
        visited = set()
        
        while stack:
            if time.time() - start_time > 600:
                if best_solution:
                    print(f"IDS: tempo esgotado, retornando melhor solução parcial com {len(best_solution)} passos")
                    return True, best_solution
                return False, None
                
            node = stack.pop()
            
            if is_goal(node):
                solution = get_solution_path(node)
                print(f"IDS: encontrou solução com {len(solution)} passos na profundidade {depth_limit}")
                return True, solution
            
            state_repr = str(node.state.get_state_representation())
            if state_repr in visited or node.depth >= depth_limit:
                continue
                
            visited.add(state_repr)
            
            if node.state.avl_plates.is_exhausted():
                solution = get_solution_path(node)
                if best_solution is None or len(solution) < len(best_solution):
                    best_solution = solution
            
            if node.depth < depth_limit:
                successors = get_successors(node)
                for successor in successors:
                    stack.append(successor)
    
    if best_solution:
        print(f"IDS: retornando melhor solução parcial com {len(best_solution)} passos")
        return True, best_solution
    
    return False, None


def ucs(initial_state):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    priority_queue = [initial_node]  
    visited = set()
    
    while priority_queue:
        node = heapq.heappop(priority_queue)
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        for successor in get_successors(node):
            if is_goal(successor):
                return True, get_solution_path(successor)
                        
            heapq.heappush(priority_queue, successor)
    
    return False, None


def greedy_search(initial_state, heuristic_func=combined_custom_heuristic):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    import itertools
    counter = itertools.count() 

    priority_queue = [(heuristic_func(initial_node), next(counter), initial_node)]
    visited = set()
    
    while priority_queue:
        _, _, node = heapq.heappop(priority_queue)
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        if is_goal(node):
            return True, get_solution_path(node)
        
        successors = get_successors(node)
        
        for successor in successors:
            h_value = heuristic_func(successor)
            
            heapq.heappush(priority_queue, (h_value, next(counter), successor))
    
    return False, None


def astar(initial_state, heuristic_func=combined_custom_heuristic):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    import itertools
    counter = itertools.count()
    
    priority_queue = [(initial_node.cost + heuristic_func(initial_node), next(counter), initial_node)]
    
    visited = set()
    
    nodes_explored = 0
    
    while priority_queue:
        _, _, node = heapq.heappop(priority_queue)
        nodes_explored += 1
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        if is_goal(node):
            print(f"A*: Solução encontrada após explorar {nodes_explored} nós")
            return True, get_solution_path(node)
        
        for successor in get_successors(node):
            f_value = successor.cost + heuristic_func(successor)
            
            heapq.heappush(priority_queue, (f_value, next(counter), successor))
    
    return False, None


def weighted_astar(initial_state, weight=2.0, heuristic_func=combined_custom_heuristic):
    initial_node = Node(initial_state)
    
    if is_goal(initial_node):
        return True, []
    
    import itertools
    counter = itertools.count()
    
    priority_queue = [(initial_node.cost + weight * heuristic_func(initial_node), next(counter), initial_node)]
    
    visited = set()
    
    nodes_explored = 0
    
    while priority_queue:
        _, _, node = heapq.heappop(priority_queue)
        nodes_explored += 1
        
        state_repr = str(node.state.get_state_representation())
        
        if state_repr in visited:
            continue
        
        visited.add(state_repr)
        
        if is_goal(node):
            print(f"Weighted A* (w={weight}): Solução encontrada após explorar {nodes_explored} nós")
            return True, get_solution_path(node)
        
        for successor in get_successors(node):
            f_value = successor.cost + weight * heuristic_func(successor)
            
            heapq.heappush(priority_queue, (f_value, next(counter), successor))
    
    return False, None


def get_algorithm(algorithm_name):
    algorithms = {
        'bfs': bfs,
        'dfs': lambda state: dfs(state, depth_limit=state.avl_plates.total_plate_limit * 3),
        'ids': lambda state: ids(state, max_depth=state.avl_plates.total_plate_limit * 2),
        'ucs': ucs,
        'greedy': lambda state: greedy_search(state, heuristic_func=combined_custom_heuristic),
        'astar': lambda state: astar(state, heuristic_func=combined_custom_heuristic),
        'wastar': lambda state: weighted_astar(state, weight=1.5, heuristic_func=combined_custom_heuristic)
    }
    
    return algorithms.get(algorithm_name.lower())