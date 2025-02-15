from memory import Memory
from core import Core
from asm_parser import parse_assembly_file
import sys


def run_program(assembly_file: str):
    instructions, label_map = parse_assembly_file(assembly_file)
    print(f"Loaded {len(instructions)} instructions with labels: {label_map}")

    mem = Memory(size_in_bytes=4096)

    core = Core(core_id=0)
    core.program = instructions

    cycle = 0

    while core.pc < len(core.program):
        instr = core.program[core.pc]
        print(
            f"Cycle: {cycle} Core_id:{core.core_id} Executing pc={core.pc} {instr.original_line}")
        core.execute_instruction(instr, mem, label_map)
        cycle += 1

    print("\nProgram execution complete!")
    print(f"Total cycles: {cycle}")
    print(f"Final register state for Core {core.core_id}: {core.registers}")
    print("\nMemory Dump (first 16 words):")

    for idx in range(16):
        print(f"Address {idx*4}: {mem.word[idx]}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python execution_engine.py <assembly_file>")
    else:
        run_program(sys.argv[1])
