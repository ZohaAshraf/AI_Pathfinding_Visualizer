# AI Pathfinder - Uninformed Search Algorithms Visualizer

## 🎯 Project Overview

This project implements a comprehensive AI pathfinding system that visualizes six fundamental uninformed search algorithms in a dynamic grid environment. The system includes real-time obstacle spawning and path re-planning capabilities.

**Academic Assignment**: AI 2002 - Artificial Intelligence (Spring 2026)  
**Assignment**: Question 7 - Uninformed Search in a Grid Environment

---

## 🚀 Features

### Implemented Algorithms
1. **Breadth-First Search (BFS)** - Explores level by level
2. **Depth-First Search (DFS)** - Explores deep paths first
3. **Uniform-Cost Search (UCS)** - Considers movement costs (diagonal costs more)
4. **Depth-Limited Search (DLS)** - DFS with depth constraint
5. **Iterative Deepening DFS (IDDFS)** - Combines BFS completeness with DFS space efficiency
6. **Bidirectional Search** - Searches from both start and target simultaneously

### Key Features
- ✅ **Step-by-step visualization** of algorithm execution
- ✅ **Dynamic obstacle spawning** during runtime
- ✅ **Automatic path re-planning** when obstacles block the path
- ✅ **Professional GUI** with real-time statistics
- ✅ **Strict movement order** following assignment specifications
- ✅ **All diagonal movements** supported (8-directional movement)
- ✅ **Color-coded visualization** (Frontier, Explored, Path, Obstacles)
- ✅ **Real-time statistics** (nodes expanded, path length, path cost)

---

## 📋 Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```bash
pygame>=2.0.0
```

---

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd ai-pathfinder
```

### Step 2: Install Dependencies
```bash
pip install pygame
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

---

## 🎮 How to Run

### Method 1: Interactive Menu
```bash
python pathfinder.py
```

Follow the on-screen menu to select an algorithm:
- Enter 1-6 to run a specific algorithm
- Enter 7 to run all algorithms sequentially
- Enter 0 to exit

### Method 2: Run Specific Algorithm Programmatically

You can modify the `main()` function or create a custom script:

```python
from pathfinder import *

# Create environment
env = GridEnvironment()
env.set_start(6, 1)
env.set_target(5, 7)
env.create_sample_maze()

# Run BFS
run_algorithm(BFS, env)
```

---

## 🎨 GUI Controls

- **Window Title**: "GOOD PERFORMANCE TIME APP"
- **Close Window**: Click X or press ESC/Q after algorithm completes
- **Visual Elements**:
  - 🔵 Blue = Start (S)
  - 🟢 Green = Target (T)
  - ⬛ Black = Static Wall
  - 🟡 Yellow = Frontier Nodes (waiting to be explored)
  - 🔴 Red = Explored Nodes (already visited)
  - 🟣 Purple = Final Path
  - 🟠 Orange = Dynamic Obstacle


---

## 📊 Configuration

You can modify these constants in `pathfinder.py`:

```python
GRID_SIZE = 20                          # Grid dimensions (20x20)
CELL_SIZE = 30                          # Pixel size of each cell
ANIMATION_DELAY = 50                    # Milliseconds between steps
DYNAMIC_OBSTACLE_PROBABILITY = 0.002   # Chance of obstacle spawning per step
```

---

## 🏗️ Architecture

### Project Structure
```
ai-pathfinder/
│
├── pathfinder.py           # Main application file
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── report/                 # Report with screenshots (to be created)
    ├── report.pdf
    └── screenshots/
        ├── bfs_best.png
        ├── bfs_worst.png
        ├── dfs_best.png
        └── ...
