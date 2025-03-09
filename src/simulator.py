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
        self.latency_config = {}
        self.instruction_fetch_stall = []
        self.structural_stall = 0
        self.data_fwd_on = input("Do you want to enable data forwarding? (y/n): ")

    def execute_data_instruction(self, data_instructions, data_values: int, memory) -> dict:
        label_map = {}
        address = 4096 - data_values * 4
        memory.set_data_section_end(address)
        for data_instr in data_instructions:
            if data_instr.label:
                label_map[data_instr.label] = address
            for value in data_instr.values:
                memory.write_word(address, value)
                address += 4
        return label_map
    
    def get_latency(self):
        valid_opcodes = {"add", "sub", "mul", "slli", "addi", "j", "jal", "bne", "beq", "bge", "lw", "la", "sw"}

        print(f"Available Opcodes: {', '.join(valid_opcodes)}")
        print("Start entering in the format 'opcode' then latency. Type 'exit' to stop.")

        self.latency_config = []  # Ensure it's initialized

        while True:
            opcode = input("Enter opcode: ").strip()
            
            if opcode == "exit":
                break

            if opcode not in valid_opcodes:
                print(f"Invalid opcode '{opcode}'. Please enter a valid opcode from the list.")
                continue

            try:
                value = int(input("Enter latency: ").strip())
                if value <= 0:
                    print("Latency must be a positive integer. Try again.")
                    continue
                self.latency_config.append((opcode, value))  # Store as tuple
            except ValueError:
                print("Invalid input! Please enter a valid integer for latency.")


    def instruction_fetch(self, instructions):
        instructions_fetch_possible = [False] * 4

        if self.cores[0].pc == self.cores[1].pc == self.cores[2].pc == self.cores[3].pc:
            instructions_fetch_possible = [True] * 4
            self.instruction_fetch_stall = []
        else:
            self.structural_stall += 1
            if not self.instruction_fetch_stall:
                self.instruction_fetch_stall.extend(range(4))

            core_id = self.instruction_fetch_stall.pop(0)
            instructions_fetch_possible[core_id] = True

        for i in range(4):
            if not self.fetch_ins[i]:
                continue    
        
            if instructions_fetch_possible[i] and not self.pc_changed[i] and self.fetch_ins[i]:
                self.fetch_ins[i] = False
            
            if self.pc_changed[i]:
                self.cores[i].pc = self.new_pc[i]
                self.pc_changed[i] = False
                self.cores[i].execute_prev_done = True
                self.cores[i].IF_ID = None
                if self.cores[i].ID_EX:
                    rd = self.cores[i].ID_EX[1]
                    opcode = self.cores[i].ID_EX[0]
                    if opcode in ["add", "sub", "mul", "addi", "jalr", "slli", "la", "jal", "lw"]:
                        rd_id = int(rd[1:])
                        self.cores[i].register_active[rd_id] -= 1
                self.cores[i].ID_EX = []
                self.fetch_ins[i] = True
                continue
            if instructions_fetch_possible[i]:
                if self.cores[i].pc >= len(instructions):
                    continue
                self.cores[i].IF_ID = instructions[self.cores[i].pc]
                self.cores[i].pc += 1
            if self.cores[i].pc >= len(instructions):
                continue

    def run_simulator(self, assembly_file: str):
        def decimal_to_hex(n: int) -> str:
            return f"0x{n:x}"

        self.get_latency()
        instructions, label_map, data_instructions, data_values = parse_assembly_file(assembly_file)

        # Initialize memory and cores
        data_label_map = self.execute_data_instruction(data_instructions, data_values, self.mem)
        for core in self.cores:
            core.labels_map.update(label_map)
            core.labels_map.update(data_label_map)
            core.latency_map = self.latency_config
            if self.data_fwd_on == 'y':
                core.isDF = True
            else:
                core.isDF = False

        cycle = 0
        pipeline_active = True

        while pipeline_active:
            for i in range(4):
                core=self.cores[i]
                core.execute_instruction(self.mem,self.fetch_ins)
            self.instruction_fetch(instructions)

            fetch_possible = True
            if all(core.pc >= len(instructions) for core in self.cores):
                fetch_possible = False

            # Check if pipeline should stop
            cycle += 1
            if not fetch_possible and all(not core.IF_ID and not core.ID_EX and not core.EX_MEM and not core.MEM_WB for core in self.cores):
                pipeline_active = False
        
        print("Registers:\n")
        for i, core in enumerate(self.cores):
            print(f"Core {i} registers: {core.registers}")

        print("\nMemory Dump:")

        for idx in range(0, 1024, 6):
            addresses = [
                f"{decimal_to_hex(i*4)}: {self.mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
            print("  |  ".join(addresses))

        # Print simulation Statistics
        print(f"Simulation completed in {cycle} cycles (Assuming Parallelism).")
        print(f"Simulation done in {cycle * 4} cycles (No Parallelism).\n")
        print("No of Stalls in each core:")
        total_stall = 0
        for core in self.cores:
            print(f"Core ID:{core.core_id} | No Of Stalls: {core.stall_count}")
            total_stall += core.stall_count
        print(f"Total No of Stalls are:{total_stall+self.structural_stall}")
        print(f"Total no of structural stalls:{self.structural_stall}")

        print("CPI For Each Core:")
        for core in self.cores:
            print(f"Core ID:{core.core_id} | CPI:{cycle/core.instruction_count}")

