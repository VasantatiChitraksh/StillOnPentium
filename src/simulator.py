from memory import Memory
from core import Core
from asm_parser import parse_assembly_file
import sys


def run_simulator(assembly_file: str):
    instructions, label_map = parse_assembly_file(assembly_file)
    mem = Memory(size_in_bytes=4096)
    cores = [Core(core_id=i) for i in range(4)]
    for core in cores:
        core.program = instructions

    cycle = 0
    while any(core.pc < len(core.program) for core in cores):
        for core in cores:
            if core.pc < len(core.program):
                instr = core.program[core.pc]
                core.execute_instruction(instr, mem, label_map)
        cycle += 1
    print(f"Simulation done in {cycle} cycles")
    for i, core in enumerate(cores):
        print(f"Core {i} registers: {core.registers}")

    print("/n Memory Dump:")
    for idx in range(1024):
        print(f"Address {idx*4}: {mem.word[idx]}")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: python simulator.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        run_simulator(assembly_file)
