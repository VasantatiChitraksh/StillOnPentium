import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

from memory import Memory
from core import Core
from asm_parser import parse_assembly_file,DataInstruction


def run_simulator(assembly_file: str):
    def decimal_to_hex(n: int) -> str:
        return f"0x{n:x}"
    
    instructions, label_map,data_instructions,data_values = parse_assembly_file(assembly_file)
    mem = Memory(size_in_bytes=4096)
    cores = [Core(core_id=i) for i in range(4)]
    for core in cores:
        data_label_map = core.execute_data_instruction(data_instructions, data_values, mem)
        label_map.update(data_label_map)
        core.program = instructions

    registers_history = [] 
    memory_history = []

    print("Memory Dump Before Execution:\n")
    for idx in range(0, 1024, 6):
        addresses = [
                f"{decimal_to_hex(i*4)}: {mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
        print("  |  ".join(addresses))

    def record_state():
        # Capture all core registers (4x32 matrix)
        regs_snapshot = np.array([core.registers[:] for core in cores])
        registers_history.append(regs_snapshot)

        # Capture first 1024 memory addresses (reshaped as 32x32)
        mem_snapshot = np.array(mem.word[:1024]).reshape(32, 32)
        memory_history.append(mem_snapshot)

    record_state()

    cycle = 0
    while any(core.pc < len(core.program) for core in cores):
        for core in cores:
            if core.pc < len(core.program):
                instr = core.program[core.pc]
                core.execute_instruction(instr, mem, label_map)
        cycle += 1

        # Record state after this cycle
        record_state()

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    def update(frame):
        axes[0].clear()
        axes[1].clear()

        reg_matrix = registers_history[frame]
        cax1 = axes[0].imshow(reg_matrix, cmap="Blues", aspect="auto")
        axes[0].set_title(f"Registers - Cycle {frame}")
        axes[0].set_xticks(range(32))
        axes[0].set_yticks(range(4))
        axes[0].set_yticklabels([f"Core {i}" for i in range(4)])

        for i in range(4):
            for j in range(32):
                axes[0].text(j, i, f"{reg_matrix[i, j]}",
                             ha="center", va="center", color="black")

        mem_matrix = memory_history[frame]
        cax2 = axes[1].imshow(mem_matrix, cmap="Oranges", aspect="auto")
        axes[1].set_title(f"Memory (First 1024 addresses) - Cycle {frame}")
        axes[1].set_xticks(range(32))
        axes[1].set_yticks(range(32))

        for i in range(32):
            for j in range(32):
                axes[1].text(j, i, f"{mem_matrix[i, j]}", ha="center",
                             va="center", color="black", fontsize=8)

        return cax1, cax2

    ani = animation.FuncAnimation(fig, update, frames=range(0, len(
        registers_history), 16), interval=10, blit=False)
    
    print("\n")
    for i, core in enumerate(cores):
        print(f"Core {i} registers: {core.registers}")

    print("\nMemory Dump:")

    for idx in range(0, 1024, 6):
        addresses = [
            f"{decimal_to_hex(i*4)}: {mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
        print("  |  ".join(addresses))

    print(f"Simulation completed in {cycle} cycles (Assuming Parallelism).")
    print(f"Simulation done in {cycle*4} cycles (No Parallelism).")

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python simulator.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        run_simulator(assembly_file)
