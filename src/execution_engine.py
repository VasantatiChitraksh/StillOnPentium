from memory import Memory
from core import Core
from asm_parser import parse_assembly_file
import sys

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


def run_program(assembly_file: str):
    data_instructions, instructions, label_map = parse_assembly_file(
        assembly_file)
    print(f"Loaded {len(instructions)} instructions with labels: {label_map}")

    mem = Memory(size_in_bytes=4096)
    core = Core(core_id=0)
    core.program = instructions

    registers_history = []  # Stores 1×32 register snapshots
    memory_history = []  # Stores 32×32 memory snapshots (first 1024 addresses)

    def record_state():
        # Capture single-core registers (1x32 matrix)
        regs_snapshot = np.array([core.registers[:]])  # Now just (1, 32)
        registers_history.append(regs_snapshot)

        # Capture first 1024 memory addresses (reshaped as 32x32)
        mem_snapshot = np.array(mem.word[:1024]).reshape(32, 32)
        memory_history.append(mem_snapshot)

    # Record initial state
    record_state()

    cycle = 0

    while core.pc < len(core.program):
        instr = core.program[core.pc]
        print(f"Cycle: {cycle} Executing pc={core.pc} {instr.original_line}")
        core.execute_instruction(instr, mem, label_map)
        cycle += 1
        record_state()

    fig, axes = plt.subplots(2, 1, figsize=(12, 4))  # Adjusted figure size

    def update(frame):
        # Clear previous frames
        axes[0].clear()
        axes[1].clear()

        # --- Registers Heatmap (1x32) ---
        reg_matrix = registers_history[frame]
        cax1 = axes[0].imshow(reg_matrix, cmap="Blues", aspect="auto")
        axes[0].set_title(f"Registers - Cycle {frame}")
        axes[0].set_xticks(range(32))
        axes[0].set_yticks([0])
        axes[0].set_yticklabels(["Core 0"])  # Only one core

        # Overlay register values
        for j in range(32):
            axes[0].text(j, 0, f"{reg_matrix[0, j]}",
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

    print("\nProgram execution complete!")
    print(f"Total cycles: {cycle}")
    print(f"Final register state: {core.registers}")
    print("\nMemory Dump (first core words):")

    for idx in range(0, 256, 6):
        addresses = [
            f"Address {i*4}: {mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
        print("  |  ".join(addresses))

    ani = animation.FuncAnimation(fig, update, frames=range(0, len(
        registers_history), 16), interval=10, blit=False)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python execution_engine.py <assembly_file>")
    else:
        run_program(sys.argv[1])
