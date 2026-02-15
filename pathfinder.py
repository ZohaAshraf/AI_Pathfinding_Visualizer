"""
AI Pathfinder - Uninformed Search Algorithms Visualizer
Academic Assignment: Grid-based pathfinding with dynamic obstacles
Author: Student Implementation
"""

import pygame
import time
from collections import deque
from queue import PriorityQueue
import random
from typing import List, Tuple, Set, Optional, Dict
import sys

# Color scheme for professional GUI
COLORS = {
    'background': (240, 240, 245),
    'grid_line': (200, 200, 210),
    'empty': (255, 255, 255),
    'wall': (50, 50, 50),
    'start': (66, 133, 244),  # Blue
    'target': (52, 168, 83),  # Green
    'frontier': (251, 188, 5),  # Yellow/Gold
    'explored': (234, 67, 53),  # Red
    'path': (156, 39, 176),  # Purple
    'dynamic_obstacle': (255, 87, 34),  # Deep Orange
    'text': (33, 33, 33),
    'panel': (250, 250, 252)
}

# Grid configuration
GRID_SIZE = 20  # 20x20 grid
CELL_SIZE = 30
MARGIN = 5
INFO_PANEL_WIDTH = 300
WINDOW_WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + INFO_PANEL_WIDTH
WINDOW_HEIGHT = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 100

# Search animation speed (milliseconds)
ANIMATION_DELAY = 50

# Dynamic obstacle probability (per step)
DYNAMIC_OBSTACLE_PROBABILITY = 0.002


class Node:
    """Represents a grid cell/node in the search space"""
    
    def __init__(self, row: int, col: int, cost: int = 0):
        self.row = row
        self.col = col
        self.cost = cost
        self.parent: Optional[Node] = None
        
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.row == other.row and self.col == other.col
        return False
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __lt__(self, other):
        return self.cost < other.cost
    
    def __repr__(self):
        return f"Node({self.row}, {self.col})"
    
    def get_position(self) -> Tuple[int, int]:
        return (self.row, self.col)


