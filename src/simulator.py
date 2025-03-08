import sys
from memory import Memory
import core
from asm_parser import parse_assembly_file

class Simulator:

    pc_changed = [False] * 4
    new_pc = [0] * 4
    clock = 0
    fetch_ins = [True] * 4
    def __init__(self):
        self.mem = Memory(size_in_bytes=4096)  # Initialize memory
        self.cores = [core.Core(core_id=i) for i in range(4)]  # Initialize cores

    def execute_data_instruction(self, data_instructions, data_values: int, memory) -> dict:
        label_map = {}
        address = 1024 - data_values * 4
        for data_instr in data_instructions:
            if data_instr.label:
                label_map[data_instr.label] = address
            for value in data_instr.values:
                memory.write_word(address, value)
                address += 4
        return label_map

    def instruction_fetch(self, instructions):
        for i in range(1):
            if not self.fetch_ins[i]:
                continue    
        
            self.fetch_ins[i] = False
            # if core_id == 0:
                # print("Writing to ID:", instructions[pc])
            if self.pc_changed[i]:
                self.cores[i].pc = self.new_pc[i]
                self.pc_changed[i] = False
                self.cores[i].IF_ID = None
                rd = self.cores[i].ID_EX[1]
                opcode = self.cores[i].ID_EX[0]
                if opcode in ["add", "sub", "mul", "addi", "jalr", "slli", "la", "jal", "lw"]:
                    rd_id = int(rd[1:])
                    self.cores[i].register_active[rd_id] -= 1
                self.cores[i].ID_EX = []
                self.fetch_ins[i] = True
            else:
                if self.cores[i].pc >= len(instructions):
                    continue
                self.cores[i].IF_ID = instructions[self.cores[i].pc]
                self.cores[i].pc += 1
            if self.cores[i].pc >= len(instructions):
                continue

    def run_simulator(self, assembly_file: str):
        def decimal_to_hex(n: int) -> str:
            return f"0x{n:x}"

        instructions, label_map, data_instructions, data_values = parse_assembly_file(assembly_file)

        # Initialize memory and cores
        data_label_map = self.execute_data_instruction(data_instructions, data_values, self.mem)
        for core in self.cores:
            core.labels_map.update(label_map)
            core.labels_map.update(data_label_map)

        cycle = 0
        pipeline_active = True

        while pipeline_active:
            for i in range(4):
                core=self.cores[i]
                core.execute_instruction(self.mem,self.fetch_ins)
            self.instruction_fetch(instructions)

            fetch_possible = True
            if self.cores[0].pc >= len(instructions):
                fetch_possible = False

            # Check if pipeline should stop
            cycle += 1
            if not fetch_possible and all(not core.IF_ID and not core.ID_EX and not core.EX_MEM and not core.MEM_WB for core in self.cores):
                pipeline_active = False

        # Print simulation results
        print(f"Simulation completed in {cycle} cycles (Assuming Parallelism).")
        print(f"Simulation done in {cycle * 4} cycles (No Parallelism).\n")
        print(f"No of Stalls in each core:")
        total_stall = 0
        for core in self.cores:
            print(f"Core ID:{core.core_id} | No Of Stalls: {core.stall_count}")
            total_stall += core.stall_count
        print(f"Total No of Stalls are:{total_stall}\n")
        for i, core in enumerate(self.cores):
            print(f"Core {i} registers: {core.registers}")

        print("\nMemory Dump:")

        for idx in range(0, 1024, 6):
            addresses = [
                f"{decimal_to_hex(i*4)}: {self.mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
            print("  |  ".join(addresses))
