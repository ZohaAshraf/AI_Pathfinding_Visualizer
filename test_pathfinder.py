"""
Test and demonstration script for AI Pathfinder
Run this to see all algorithms in action
"""

import sys
import os

# Make sure pathfinder is importable
sys.path.insert(0, os.path.dirname(__file__))

from pathfinder import *

def create_simple_test_environment():
    """Create a simple test environment with clear path"""
    env = GridEnvironment(size=15)  # Smaller grid for faster testing
    env.set_start(2, 2)
    env.set_target(12, 12)
    
    # Add some walls
    for i in range(5, 10):
        env.add_wall(i, 7)
    
    return env

def create_complex_test_environment():
    """Create a complex environment with many obstacles"""
    env = GridEnvironment(size=20)
    env.set_start(1, 1)
    env.set_target(18, 18)
    
    # Create maze-like structure
    for i in range(5, 15):
        env.add_wall(i, 10)
    
    for j in range(5, 15):
        if j != 10:
            env.add_wall(5, j)
            env.add_wall(14, j)
    
    return env

def test_algorithm(algorithm_class, env_type="simple", **kwargs):
    """Test a specific algorithm"""
    print(f"\n{'='*70}")
    print(f"Testing {algorithm_class.__name__} with {env_type} environment")
    print(f"{'='*70}\n")
    
    if env_type == "simple":
        env = create_simple_test_environment()
    else:
        env = create_complex_test_environment()
    
    try:
        run_algorithm(algorithm_class, env, **kwargs)
        print(f"✓ {algorithm_class.__name__} completed successfully")
    except Exception as e:
        print(f"✗ {algorithm_class.__name__} failed: {e}")

def run_all_tests():
    """Run all algorithms with both simple and complex environments"""
    
    algorithms = [
        (BFS, "Breadth-First Search", {}),
        (DFS, "Depth-First Search", {}),
        (UCS, "Uniform-Cost Search", {}),
        (DLS, "Depth-Limited Search", {"limit": 15}),
        (IDDFS, "Iterative Deepening DFS", {}),
        (BidirectionalSearch, "Bidirectional Search", {}),
    ]
    
    print("\n" + "="*70)
    print("AI PATHFINDER - COMPREHENSIVE ALGORITHM TEST SUITE")
    print("="*70)
    
    # Run simple tests
    print("\n\n--- SIMPLE ENVIRONMENT TESTS ---\n")
    for algo_class, name, kwargs in algorithms:
        test_algorithm(algo_class, "simple", **kwargs)
        input("\nPress Enter to continue to next algorithm...")
    
    # Run complex tests
    print("\n\n--- COMPLEX ENVIRONMENT TESTS ---\n")
    for algo_class, name, kwargs in algorithms:
        test_algorithm(algo_class, "complex", **kwargs)
        input("\nPress Enter to continue to next algorithm...")
    
    print("\n\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)

def quick_demo():
    """Quick demonstration of BFS"""
    print("\n" + "="*70)
    print("QUICK DEMO - Running BFS")
    print("="*70 + "\n")
    
    env = create_simple_test_environment()
    run_algorithm(BFS, env)

if __name__ == "__main__":
    print("AI Pathfinder Test Suite")
    print("=" * 70)
    print("\nChoose an option:")
    print("1. Quick Demo (BFS only)")
    print("2. Run All Tests (all algorithms, both environments)")
    print("3. Test specific algorithm")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-3): ").strip()
    
    if choice == "0":
        print("Exiting...")
    elif choice == "1":
        quick_demo()
    elif choice == "2":
        run_all_tests()
    elif choice == "3":
        print("\nSelect algorithm:")
        print("1. BFS")
        print("2. DFS")
        print("3. UCS")
        print("4. DLS")
        print("5. IDDFS")
        print("6. Bidirectional")
        
        algo_choice = input("Enter algorithm (1-6): ").strip()
        env_choice = input("Environment (simple/complex): ").strip().lower()
        
        algorithms = {
            "1": (BFS, {}),
            "2": (DFS, {}),
            "3": (UCS, {}),
            "4": (DLS, {"limit": 15}),
            "5": (IDDFS, {}),
            "6": (BidirectionalSearch, {}),
        }
        
        if algo_choice in algorithms:
            algo_class, kwargs = algorithms[algo_choice]
            test_algorithm(algo_class, env_choice or "simple", **kwargs)
        else:
            print("Invalid choice")
    else:
        print("Invalid choice")
