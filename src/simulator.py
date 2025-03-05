import sys
import numpy as np

from memory import Memory
from core import Core
from asm_parser import parse_assembly_file, DataInstruction
from helpers import *


def run_simulator(assembly_file: str):
    def decimal_to_hex(n: int) -> str:
        return f"0x{n:x}"

    instructions, label_map, data_instructions, data_values = parse_assembly_file(
        assembly_file)

    # The parsed file is creating a instruction list, label map, data instruction list and data values, this serves as the common memory for all instruction as they are stored.
    mem = Memory(size_in_bytes=4096)
    cores = [Core(core_id=i) for i in range(4)]
    data_label_map = execute_data_instruction(
        data_instructions, data_values, mem)
    for core in cores:
        label_map.update(data_label_map)

    cycle = 0
    while any(core.pc < len(instructions) for core in cores):
        for core in cores:
            if core.pc < len(instructions):
                instruction_fetch(instructions, cores, core.core_id, core.pc)
                core.execute_instruction(core.pipeline_registers[0].instruction, mem, label_map)
        cycle += 1

    print(f"Simulation completed in {cycle} cycles.")
    print(f"Simulation done in {cycle} cycles")
    for i, core in enumerate(cores):
        print(f"Core {i} registers: {core.registers}")

    print("\nMemory Dump:")

    for idx in range(0, 1024, 6):
        addresses = [
            f"{decimal_to_hex(i*4)}: {mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
        print("  |  ".join(addresses))

    print(f"Simulation completed in {cycle} cycles (Assuming Parallelism).")
    print(f"Simulation done in {cycle*4} cycles (No Parallelism).")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python simulator.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        run_simulator(assembly_file)
