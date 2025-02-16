import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

from memory import Memory
from core import Core
from asm_parser import parse_assembly_file


def run_simulator(assembly_file: str):
    # 1. Parse assembly and initialize memory/cores
    instructions, label_map = parse_assembly_file(assembly_file)
    mem = Memory(size_in_bytes=4096)
    cores = [Core(core_id=i) for i in range(4)]
    for core in cores:
        core.program = instructions

    # 2. Track history of registers and memory
    registers_history = []  # Stores 4×32 register snapshots
    # Stores 32×32 memory snapshots (first 1024 addresses)
    memory_history = []

    # Helper function to record states
    def record_state():
        # Capture all 4 cores' registers (4x32 matrix)
        regs_snapshot = np.array([core.registers[:] for core in cores])
        registers_history.append(regs_snapshot)

        # Capture first 1024 memory addresses (reshaped as 32x32)
        mem_snapshot = np.array(mem.word[:1024]).reshape(32, 32)
        memory_history.append(mem_snapshot)

    # Record initial state
    record_state()

    # 3. Main simulation loop
    cycle = 0
    while any(core.pc < len(core.program) for core in cores):
        for core in cores:
            if core.pc < len(core.program):
                instr = core.program[core.pc]
                core.execute_instruction(instr, mem, label_map)
        cycle += 1

        # Record state after this cycle
        record_state()

    print(f"Simulation completed in {cycle} cycles.")

    # 4. Dynamic Visualization (Registers + Memory)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    def update(frame):
        # Clear previous frames
        axes[0].clear()
        axes[1].clear()

        # --- Registers Heatmap (4x32) ---
        reg_matrix = registers_history[frame]
        cax1 = axes[0].imshow(reg_matrix, cmap="Blues", aspect="auto")
        axes[0].set_title(f"Registers - Cycle {frame}")
        axes[0].set_xticks(range(32))
        axes[0].set_yticks(range(4))
        axes[0].set_yticklabels([f"Core {i}" for i in range(4)])

        # Overlay register values
        for i in range(4):
            for j in range(32):
                axes[0].text(j, i, f"{reg_matrix[i, j]}",
                             ha="center", va="center", color="black")

        # --- Memory Heatmap (32x32) ---
        mem_matrix = memory_history[frame]
        cax2 = axes[1].imshow(mem_matrix, cmap="Oranges", aspect="auto")
        axes[1].set_title(f"Memory (First 1024 addresses) - Cycle {frame}")
        axes[1].set_xticks(range(32))
        axes[1].set_yticks(range(32))

        # Overlay memory values
        for i in range(32):
            for j in range(32):
                axes[1].text(j, i, f"{mem_matrix[i, j]}", ha="center",
                             va="center", color="black", fontsize=8)

        return cax1, cax2

    ani = animation.FuncAnimation(fig, update, frames=range(0, len(
        registers_history), 16), interval=10, blit=False)

    print(f"Simulation done in {cycle} cycles")
    for i, core in enumerate(cores):
        print(f"Core {i} registers: {core.registers}")

    print("\nMemory Dump:")

    for idx in range(0, 1024, 6):
        addresses = [
            f"Address {i*4}: {mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
        print("  |  ".join(addresses))

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python simulator.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        run_simulator(assembly_file)
