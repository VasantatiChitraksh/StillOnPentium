import sys
from cache import Cache
from memory import Memory
import core
from asm_parser import parse_assembly_file


class Simulator:
    pc_changed = [False] * 4
    new_pc = [0] * 4
    clock = 0
    fetch_ins = [True] * 4

    def __init__(self):
        self.cache_block_size = 8  # bytes
        cache_size = 64
        associativity = 4
        self.cache1 = Cache(cache_size, self.cache_block_size, associativity)
        self.cache_instruction = Cache(cache_size, self.cache_block_size, associativity)
        self.cache2 = Cache(cache_size, self.cache_block_size, associativity)
        self.mem = Memory(size_in_bytes=4096)  # Initialize memory
        self.cores = [core.Core(core_id=i)
                      for i in range(4)]  # Initialize cores
        self.latency_config = {
            'add': 1,
            'mul': 1,
            'sub': 1,
            'lw': 1,
            'sw': 1,
            'bne': 1,
            'beq': 1,
            'bge': 1,
            'la': 1,
            'li': 1,
            'addi': 1,
            'slli': 1,
            'j': 1,
            'jal': 1,
            'jalr': 1
        }
        self.instruction_fetch_stall = []
        self.data_fwd_on = input(
            "Do you want to enable data forwarding? (y/n): ")
                
    def execute_data_instruction(self, data_instructions, data_values: int, memory) -> dict:
        label_map = {}
        address = 0
        memory.set_data_section_end(address)
        for data_instr in data_instructions:
            if data_instr.label:
                label_map[data_instr.label] = address
            for value in data_instr.values:
                memory.write_word(address, value)
                address += 4
        return label_map

    def get_latency(self):
        print("Enter opcode and latency in the format: opcode latency")
        print("Type 'exit' when finished.")
        print("Available opcodes:", ", ".join(self.latency_config.keys()))

        while True:
            user_input = input("Enter opcode and latency: ").strip()
            if user_input.lower() == "exit":
                break
            try:
                opcode, latency = user_input.split()
                latency = int(latency)
                if opcode in self.latency_config:
                    if latency > 0:
                        # Update if valid
                        self.latency_config[opcode] = latency
                    else:
                        print("Latency must be positive.")
                else:
                    print(
                        f"Invalid opcode '{opcode}'. Please enter a valid opcode.")

            except ValueError:
                print("Invalid format. Please enter in 'opcode latency' format.")
            except IndexError:
                print("Please enter both opcode and latency.")

    def instruction_fetch(self, instructions):
        instructions_fetch_possible = [False] * 4

        if self.cores[0].pc == self.cores[1].pc == self.cores[2].pc == self.cores[3].pc:
            instructions_fetch_possible = [True] * 4
            self.instruction_fetch_stall = []
        else:
            # if not self.instruction_fetch_stall:
            #     self.instruction_fetch_stall.extend(range(4))

            # core_id = self.instruction_fetch_stall.pop(0)
            # instructions_fetch_possible[core_id] = True
            if not self.instruction_fetch_stall:
                for i in range(4):
                    if self.cores[i].pc >= len(instructions):
                        continue
                    self.instruction_fetch_stall.append(i)

            core_id = self.instruction_fetch_stall.pop(0)
            instructions_fetch_possible[core_id] = True

        for i in range(4):
            self.cores[i].isWB = False
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
    
    def cache_controller(self, address, data, operation):
        if operation == 0:  # Load operation
            # Check cache1 cache first
            data = self.cache1.fetch(address)
            if data is None:
                data = self.cache2.fetch(address)
                if data is None:
                    data = self.mem.read_word(address)
                    temp_data_array=[0]*(self.cache_block_size//4)
                    for i in range(self.cache_block_size//4):
                        temp_data_array[i]=self.mem.read_word(address//4+i)
                    temp_addr,temp_data_array,temp_value_changed=self.cache1.replace_line(address, temp_data_array,False)
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.replace_line(temp_addr, temp_data_array,temp_value_changed)
                    if(temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(temp_addr//4+i,temp_data_array[i])
                else:
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.get_line_data(address)
                    temp_addr,temp_data_array,temp_value_changed=self.cache1.replace_line(temp_addr, temp_data_array,temp_value_changed)
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.replace_line(temp_addr, temp_data_array,temp_value_changed)
                    if(temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(temp_addr//4+i,temp_data_array[i])
            return data
        elif operation == 1:  # Store operation
            # Store in cache1 cache first
            success=self.cache1.store(address, data)

            # DONT FORGET TO UPDATE THE MEMORY AFTER END OF SIMULATION,you SHOULD DO IT 
            self.mem.write_word(address, data)
            print("success cache1",success)
            if success== False:
                # If cache1 cache miss, store in cache2 cache
                success=self.cache2.store(address, data)
                print("success cache2",success)
                if success==False:
                    # If cache2 cache miss, store in main memory
                    self.mem.write_word(address, data)
                    # Store in cache1 cache for consistency
                    temp_data_array=[0]*(self.cache_block_size//4)
                    for i in range(self.cache_block_size//4):
                        temp_data_array[i]=self.mem.read_word(address//4+i)
                    print("temp data array",temp_data_array)
                    temp_addr,temp_data_array,temp_value_changed=self.cache1.replace_line(address, temp_data_array,False)
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.replace_line(temp_addr, temp_data_array,temp_value_changed)
                    if(temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(temp_addr//4+i,temp_data_array[i])
                else:
                    # If cache2 cache hit, update cache1 cache
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.get_line_data(address)
                    temp_addr,temp_data_array,temp_value_changed=self.cache1.replace_line(temp_addr, temp_data_array,temp_value_changed)
                    temp_addr,temp_data_array,temp_value_changed=self.cache2.replace_line(temp_addr, temp_data_array,temp_value_changed)    
                    if(temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(temp_addr//4+i,temp_data_array[i])
            # Also store in cache2 cache for consistenc
        
    def run_simulator(self, assembly_file: str):
        def decimal_to_hex(n: int) -> str:
            return f"0x{n:x}"

        self.get_latency()
        print("\nCONSOLE\n")
        instructions, label_map, data_instructions, data_values = parse_assembly_file(
            assembly_file)

        # Initialize memory and cores
        data_label_map = self.execute_data_instruction(
            data_instructions, data_values, self.mem)
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
                core = self.cores[i]
                core.execute_instruction(self.mem, self.fetch_ins, self)
            self.instruction_fetch(instructions)

            fetch_possible = True
            if all(core.pc >= len(instructions) for core in self.cores):
                fetch_possible = False

            # Check if pipeline should stop
            cycle += 1
            if not fetch_possible and all(not core.IF_ID and not core.ID_EX and not core.EX_MEM and not core.MEM_WB for core in self.cores):
                pipeline_active = False

        print("---------------------------------------------------------------------------------------------------------")
        print("\nRegisters:")
        for i, core in enumerate(self.cores):
            print(f"Core {i} registers: {core.registers}")

        print("\nMemory Dump:")

        for idx in range(0, 1024, 6):
            addresses = [
                f"{decimal_to_hex(i*4)}: {self.mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
            print("  |  ".join(addresses))

        # Print simulation Statistics
        print(f"\nSimulation completed in {cycle} cycles (Parallelism).")
        print("\nNo of Stalls in each core:")
        total_stall = 0
        for core in self.cores:
            print(f"Core ID:{core.core_id} | No Of Stalls: {core.stall_count}")
            total_stall += core.stall_count
        print(f"Total No of Stalls are:{total_stall}")

        print("\nIPC For Each Core:")
        for core in self.cores:
            print(
                f"Core ID:{core.core_id} | IPC:{core.instruction_count/cycle}")