class GridEnvironment:
    """Manages the grid environment with static and dynamic obstacles"""
    
    def __init__(self, size: int = GRID_SIZE):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.start: Optional[Tuple[int, int]] = None
        self.target: Optional[Tuple[int, int]] = None
        self.static_walls: Set[Tuple[int, int]] = set()
        self.dynamic_obstacles: Set[Tuple[int, int]] = set()
        
    def set_start(self, row: int, col: int):
        """Set the start position"""
        self.start = (row, col)
        
    def set_target(self, row: int, col: int):
        """Set the target position"""
        self.target = (row, col)
        
    def add_wall(self, row: int, col: int):
        """Add a static wall"""
        if (row, col) != self.start and (row, col) != self.target:
            self.static_walls.add((row, col))
            
    def add_dynamic_obstacle(self, row: int, col: int):
        """Add a dynamic obstacle during runtime"""
        if (row, col) not in self.static_walls and \
           (row, col) != self.start and \
           (row, col) != self.target:
            self.dynamic_obstacles.add((row, col))
            return True
        return False
    
    def remove_dynamic_obstacle(self, row: int, col: int):
        """Remove a dynamic obstacle"""
        self.dynamic_obstacles.discard((row, col))
        
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is valid and not blocked"""
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        if (row, col) in self.static_walls or (row, col) in self.dynamic_obstacles:
            return False
        return True
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Get valid neighbors following the strict movement order:
        1. Up, 2. Right, 3. Bottom, 4. Bottom-Right (Diagonal),
        5. Left, 6. Top-Left (Diagonal)
        Plus all other diagonals: Top-Right, Bottom-Left
        """
        row, col = node.row, node.col
        neighbors = []
        
        # Movement directions in strict order (including ALL diagonals)
        directions = [
            (-1, 0),   # 1. Up
            (0, 1),    # 2. Right
            (1, 0),    # 3. Bottom
            (1, 1),    # 4. Bottom-Right (Diagonal)
            (0, -1),   # 5. Left
            (-1, -1),  # 6. Top-Left (Diagonal)
            (-1, 1),   # 7. Top-Right (Diagonal)
            (1, -1),   # 8. Bottom-Left (Diagonal)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                # Diagonal moves cost more (sqrt(2) ≈ 1.414, we use 14 vs 10)
                cost = 14 if dr != 0 and dc != 0 else 10
                neighbors.append(Node(new_row, new_col, node.cost + cost))
        
        return neighbors
    
    def spawn_dynamic_obstacle(self) -> Optional[Tuple[int, int]]:
        """Randomly spawn a dynamic obstacle"""
        if random.random() < DYNAMIC_OBSTACLE_PROBABILITY:
            # Find empty cells
            empty_cells = []
            for row in range(self.size):
                for col in range(self.size):
                    if self.is_valid_position(row, col) and \
                       (row, col) != self.start and \
                       (row, col) != self.target:
                        empty_cells.append((row, col))
            
            if empty_cells:
                obstacle_pos = random.choice(empty_cells)
                self.add_dynamic_obstacle(*obstacle_pos)
                return obstacle_pos
        return None
    
    def create_sample_maze(self):
        """Create a sample maze with walls"""
        # Vertical wall in the middle with gap
        for i in range(self.size):
            if i not in [self.size // 2 - 1, self.size // 2, self.size // 2 + 1]:
                self.add_wall(i, self.size // 2)
        
        # Horizontal walls
        for j in range(self.size // 3, 2 * self.size // 3):
            if j != self.size // 2:
                self.add_wall(self.size // 4, j)
                self.add_wall(3 * self.size // 4, j)


class SearchAlgorithm:
    """Base class for all search algorithms"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        self.env = environment
        self.visualizer = visualizer
        self.frontier_nodes: Set[Tuple[int, int]] = set()
        self.explored_nodes: Set[Tuple[int, int]] = set()
        self.path: List[Tuple[int, int]] = []
        self.algorithm_name = "Generic Search"
        self.nodes_expanded = 0
        self.path_cost = 0
        self.is_running = True
        
    def reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruct path from target to start using parent pointers"""
        path = []
        current = node
        while current is not None:
            path.append(current.get_position())
            current = current.parent
        return path[::-1]
    
    def check_dynamic_obstacle_on_path(self, path: List[Tuple[int, int]]) -> bool:
        """Check if a dynamic obstacle appeared on the planned path"""
        for pos in path:
            if pos in self.env.dynamic_obstacles:
                return True
        return False
    
    def handle_dynamic_obstacle(self):
        """Handle dynamic obstacle spawn"""
        obstacle_pos = self.env.spawn_dynamic_obstacle()
        if obstacle_pos:
            # Check if it blocks current path
            if obstacle_pos in self.path:
                # Need to re-plan!
                return True
        return False
    
    def search(self) -> bool:
        """To be implemented by subclasses"""
        raise NotImplementedError


class BFS(SearchAlgorithm):
    """Breadth-First Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        super().__init__(environment, visualizer)
        self.algorithm_name = "Breadth-First Search (BFS)"
    
    def search(self) -> bool:
        """Execute BFS algorithm"""
        if not self.env.start or not self.env.target:
            return False
        
        start_node = Node(*self.env.start)
        target_pos = self.env.target
        
        queue = deque([start_node])
        visited = {self.env.start}
        
        while queue and self.is_running:
            # Handle dynamic obstacles
            if self.handle_dynamic_obstacle():
                self.visualizer.show_message("Dynamic obstacle detected! Re-planning...")
                return self.search()  # Restart search
            
            current = queue.popleft()
            current_pos = current.get_position()
            
            # Update visualization
            self.frontier_nodes = {node.get_position() for node in queue}
            self.explored_nodes = visited.copy()
            self.nodes_expanded += 1
            
            self.visualizer.update_display(self)
            pygame.time.delay(ANIMATION_DELAY)
            
            # Check if target reached
            if current_pos == target_pos:
                self.path = self.reconstruct_path(current)
                self.path_cost = len(self.path) - 1
                return True
            
            # Explore neighbors
            for neighbor in self.env.get_neighbors(current):
                neighbor_pos = neighbor.get_position()
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    neighbor.parent = current
                    queue.append(neighbor)
        
        return False


class DFS(SearchAlgorithm):
    """Depth-First Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        super().__init__(environment, visualizer)
        self.algorithm_name = "Depth-First Search (DFS)"
    
    def search(self) -> bool:
        """Execute DFS algorithm"""
        if not self.env.start or not self.env.target:
            return False
        
        start_node = Node(*self.env.start)
        target_pos = self.env.target
        
        stack = [start_node]
        visited = {self.env.start}
        
        while stack and self.is_running:
            # Handle dynamic obstacles
            if self.handle_dynamic_obstacle():
                self.visualizer.show_message("Dynamic obstacle detected! Re-planning...")
                return self.search()
            
            current = stack.pop()
            current_pos = current.get_position()
            
            # Update visualization
            self.frontier_nodes = {node.get_position() for node in stack}
            self.explored_nodes = visited.copy()
            self.nodes_expanded += 1
            
            self.visualizer.update_display(self)
            pygame.time.delay(ANIMATION_DELAY)
            
            # Check if target reached
            if current_pos == target_pos:
                self.path = self.reconstruct_path(current)
                self.path_cost = len(self.path) - 1
                return True
            
            # Explore neighbors (reverse to maintain order due to stack)
            neighbors = self.env.get_neighbors(current)
            for neighbor in reversed(neighbors):
                neighbor_pos = neighbor.get_position()
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    neighbor.parent = current
                    stack.append(neighbor)
        
        return False


class UCS(SearchAlgorithm):
    """Uniform-Cost Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        super().__init__(environment, visualizer)
        self.algorithm_name = "Uniform-Cost Search (UCS)"
    
    def search(self) -> bool:
        """Execute UCS algorithm"""
        if not self.env.start or not self.env.target:
            return False
        
        start_node = Node(*self.env.start, cost=0)
        target_pos = self.env.target
        
        pq = PriorityQueue()
        pq.put((0, id(start_node), start_node))
        visited = set()
        cost_so_far = {self.env.start: 0}
        
        while not pq.empty() and self.is_running:
            # Handle dynamic obstacles
            if self.handle_dynamic_obstacle():
                self.visualizer.show_message("Dynamic obstacle detected! Re-planning...")
                return self.search()
            
            _, _, current = pq.get()
            current_pos = current.get_position()
            
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            
            # Update visualization
            self.explored_nodes = visited.copy()
            self.nodes_expanded += 1
            
            self.visualizer.update_display(self)
            pygame.time.delay(ANIMATION_DELAY)
            
            # Check if target reached
            if current_pos == target_pos:
                self.path = self.reconstruct_path(current)
                self.path_cost = current.cost
                return True
            
            # Explore neighbors
            for neighbor in self.env.get_neighbors(current):
                neighbor_pos = neighbor.get_position()
                new_cost = current.cost + (14 if abs(neighbor.row - current.row) + abs(neighbor.col - current.col) == 2 else 10)
                
                if neighbor_pos not in visited and \
                   (neighbor_pos not in cost_so_far or new_cost < cost_so_far[neighbor_pos]):
                    cost_so_far[neighbor_pos] = new_cost
                    neighbor.cost = new_cost
                    neighbor.parent = current
                    pq.put((new_cost, id(neighbor), neighbor))
        
        return False


class DLS(SearchAlgorithm):
    """Depth-Limited Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer', limit: int = 15):
        super().__init__(environment, visualizer)
        self.algorithm_name = f"Depth-Limited Search (DLS, limit={limit})"
        self.limit = limit
    
    def dls_recursive(self, node: Node, target_pos: Tuple[int, int], 
                      depth: int, visited: Set[Tuple[int, int]]) -> Optional[Node]:
        """Recursive DLS helper"""
        if not self.is_running:
            return None
        
        # Handle dynamic obstacles
        if self.handle_dynamic_obstacle():
            return None
        
        node_pos = node.get_position()
        
        # Update visualization
        self.explored_nodes = visited.copy()
        self.nodes_expanded += 1
        
        self.visualizer.update_display(self)
        pygame.time.delay(ANIMATION_DELAY)
        
        # Check if target reached
        if node_pos == target_pos:
            return node
        
        # Check depth limit
        if depth >= self.limit:
            return None
        
        # Explore neighbors
        for neighbor in self.env.get_neighbors(node):
            neighbor_pos = neighbor.get_position()
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                neighbor.parent = node
                result = self.dls_recursive(neighbor, target_pos, depth + 1, visited)
                if result:
                    return result
        
        return None
    
    def search(self) -> bool:
        """Execute DLS algorithm"""
        if not self.env.start or not self.env.target:
            return False
        
        start_node = Node(*self.env.start)
        target_pos = self.env.target
        visited = {self.env.start}
        
        result = self.dls_recursive(start_node, target_pos, 0, visited)
        
        if result:
            self.path = self.reconstruct_path(result)
            self.path_cost = len(self.path) - 1
            return True
        
        return False


class IDDFS(SearchAlgorithm):
    """Iterative Deepening Depth-First Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        super().__init__(environment, visualizer)
        self.algorithm_name = "Iterative Deepening DFS (IDDFS)"
        self.current_depth_limit = 0
    
    def dls_iterative(self, limit: int) -> Optional[Node]:
        """Depth-limited search for IDDFS"""
        if not self.env.start or not self.env.target:
            return None
        
        start_node = Node(*self.env.start)
        target_pos = self.env.target
        
        stack = [(start_node, 0)]  # (node, depth)
        visited = {self.env.start}
        
        while stack and self.is_running:
            # Handle dynamic obstacles
            if self.handle_dynamic_obstacle():
                return None
            
            current, depth = stack.pop()
            current_pos = current.get_position()
            
            # Update visualization
            self.frontier_nodes = {node.get_position() for node, _ in stack}
            self.explored_nodes = visited.copy()
            self.nodes_expanded += 1
            
            self.visualizer.update_display(self)
            pygame.time.delay(ANIMATION_DELAY // 2)  # Faster for IDDFS
            
            # Check if target reached
            if current_pos == target_pos:
                return current
            
            # Check depth limit
            if depth < limit:
                # Explore neighbors
                neighbors = self.env.get_neighbors(current)
                for neighbor in reversed(neighbors):
                    neighbor_pos = neighbor.get_position()
                    if neighbor_pos not in visited:
                        visited.add(neighbor_pos)
                        neighbor.parent = current
                        stack.append((neighbor, depth + 1))
        
        return None
    
    def search(self) -> bool:
        """Execute IDDFS algorithm"""
        max_depth = self.env.size * 2  # Reasonable maximum depth
        
        for depth in range(max_depth):
            if not self.is_running:
                return False
            
            self.current_depth_limit = depth
            self.visualizer.show_message(f"IDDFS: Trying depth limit {depth}")
            
            result = self.dls_iterative(depth)
            
            if result:
                self.path = self.reconstruct_path(result)
                self.path_cost = len(self.path) - 1
                return True
        
        return False


class BidirectionalSearch(SearchAlgorithm):
    """Bidirectional Search implementation"""
    
    def __init__(self, environment: GridEnvironment, visualizer: 'Visualizer'):
        super().__init__(environment, visualizer)
        self.algorithm_name = "Bidirectional Search"
    
    def search(self) -> bool:
        """Execute Bidirectional Search algorithm"""
        if not self.env.start or not self.env.target:
            return False
        
        start_node = Node(*self.env.start)
        target_node = Node(*self.env.target)
        
        # Forward search from start
        forward_queue = deque([start_node])
        forward_visited = {self.env.start: start_node}
        
        # Backward search from target
        backward_queue = deque([target_node])
        backward_visited = {self.env.target: target_node}
        
        while (forward_queue or backward_queue) and self.is_running:
            # Handle dynamic obstacles
            if self.handle_dynamic_obstacle():
                self.visualizer.show_message("Dynamic obstacle detected! Re-planning...")
                return self.search()
            
            # Forward step
            if forward_queue:
                current_forward = forward_queue.popleft()
                current_pos = current_forward.get_position()
                
                # Check if paths meet
                if current_pos in backward_visited:
                    # Reconstruct complete path
                    forward_path = self.reconstruct_path(current_forward)
                    backward_path = self.reconstruct_path(backward_visited[current_pos])
                    self.path = forward_path + backward_path[-2::-1]
                    self.path_cost = len(self.path) - 1
                    return True
                
                # Explore forward
                for neighbor in self.env.get_neighbors(current_forward):
                    neighbor_pos = neighbor.get_position()
                    if neighbor_pos not in forward_visited:
                        forward_visited[neighbor_pos] = neighbor
                        neighbor.parent = current_forward
                        forward_queue.append(neighbor)
            
            # Backward step
            if backward_queue:
                current_backward = backward_queue.popleft()
                current_pos = current_backward.get_position()
                
                # Check if paths meet
                if current_pos in forward_visited:
                    # Reconstruct complete path
                    forward_path = self.reconstruct_path(forward_visited[current_pos])
                    backward_path = self.reconstruct_path(current_backward)
                    self.path = forward_path + backward_path[-2::-1]
                    self.path_cost = len(self.path) - 1
                    return True
                
                # Explore backward
                for neighbor in self.env.get_neighbors(current_backward):
                    neighbor_pos = neighbor.get_position()
                    if neighbor_pos not in backward_visited:
                        backward_visited[neighbor_pos] = neighbor
                        neighbor.parent = current_backward
                        backward_queue.append(neighbor)
            
            # Update visualization
            self.frontier_nodes = {node.get_position() for node in forward_queue} | \
                                 {node.get_position() for node in backward_queue}
            self.explored_nodes = set(forward_visited.keys()) | set(backward_visited.keys())
            self.nodes_expanded += 1
            
            self.visualizer.update_display(self)
            pygame.time.delay(ANIMATION_DELAY)
        
        return False


class Visualizer:
    """Handles all GUI visualization using Pygame"""
    
    def __init__(self, environment: GridEnvironment):
        pygame.init()
        self.env = environment
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 14, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.message_font = pygame.font.SysFont('Arial', 16)
        self.message = ""
        self.message_time = 0
        
    def draw_grid(self):
        """Draw the base grid"""
        self.screen.fill(COLORS['background'])
        
        for row in range(self.env.size):
            for col in range(self.env.size):
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                
                # Determine cell color
                pos = (row, col)
                if pos in self.env.static_walls:
                    color = COLORS['wall']
                elif pos in self.env.dynamic_obstacles:
                    color = COLORS['dynamic_obstacle']
                elif pos == self.env.start:
                    color = COLORS['start']
                elif pos == self.env.target:
                    color = COLORS['target']
                else:
                    color = COLORS['empty']
                
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, COLORS['grid_line'], 
                               (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_search_state(self, algorithm: SearchAlgorithm):
        """Draw the current search state"""
        # Draw explored nodes
        for pos in algorithm.explored_nodes:
            if pos != self.env.start and pos != self.env.target:
                row, col = pos
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                pygame.draw.rect(self.screen, COLORS['explored'], 
                               (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw frontier nodes
        for pos in algorithm.frontier_nodes:
            if pos != self.env.start and pos != self.env.target:
                row, col = pos
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                pygame.draw.rect(self.screen, COLORS['frontier'], 
                               (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw path
        for pos in algorithm.path:
            if pos != self.env.start and pos != self.env.target:
                row, col = pos
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                pygame.draw.rect(self.screen, COLORS['path'], 
                               (x, y, CELL_SIZE, CELL_SIZE))
        
        # Redraw start and target on top
        if self.env.start:
            row, col = self.env.start
            x = col * (CELL_SIZE + MARGIN) + MARGIN
            y = row * (CELL_SIZE + MARGIN) + MARGIN
            pygame.draw.rect(self.screen, COLORS['start'], 
                           (x, y, CELL_SIZE, CELL_SIZE))
            text = self.font.render('S', True, COLORS['empty'])
            self.screen.blit(text, (x + CELL_SIZE//3, y + CELL_SIZE//4))
        
        if self.env.target:
            row, col = self.env.target
            x = col * (CELL_SIZE + MARGIN) + MARGIN
            y = row * (CELL_SIZE + MARGIN) + MARGIN
            pygame.draw.rect(self.screen, COLORS['target'], 
                           (x, y, CELL_SIZE, CELL_SIZE))
            text = self.font.render('T', True, COLORS['empty'])
            self.screen.blit(text, (x + CELL_SIZE//3, y + CELL_SIZE//4))
        
        # Draw grid lines
        for row in range(self.env.size):
            for col in range(self.env.size):
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                pygame.draw.rect(self.screen, COLORS['grid_line'], 
                               (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_info_panel(self, algorithm: SearchAlgorithm):
        """Draw information panel on the right side"""
        panel_x = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 10
        panel_y = 20
        
        # Title
        title = self.title_font.render("GOOD PERFORMANCE TIME APP", True, COLORS['text'])
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 40
        
        # Algorithm name
        algo_text = self.font.render(f"Algorithm:", True, COLORS['text'])
        self.screen.blit(algo_text, (panel_x, panel_y))
        panel_y += 20
        
        algo_name = self.message_font.render(algorithm.algorithm_name, True, COLORS['text'])
        self.screen.blit(algo_name, (panel_x, panel_y))
        panel_y += 35
        
        # Statistics
        stats = [
            f"Nodes Expanded: {algorithm.nodes_expanded}",
            f"Frontier Size: {len(algorithm.frontier_nodes)}",
            f"Explored Size: {len(algorithm.explored_nodes)}",
            f"Path Length: {len(algorithm.path)}",
            f"Path Cost: {algorithm.path_cost}",
            f"",
            "Legend:",
        ]
        
        for stat in stats:
            text = self.font.render(stat, True, COLORS['text'])
            self.screen.blit(text, (panel_x, panel_y))
            panel_y += 20
        
        # Legend with colored boxes
        legend_items = [
            ("Start (S)", COLORS['start']),
            ("Target (T)", COLORS['target']),
            ("Wall", COLORS['wall']),
            ("Frontier", COLORS['frontier']),
            ("Explored", COLORS['explored']),
            ("Path", COLORS['path']),
            ("Dynamic Obstacle", COLORS['dynamic_obstacle']),
        ]
        
        for label, color in legend_items:
            pygame.draw.rect(self.screen, color, (panel_x, panel_y, 15, 15))
            text = self.font.render(label, True, COLORS['text'])
            self.screen.blit(text, (panel_x + 20, panel_y))
            panel_y += 20
        
        # Message display
        if self.message and time.time() - self.message_time < 3:
            panel_y += 20
            msg = self.message_font.render(self.message, True, COLORS['dynamic_obstacle'])
            self.screen.blit(msg, (panel_x, panel_y))
    
    def update_display(self, algorithm: SearchAlgorithm):
        """Update the complete display"""
        self.draw_grid()
        self.draw_search_state(algorithm)
        self.draw_info_panel(algorithm)
        pygame.display.flip()
        self.clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                algorithm.is_running = False
    
    def show_message(self, message: str):
        """Show a temporary message"""
        self.message = message
        self.message_time = time.time()
    
    def show_final_result(self, algorithm: SearchAlgorithm, success: bool):
        """Show final result screen"""
        self.draw_grid()
        self.draw_search_state(algorithm)
        self.draw_info_panel(algorithm)
        
        # Result message
        result_text = "Path Found!" if success else "No Path Found!"
        color = COLORS['target'] if success else COLORS['explored']
        
        result_surface = self.title_font.render(result_text, True, color)
        rect = result_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        
        # Background for text
        padding = 10
        bg_rect = pygame.Rect(rect.x - padding, rect.y - padding,
                            rect.width + 2*padding, rect.height + 2*padding)
        pygame.draw.rect(self.screen, COLORS['panel'], bg_rect)
        pygame.draw.rect(self.screen, color, bg_rect, 2)
        
        self.screen.blit(result_surface, rect)
        pygame.display.flip()
    
    def wait_for_close(self):
        """Wait for user to close the window"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        waiting = False
            self.clock.tick(30)


def run_algorithm(algorithm_class, environment: GridEnvironment, **kwargs):
    """Run a specific search algorithm"""
    visualizer = Visualizer(environment)
    algorithm = algorithm_class(environment, visualizer, **kwargs)
    
    print(f"\n{'='*60}")
    print(f"Running: {algorithm.algorithm_name}")
    print(f"{'='*60}")
    
    visualizer.update_display(algorithm)
    pygame.time.delay(1000)  # Initial delay
    
    success = algorithm.search()
    
    print(f"Result: {'Success' if success else 'Failed'}")
    print(f"Nodes Expanded: {algorithm.nodes_expanded}")
    print(f"Path Length: {len(algorithm.path)}")
    print(f"Path Cost: {algorithm.path_cost}")
    
    visualizer.show_final_result(algorithm, success)
    visualizer.wait_for_close()
    
    pygame.quit()


def main():
    """Main function to demonstrate all algorithms"""
    
    # Algorithm selection menu
    print("="*60)
    print("GOOD PERFORMANCE TIME APP")
    print("AI Pathfinder - Uninformed Search Algorithms")
    print("="*60)
    print("\nAvailable Algorithms:")
    print("1. Breadth-First Search (BFS)")
    print("2. Depth-First Search (DFS)")
    print("3. Uniform-Cost Search (UCS)")
    print("4. Depth-Limited Search (DLS)")
    print("5. Iterative Deepening DFS (IDDFS)")
    print("6. Bidirectional Search")
    print("7. Run All Algorithms Sequentially")
    print("0. Exit")
    
    choice = input("\nSelect algorithm (0-7): ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    
    # Create environment
    env = GridEnvironment()
    env.set_start(6, 1)  # Start position
    env.set_target(5, 7)  # Target position
    env.create_sample_maze()  # Create sample obstacles
    
    algorithms = {
        "1": (BFS, {}),
        "2": (DFS, {}),
        "3": (UCS, {}),
        "4": (DLS, {"limit": 15}),
        "5": (IDDFS, {}),
        "6": (BidirectionalSearch, {}),
    }
    
    if choice == "7":
        # Run all algorithms
        for key in sorted(algorithms.keys()):
            env = GridEnvironment()
            env.set_start(6, 1)
            env.set_target(5, 7)
            env.create_sample_maze()
            
            algo_class, kwargs = algorithms[key]
            run_algorithm(algo_class, env, **kwargs)
    elif choice in algorithms:
        algo_class, kwargs = algorithms[choice]
        run_algorithm(algo_class, env, **kwargs)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
