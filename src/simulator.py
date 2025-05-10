import sys
from cache import Cache
from memory import Memory
import core
from asm_parser import parse_assembly_file
import math

class Simulator:
    pc_changed = [False] * 4
    new_pc = [0] * 4
    clock = 0
    fetch_ins = [True] * 4

    def __init__(self):
        self.replacement_policy = input(
            "Enter replacement policy (0 for LRU, 1 for NRU): ")
        self.instruction_address_start = 512
        self.L1_Instr_Latency = 2
        self.L1_Data_Latency = 2
        self.L2_Latency = 4
        self.scratch_pad_latency = 1
        self.main_merory_Latency = 10
        self.L1_Instr_cache_size = 64
        self.L1_Instr_cache_associativity = 4
        self.L1_Data_cache_size = 64
        self.L1_Data_cache_associativity = 4
        self.L2_cache_size = 128
        self.L2_cache_associativity = 8
        self.cache_block_size = 8
        self.offset_bits_length = int(math.log2(self.cache_block_size))
        self.offset_mask = (1 << self.offset_bits_length) - 1
        self.cache1 = Cache(self.L1_Data_cache_size,
                            self.cache_block_size, self.L1_Data_cache_associativity,self.replacement_policy)
        self.cache_instruction = Cache(
            self.L1_Instr_cache_size, self.cache_block_size, self.L1_Instr_cache_associativity,self.replacement_policy)
        self.cache2 = Cache(self.L2_cache_size,
                            self.cache_block_size, self.L2_cache_associativity,self.replacement_policy)
        self.mem = Memory(size_in_bytes=4096)  # Initialize memory
        self.scratch_pad = Memory(size_in_bytes=400)  # Initialize scratchpad
        self.scratchpad_start = 2048
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
            'jalr': 1,
            "lw_spm":1,
            "sw_spm":1
        }
        self.instruction_fetch_stall = []
        self.sync_reached = [False]*4
        self.data_fwd_on = input(
            "Do you want to enable data forwarding? (y/n): ")
        self.stats = {}


    def get_scratchpad_latency(self):
        return self.scratch_pad_latency
    
    def excute_scratchpad_instructions(self, scratchpad_instructions, scratchpad_values: int, memory) -> dict:
        label_map = {}
        address = 0
        memory.set_data_section_end(address)
        for scratchpad_instr in scratchpad_instructions:
            if scratchpad_instr.label:
                label_map[scratchpad_instr.label] = address
            for value in scratchpad_instr.values:
                memory.write_word(address, value)
                address += 4
        
        address = self.scratchpad_start
        self.mem.set_data_section_end(address)
        for scratchpad_instr in scratchpad_instructions:
            for value in scratchpad_instr.values:
                self.mem.write_word(address, value)
                address += 4
        return label_map

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

    def get_cache_latency(self):
        print("Enter cache latency in the format: cache_type latency")
        print("Type 'exit' when finished.")
        print("Available cache types: L1_Instr, L1_Data, L2")

        while True:
            user_input = input("Enter cache type and latency: ").strip()
            if user_input.lower() == "exit":
                break
            try:
                cache_type, latency = user_input.split()
                latency = int(latency)
                if cache_type in ["L1_Instr", "L1_Data", "L2"]:
                    if latency > 0:
                        # Update if valid
                        if cache_type == "L1_Instr":
                            self.L1_Instr_Latency = latency
                        elif cache_type == "L1_Data":
                            self.L1_Data_Latency = latency
                        elif cache_type == "L2":
                            self.L2_Latency = latency
                    else:
                        print("Latency must be positive.")
                else:
                    print(
                        f"Invalid cache type '{cache_type}'. Please enter a valid cache type.")

            except ValueError:
                print("Invalid format. Please enter in 'cache_type latency' format.")
            except IndexError:
                print("Please enter both cache type and latency.")

    def get_cache_details(self):
        print("Enter cache details in the format: cache_type block_size associativity cache_size")
        print("Type 'exit' when finished.")
        print("Available cache types: L1_Instr, L1_Data, L2")

        while True:
            user_input = input("Enter cache type, block size, associativity and cache size: ").strip()
            if user_input.lower() == "exit":
                break

            try:
                cache_type, block_size, associativity, cache_size = user_input.split()
                block_size = int(block_size)
                associativity = int(associativity)
                cache_size = int(cache_size)

                if block_size <= 0 or associativity <= 0 or cache_size <= 0:
                    print("All values must be positive integers.")
                    continue

                if cache_type == "L1_Instr":
                    self.cache_block_size = block_size
                    self.L1_Instr_cache_associativity = associativity
                    self.L1_Instr_cache_size = cache_size
                elif cache_type == "L1_Data":
                    self.cache_block_size = block_size
                    self.L1_Data_cache_associativity = associativity
                    self.L1_Data_cache_size = cache_size
                elif cache_type == "L2":
                    self.cache_block_size = block_size
                    self.L2_cache_associativity = associativity
                    self.L2_cache_size = cache_size
                else:
                    print("Invalid cache type. Please use L1_Instr, L1_Data, or L2.")

            except ValueError:
                print("Invalid format. Please enter in 'cache_type block_size associativity cache_size' format.")

    def cache_latency(self, address, operation):
        latency = 0
        if operation == 0 or operation == 1:
            latency += self.L1_Data_Latency
            if self.cache1.check_cache(address) == False:
                latency += self.L2_Latency
                if self.cache2.check_cache(address) == False:
                    latency += self.main_merory_Latency

        elif operation == 2:
            latency += self.L1_Instr_Latency
            if self.cache_instruction.check_cache(address) == False:
                latency += self.L2_Latency
                if self.cache2.check_cache(address) == False:
                    latency += self.main_merory_Latency

        return latency

    def instruction_fetch(self, instructions):
        instructions_fetch_possible = [False] * 4

        if self.cores[0].pc == self.cores[1].pc == self.cores[2].pc == self.cores[3].pc:
            instructions_fetch_possible = [True] * 4
            if self.sync_reached[0] == True:
                for i in range(4):
                    self.sync_reached[i] = False
            self.instruction_fetch_stall = []
        else:
            if not self.instruction_fetch_stall:
                for i in range(4):
                    if self.cores[i].pc >= len(instructions):
                        continue
                    if self.sync_reached[i] == False:
                        self.instruction_fetch_stall.append(i)

            if len(self.instruction_fetch_stall) == 0:
                print("You have tried to use sync in the wrong way after a core has skipped sync it can't reach it since it can't go back in time so use it properly.")
                exit()
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
                    if opcode in ["add", "sub", "mul", "addi", "jalr", "slli", "la", "jal", "lw", "lw_spm"]:
                        rd_id = int(rd[1:])
                        self.cores[i].register_active[rd_id] -= 1
                self.cores[i].ID_EX = []
                self.fetch_ins[i] = True
                continue
            if instructions_fetch_possible[i]:
                if self.cores[i].pc >= len(instructions):
                    continue
                self.cores[i].IF_ID = instructions[self.cores[i].pc]
                if self.cores[i].IF_ID.opcode == "sync":
                    self.sync_reached[i] = True
                instruction_address = self.cores[i].pc * \
                    4 + self.instruction_address_start
                self.cache_controller(instruction_address, None, 2)
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
                    temp_data_array = [0]*(self.cache_block_size//4)
                    offset_bits = address & self.offset_mask
                    if offset_bits != 0:
                        address = address-(offset_bits)
                    for i in range(self.cache_block_size//4):
                        temp_data_array[i] = self.mem.read_word(address+i*4)
                    temp_addr, temp_data_array, temp_value_changed = self.cache1.replace_line(
                        address, temp_data_array, False)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    if (temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(
                                temp_addr+i*4, temp_data_array[i])
                else:
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.get_line_data(
                        address)
                    temp_addr, temp_data_array, temp_value_changed = self.cache1.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    if (temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(
                                temp_addr+i*4, temp_data_array[i])
            return data
        elif operation == 1:  # Store operation
            # Store in cache1 cache first
            success = self.cache1.store(address, data)

            # DONT FORGET TO UPDATE THE MEMORY AFTER END OF SIMULATION,you SHOULD DO IT
            self.mem.write_word(address, data)
            # print("success cache1",success)
            if success == False:
                # If cache1 cache miss, store in cache2 cache
                success = self.cache2.store(address, data)
                # print("success cache2",success)
                if success == False:
                    # If cache2 cache miss, store in main memory
                    self.mem.write_word(address, data)
                    # Store in cache1 cache for consistency

                    temp_data_array = [0]*(self.cache_block_size//4)
                    offset_bits = address & self.offset_mask
                    if offset_bits != 0:
                        address = address-(offset_bits)
                    for i in range(self.cache_block_size//4):
                        temp_data_array[i] = self.mem.read_word(address+i*4)
                    # print("temp data array",temp_data_array)
                    temp_addr, temp_data_array, temp_value_changed = self.cache1.replace_line(
                        address, temp_data_array, False)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    if (temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(
                                temp_addr+i*4, temp_data_array[i])
                else:
                    # If cache2 cache hit, update cache1 cache
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.get_line_data(
                        address)
                    temp_addr, temp_data_array, temp_value_changed = self.cache1.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    if (temp_value_changed):
                        for i in range(self.cache_block_size//4):
                            self.mem.write_word(
                                temp_addr+i*4, temp_data_array[i])
            # Also store in cache2 cache for consistenc

        elif operation == 2:  # Instruction fetch operation
            instr = self.cache_instruction.fetch(address)
            if instr is None:
                instr = self.cache2.fetch(address)
                if instr is None:
                    instr = self.mem.read_word(address)
                    temp_data_array = [0]*(self.cache_block_size//4)
                    offset_bits = address & self.offset_mask
                    if offset_bits != 0:
                        address = address-(offset_bits)
                    for i in range(self.cache_block_size//4):
                        temp_data_array[i] = self.mem.read_word(address+i*4)
                    temp_addr, temp_data_array, temp_value_changed = self.cache_instruction.replace_line(
                        address, temp_data_array, False)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                else:
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.get_line_data(
                        address)
                    temp_addr, temp_data_array, temp_value_changed = self.cache_instruction.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)
                    temp_addr, temp_data_array, temp_value_changed = self.cache2.replace_line(
                        temp_addr, temp_data_array, temp_value_changed)

    def print_cache_statistics(self):
        # Column titles
        self.stats = {
            "L1_Data": {
                "access": self.cache1.access,
                "misses": self.cache1.misses,
                "hits": self.cache1.access - self.cache1.misses,
                "hit_rate": round(((self.cache1.access - self.cache1.misses) / self.cache1.access) * 100, 2) if self.cache1.access > 0 else 0,
                "miss_rate": round((self.cache1.misses / self.cache1.access) * 100, 2) if self.cache1.access > 0 else 0
            },
            "L1_Instr": {
                "access": self.cache_instruction.access,
                "misses": self.cache_instruction.misses,
                "hits": self.cache_instruction.access - self.cache_instruction.misses,
                "hit_rate": round(((self.cache_instruction.access - self.cache_instruction.misses) / self.cache_instruction.access) * 100, 2) if self.cache_instruction.access > 0 else 0,
                "miss_rate": round((self.cache_instruction.misses / self.cache_instruction.access) * 100, 2) if self.cache_instruction.access > 0 else 0
            },
            "L2": {
                "access": self.cache2.access,
                "misses": self.cache2.misses,
                "hits": self.cache2.access - self.cache2.misses,
                "hit_rate": round(((self.cache2.access - self.cache2.misses) / self.cache2.access) * 100, 2) if self.cache2.access > 0 else 0,
                "miss_rate": round((self.cache2.misses / self.cache2.access) * 100, 2) if self.cache2.access > 0 else 0
            }                               
        }   
        print(f"{'Stats':<15}{'L1 Data':<15}{'L1 Instruction':<20}{'L2':<10}")
        print("-" * 60)

        # Print each row with aligned formatting
        print(f"{'Access':<15}{self.stats['L1_Data']['access']:<15}{self.stats['L1_Instr']['access']:<20}{self.stats['L2']['access']:<10}")
        print(f"{'Misses':<15}{self.stats['L1_Data']['misses']:<15}{self.stats['L1_Instr']['misses']:<20}{self.stats['L2']['misses']:<10}")
        print(f"{'Hits':<15}{self.stats['L1_Data']['hits']:<15}{self.stats['L1_Instr']['hits']:<20}{self.stats['L2']['hits']:<10}")
        print(f"{'Hit Rate (%)':<15}{self.stats['L1_Data']['hit_rate']:<15}{self.stats['L1_Instr']['hit_rate']:<20}{self.stats['L2']['hit_rate']:<10}")
        print(f"{'Miss Rate (%)':<15}{self.stats['L1_Data']['miss_rate']:<15}{self.stats['L1_Instr']['miss_rate']:<20}{self.stats['L2']['miss_rate']:<10}")


    def run_simulator(self, assembly_file: str):
        def decimal_to_hex(n: int) -> str:
            return f"0x{n:x}"

        self.get_latency()
        self.get_cache_latency()
        self.get_cache_details()
        print("\nCONSOLE\n")
        instructions, label_map, data_instructions, data_values, scratchpad_instructions, scratchpad_values = parse_assembly_file(
            assembly_file)

        for i in range(len(instructions)):
            self.mem.write_word(
                i*4 + self.instruction_address_start, instructions[i])

        scratchpad_label_map = self.excute_scratchpad_instructions(
            scratchpad_instructions,scratchpad_values, self.scratch_pad)
        
        data_label_map = self.execute_data_instruction(
            data_instructions, data_values, self.mem)
        for core in self.cores:
            core.labels_map.update(label_map)
            core.labels_map.update(data_label_map)
            core.labels_map.update(scratchpad_label_map)
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
                core.execute_instruction(self.fetch_ins, self)
            self.instruction_fetch(instructions)

            fetch_possible = True
            if all(core.pc >= len(instructions) for core in self.cores):
                fetch_possible = False

            # Check if pipeline should stop
            if not fetch_possible and all(not core.IF_ID and not core.ID_EX and not core.EX_MEM and not core.MEM_WB for core in self.cores):
                pipeline_active = False
            cycle += 1

        print("---------------------------------------------------------------------------------------------------------")
        print("\nRegisters:")
        for i, core in enumerate(self.cores):
            print(f"Core {i} registers: {core.registers}")

        print("\nMemory Dump:")

        for idx in range(0, 1024, 6):
            addresses = [
                f"{decimal_to_hex(i*4)}: {self.mem.word[i]}" for i in range(idx, min(idx + 6, 1024))]
            print("  |  ".join(addresses))

        print("\nScratch Pad")

        for idx in range(0, 100, 6):
            addresses = [
                f"{decimal_to_hex(i*4)}: {self.scratch_pad.word[i]}" for i in range(idx, min(idx + 6, 100))]
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
            
        print("\nCache Statistics:")
        self.print_cache_statistics()