```

### Class Architecture

#### 1. **Node**
- Represents a grid cell
- Stores position, cost, and parent pointer
- Used for path reconstruction

#### 2. **GridEnvironment**
- Manages the grid state
- Handles static and dynamic obstacles
- Validates positions and generates neighbors
- Implements strict movement order

#### 3. **SearchAlgorithm** (Base Class)
- Common functionality for all algorithms
- Path reconstruction
- Dynamic obstacle handling
- Visualization updates

#### 4. **BFS, DFS, UCS, DLS, IDDFS, BidirectionalSearch**
- Inherit from SearchAlgorithm
- Implement specific search strategies
- Handle frontier and explored sets

#### 5. **Visualizer**
- Pygame-based GUI
- Real-time visualization
- Statistics display
- Event handling

---

## 🔍 Algorithm Details

### Movement Order (Strict Specification)
When expanding nodes, neighbors are added in this order:
1. Up (-1, 0)
2. Right (0, 1)
3. Bottom (1, 0)
4. Bottom-Right (1, 1) - Diagonal
5. Left (0, -1)
6. Top-Left (-1, -1) - Diagonal
7. Top-Right (-1, 1) - Diagonal
8. Bottom-Left (1, -1) - Diagonal

### Cost Calculation (UCS)
- Straight moves (Up, Right, Down, Left): Cost = 10
- Diagonal moves: Cost = 14 (approximation of √2 × 10)

### Dynamic Obstacles
- Small probability of spawning each step (0.2% by default)
- If obstacle blocks current path → re-plan automatically
- Shown in orange color
- Cannot spawn on start, target, or walls

---

## 📝 Design Decisions

### 1. **Object-Oriented Design**
- **Why**: Clean separation of concerns, easy to extend and modify
- **Benefit**: Each algorithm is self-contained, easy to test and debug

### 2. **Pygame for Visualization**
- **Why**: Better animation control than Matplotlib
- **Benefit**: Real-time updates, smoother animations, better interactivity

### 3. **Separate Visualizer Class**
- **Why**: Decouples GUI from algorithm logic
- **Benefit**: Algorithms can be tested without GUI, easy to switch visualization libraries

### 4. **Base SearchAlgorithm Class**
- **Why**: Reduces code duplication
- **Benefit**: Common functionality (path reconstruction, dynamic obstacles) implemented once

### 5. **Dynamic Obstacle Re-planning**
- **Why**: Assignment requirement
- **Implementation**: Recursive call to `search()` if obstacle detected
- **Limitation**: Resets explored nodes (could be optimized with A* or incremental search)

### 6. **Priority Queue for UCS**
- **Why**: Efficient retrieval of lowest-cost node
- **Implementation**: Python's built-in `queue.PriorityQueue`

### 7. **Bidirectional Search Implementation**
- **Strategy**: Alternates between forward and backward expansion
- **Termination**: When a node appears in both visited sets
- **Path Reconstruction**: Concatenates forward and backward paths

---

## 🧪 Testing Scenarios

### Best Case Scenarios
- **BFS/UCS**: Direct path with minimal obstacles
- **DFS**: Target is in the first deep exploration branch
- **IDDFS**: Target found at low depth
- **Bidirectional**: Paths meet quickly in the middle

### Worst Case Scenarios
- **BFS/UCS**: Target in far corner, requires exploring entire grid
- **DFS**: Target requires backtracking through entire search space
- **DLS**: Depth limit too small, fails to find path
- **IDDFS**: High depth required, many redundant expansions
- **Bidirectional**: Paths don't meet until exploring most of grid

---
## Algorithm Complexity Analysis
   
   | Algorithm | Time | Space | Complete | Optimal |
   |-----------|------|-------|----------|---------|
   | BFS       | O(V+E) | O(V) | Yes | Yes* |
   | DFS       | O(V+E) | O(h) | No | No |
   | UCS       | O(E log V) | O(V) | Yes | Yes |
   | DLS       | O(b^l) | O(l) | No | No |
   | IDDFS     | O(b^d) | O(d) | Yes | Yes* |
   | Bidirectional | O(b^(d/2)) | O(b^(d/2)) | Yes | Yes* |
   
   *Optimal for unweighted graphs
```


## 🐛 Known Limitations

1. **Dynamic Obstacle Re-planning**: Current implementation restarts the search completely. Could be optimized with incremental search algorithms.

2. **Memory Usage**: For large grids, storing all nodes can be memory-intensive. Could be optimized with state-space compression.

3. **Animation Speed**: Very fast algorithms might appear too quick. Adjust `ANIMATION_DELAY` for better visualization.

4. **DLS Depth Limit**: Fixed at 15 by default. May need adjustment for larger grids.

---

## 🎓 Viva Voce Preparation

### Code Modification Examples

**Example 1**: Change movement order
```python
# In GridEnvironment.get_neighbors():
directions = [
    (0, 1),    # Right
    (1, 0),    # Down
    (0, -1),   # Left
    (-1, 0),   # Up
    # ... diagonals
]
```

**Example 2**: Modify visualization colors
```python
COLORS = {
    'frontier': (0, 255, 0),  # Change to green
    'explored': (255, 0, 0),   # Keep red
    # ...
}
```

**Example 3**: Add heuristic to UCS (making it A*)
```python
def heuristic(node, target):
    return abs(node.row - target[0]) + abs(node.col - target[1])

# In UCS.search():
priority = new_cost + heuristic(neighbor, target_pos)
```

**Example 4**: Change dynamic obstacle probability
```python
DYNAMIC_OBSTACLE_PROBABILITY = 0.01  # 1% instead of 0.2%
```

---

## 📚 References

- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.)
- Pygame Documentation: https://www.pygame.org/docs/
- Python Queue Documentation: https://docs.python.org/3/library/queue.html

---

## 👨‍💻 Author

**Student ID**: 24F-3019
**Course**: AI 2002 - Artificial Intelligence  
**Semester**: Spring 2026

---

## 📄 License

This project is submitted as academic coursework for AI 2002.

---

## 🙏 Acknowledgments

- Course instructor for assignment design
- Pygame community for excellent documentation
- Python community for robust libraries

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review code comments
3. Contact via university email

---

## 🔄 Version History

- **v1.0** (February 2026): Initial implementation with all 6 algorithms
  - BFS, DFS, UCS, DLS, IDDFS, Bidirectional Search
  - Dynamic obstacles
  - Professional GUI
  - Complete visualization

---

## 🎯 Assignment Checklist

- ✅ All 6 algorithms implemented
- ✅ Strict movement order followed
- ✅ Dynamic obstacles with re-planning
- ✅ Professional GUI with title "GOOD PERFORMANCE TIME APP"
- ✅ Step-by-step visualization
- ✅ Frontier and explored nodes shown
- ✅ Final path highlighted
- ✅ Real-time statistics
- ✅ Comprehensive README
- ✅ Clean, commented code
- ✅ OOP design for viva modifications
- ✅ GitHub ready with commit history

---
## Version History
   - v1.0 - Initial release with all 6 algorithms
```
5. **Scroll down to "Commit changes"**
6. **Write commit message:**
```
## Troubleshooting
   
   ### Issue: "No module named pygame"
   **Solution:** Run `pip install pygame`
   
   ### Issue: Window closes immediately  
   **Solution:** Run from command prompt, not double-click
   
   ### Issue: Program runs but no window appears
   **Solution:** Check if pygame installed correctly: `pip list | grep pygame`
   
   ### Issue: Animation too fast/slow
   **Solution:** Modify `ANIMATION_DELAY` in pathfinder.py (line 30)
```

**End of README**
