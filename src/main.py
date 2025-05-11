import sys
import matplotlib.pyplot as plt
import numpy as np
from simulator import Simulator

def visualize_cores(cores):
    """Visualize core registers in a heatmap"""
    num_cores = len(cores)
    num_registers = len(cores[0].registers)
    register_matrix = np.array([core.registers for core in cores])

    plt.figure(figsize=(12, 5))
    plt.imshow(register_matrix, cmap="coolwarm", aspect="auto")
    plt.title("Core Registers - Final State")
    plt.xlabel("Register Index")
    plt.ylabel("Core ID")
    plt.yticks(range(0, 4, 1))  
    plt.xticks(range(0, 33, 1))  
    
    # Annotate values
    for i in range(num_cores):
        for j in range(num_registers):
            plt.text(j, i, f"{register_matrix[i, j]}", 
                    ha="center", va="center", color="black")
    
    plt.tight_layout()
    plt.show()

def visualize_memory(memory):
    """Visualize memory as a 64x64 grid with labeled values."""
    memory_slice = memory[:1024]  # Ensure 4096 values
    if len(memory_slice) < 1024:
        memory_slice += [0] * (1024 - len(memory_slice))
    
    memory_grid = np.array(memory_slice).reshape(32, 32)
    
    plt.figure(figsize=(12, 12))
    plt.imshow(memory_grid, cmap="coolwarm", aspect="auto")
    plt.title("Memory Values (32x32 Grid)")
    plt.xlabel("Column Index")
    plt.ylabel("Row Index")
    plt.xticks(range(0, 32, 1))
    plt.yticks(range(0, 32, 1))
    
    # Annotate values
    for i in range(32):
        for j in range(32):
            plt.text(j, i, f"{memory_grid[i, j]}", ha="center", va="center", color="black", fontsize=6)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python run.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        cache_param_file = sys.argv[2]
        simulator = Simulator(cache_param_file)
        simulator.run_simulator(assembly_file)
        
        # Show visualizations separately
        visualize_cores(simulator.cores)
        # visualize_memory(simulator.mem.word)