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
        self.cache1 = Cache()  # L1 data cache
        self.cache_instruction = Cache()  # L1 instruction cache
        self.cache2 = Cache()  # L2 unified cache
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

    def load_instruction_to_L1(self, pc, instructions):
        block_address = (pc // (self.cache_instruction.block_size // 4)
                         ) * self.cache_instruction.block_size
        block_data = []
        for offset in range(0, self.cache_instruction.block_size, 4):
            addr = block_address + offset
            index = addr // 4
            if index < len(instructions):
                block_data.append(instructions[index])
            else:
                block_data.append(0)  # default NOP or 0

        # Check if we need to evict a block from the instruction cache 
        tag, index, _ = self.cache_instruction._parse_address(block_address)
        cache_set = self.cache_instruction.sets[index]

        # Find if we have an empty line
        empty_line = None
        for line in cache_set.lines:
            if line.tag is None:
                empty_line = line
                break

        if empty_line is not None:
            # print("Found empty line in instruction cache")
            # We have an empty line, just use it
            empty_line.tag = tag
            empty_line.block = block_data.copy()
            # Update LRU - move to end as most recently used
            cache_set.lru.remove(empty_line)
            cache_set.lru.append(empty_line)
        else:
            # print("No empty line found, need to evict a block")
            # Check if we have a line with the same tag (hit)
            # Need to evict - get the victim
            victim = cache_set.lru[0]  # The least recently used line
            if victim.tag is not None:
                # Calculate the original address of the victim line
                victim_block_address = victim.tag * \
                    (self.cache_instruction.block_size * self.cache_instruction.num_sets) + \
                    index * self.cache_instruction.block_size
                # Save the victim's data before replacing
                victim_data = victim.block.copy()
                # Replace the cache line
                victim.tag = tag
                victim.block = block_data.copy()
                # Update LRU
                cache_set.lru.remove(victim)
                cache_set.lru.append(victim)
                # Move evicted instruction data to cache2
                # print(f"Evicting instruction block from addr {victim_block_address} to L2 cache")
                self.Cache1TOCache2(
                    victim_block_address, victim_data, self.cache_instruction, self.cache2)
                # print(f"Evicted instruction block from addr {victim_block_address} to L2 cache")
            else:
                # Replace the cache line (shouldn't happen if we've checked properly)
                # print("Hey")
                self.cache_instruction.replaceCacheLine(
                    block_address, block_data)

    def instruction_fetch(self, instructions):
        instructions_fetch_possible = [False] * 4

        if self.cores[0].pc == self.cores[1].pc == self.cores[2].pc == self.cores[3].pc:
            instructions_fetch_possible = [True] * 4
            self.instruction_fetch_stall = []
        else:
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
                effective_address = self.cores[i].pc*4

                found, instruction = self.cache_instruction.findCache(
                    effective_address)
                if not found:
                    # print(f"Instruction cache miss at address {effective_address}")
                    # Try L2
                    found, instruction = self.cache2.findCache(
                        effective_address)
                    if found:
                        # print(f"L2 cache hit for instruction at address {effective_address}")
                        self.Cache2TOCache1(
                            effective_address, self.cache_instruction, self.cache2)
                        found, instruction = self.cache_instruction.findCache(
                            effective_address)
                    else:
                        # print(f"L2 cache miss for instruction at address {effective_address}")
                        # Fetch from main instruction memory
                        index = self.cores[i].pc
                        if index < len(instructions):
                            instruction = instructions[index]
                        else:
                            instruction = 0  # or NOP
                        self.load_instruction_to_L1(index, instructions)

                        # Now fetch again from L1
                        found, instruction = self.cache_instruction.findCache(
                            effective_address)
                else:
                    pass
                    # print(f"Instruction cache hit at address {effective_address}")

                self.cores[i].IF_ID = instruction
                self.cores[i].pc += 1
            if self.cores[i].pc >= len(instructions):
                continue

    def write_data(self, effective_address: int, value: int):
        if effective_address % 4 != 0 or effective_address < 0 or effective_address >= self.mem.size:
            raise ValueError(
                f"Invalid address to write: {effective_address*4} max is 4095 (4KB memory)"
            )

        # print(f"\nWriting value {value} to address {effective_address}")

        # First, check if the data is in the instruction cache
        # This is needed to maintain coherence between instruction and data cache
        found_instr, _ = self.cache_instruction.findCache(effective_address)
        if found_instr:
            # print("  Address found in instruction cache, updating it too")
            self.cache_instruction.update_word(effective_address, value)

        # Then check regular data path
        found1, _ = self.cache1.findCache(effective_address)
        if found1:
            # print("  Write hit in L1 data cache")
            self.cache1.update_word(effective_address, value)
            # Write through to memory
            self.mem.write_word(effective_address, value)
            return

        found2, _ = self.cache2.findCache(effective_address)
        if found2:
            # print("  Write hit in L2 cache (moving block to L1 first)")
            self.Cache2TOCache1(effective_address, self.cache1, self.cache2)
            self.cache1.update_word(effective_address, value)
            # Write through to memory
            self.mem.write_word(effective_address, value)
            return

        # print("  Write miss in both caches, loading block from memory first")
        self.MM2Cache1(effective_address, self.cache1)
        self.cache1.update_word(effective_address, value)
        # Write through to memory
        self.mem.write_word(effective_address, value)

    def fetch_memory_value(self, effective_address: int) -> int:
        if effective_address % 4 != 0 or effective_address < 0 or effective_address >= self.mem.size:
            raise ValueError(
                f"Invalid address requested : {effective_address*4} max is 4095 4Kb")

        # print(f"\nFetching value from address {effective_address}")

        # Also check instruction cache - data might have been stored there first
        found_instr, instr_value = self.cache_instruction.findCache(
            effective_address)
        if found_instr:
            # print("  Cache hit in instruction cache")
            # We should maintain coherence by keeping this value in data cache too
            if not self.cache1.findCache(effective_address)[0]:
                print(" Updating data cache with value from instruction cache")

    def MM2Cache1(self, effective_address: int, target_cache=None):
        if target_cache is None:
            target_cache = self.cache1
        
        is_instruction = (target_cache == self.cache_instruction)
        cache_type = "instruction" if is_instruction else "data"
            
        # Calculate the start address of the block
        block_address = effective_address // target_cache.block_size * target_cache.block_size
        # print(f"MM2Cache1 loading {cache_type} from memory at address {effective_address}")

        # Get the block data from memory
        block_data = [self.mem.read_word(
            block_address + i * 4) for i in range(target_cache.block_size // 4)]

        # Get the tag and index for the new block
        tag, index, _ = target_cache._parse_address(block_address)
        cache_set = target_cache.sets[index]

        # Check if there's a line with None tag (empty line)
        empty_line = None
        for line in cache_set.lines:
            if line.tag is None:
                empty_line = line
                break

        # If there's an empty line, use it
        if empty_line is not None:
            # print(f"Found empty line in {cache_type} cache")
            empty_line.tag = tag
            empty_line.block = block_data.copy()
            # Update LRU - move to end as most recently used
            cache_set.lru.remove(empty_line)
            cache_set.lru.append(empty_line)
        else:
            # Need to evict - get the victim
            victim = cache_set.lru[0]  # The least recently used line
            if victim.tag is not None:
                # Calculate the original address of the victim line
                victim_block_address = victim.tag * \
                    (target_cache.block_size * target_cache.num_sets) + \
                    index * target_cache.block_size
                # Save the victim's data before replacing
                victim_data = victim.block.copy()
                # print(f"Evicting {cache_type} block from address {victim_block_address} to L2")
                # Replace the cache line
                victim.tag = tag
                victim.block = block_data.copy()
                # Update LRU
                cache_set.lru.remove(victim)
                cache_set.lru.append(victim)
                # Move evicted data to cache2
                self.Cache1TOCache2(victim_block_address, victim_data, target_cache, self.cache2)
            else:
                # Replace the cache line (shouldn't happen if we've checked properly)
                target_cache.replaceCacheLine(block_address, block_data)

    def Cache1TOCache2(self, block_address: int, block_data, source_cache, target_cache):
        is_instruction = (source_cache == self.cache_instruction)
        cache_type = "instruction" if is_instruction else "data"
        # print(f"Moving {cache_type} from L1 to L2 cache for block at address {block_address}")
        
        # Move each word from the evicted block to cache2
        for i in range(len(block_data)):
            word_address = block_address + i * 4
            # Create a single-element list for each word to match cache2's block structure
            # We need to construct a proper block for cache2
            word_value = block_data[i]

            # Calculate the word's position in its block
            word_offset = (word_address % target_cache.block_size) // 4

            # Calculate the block address for this word
            word_block_address = word_address - word_offset * 4

            # Get the block from cache2 if it exists
            tag, index, _ = target_cache._parse_address(word_block_address)
            cache_set = target_cache.sets[index]

            existing_line = None
            for line in cache_set.lines:
                if line.tag == tag:
                    existing_line = line
                    break

            if existing_line is not None:
                # Update existing block
                # print(f"  Updating existing block in L2 cache at offset {word_offset}")
                existing_line.block[word_offset] = word_value
                # Update LRU status for the existing line
                cache_set.lru.remove(existing_line)
                cache_set.lru.append(existing_line)  # Move to MRU position
            else:
                # Create new block
                # print(f"  Creating new block in L2 cache")
                new_block = [0] * (target_cache.block_size // 4)
                new_block[word_offset] = word_value

                # Store to cache2
                target_cache.replaceCacheLine(word_block_address, new_block)

    # Exclusive
    def Cache2TOCache1(self, effective_address: int, target_cache, source_cache):
        is_instruction = (target_cache == self.cache_instruction)
        cache_type = "instruction" if is_instruction else "data"
        # print(f"Moving {cache_type} from L2 to L1 cache for address {effective_address}")
        
        # Calculate the start address of the block for cache1
        block_address = effective_address // target_cache.block_size * target_cache.block_size

        # Prepare the block data for cache1
        block_data = []

        # Keep track of cache2 lines that need to be invalidated
        cache2_lines_to_invalidate = []

        for i in range(target_cache.block_size // 4):
            word_address = block_address + i * 4
            found, value = source_cache.findCache(word_address)
            if found:
                block_data.append(value)
                # Store the address to invalidate it later in cache2
                tag, index, _ = source_cache._parse_address(word_address)
                cache2_lines_to_invalidate.append((tag, index))
            else:
                # If any part is missing from cache2, read from memory
                # print(f"  Word at address {word_address} not found in L2, reading from memory")
                block_data.append(self.mem.read_word(word_address))

        # Get tag and index for the target set in cache1
        tag, index, _ = target_cache._parse_address(block_address)
        cache_set = target_cache.sets[index]

        # Find the LRU line to replace
        victim = cache_set.lru[0]  # Get the LRU line
        cache_set.lru.remove(victim)  # Remove from LRU order

        # If the victim has valid data, move it to cache2 before overwriting
        if victim.tag is not None:
            victim_block_address = victim.tag * \
                (target_cache.block_size * target_cache.num_sets) + \
                index * target_cache.block_size
            # print(f"  Evicting {cache_type} from L1 at address {victim_block_address} before replacement")
            self.Cache1TOCache2(victim_block_address, victim.block.copy(), target_cache, source_cache)

        # Update the victim line with the new data
        victim.tag = tag
        victim.block = block_data.copy()

        # Move the updated line to the MRU position
        cache_set.lru.append(victim)

        # Now invalidate the lines in cache2 that were moved to cache1
        for tag, index in cache2_lines_to_invalidate:
            cache_set = source_cache.sets[index]
            for line in cache_set.lines:
                if line.tag == tag:
                    # Invalidate this line
                    # print(f"  Invalidating line in L2 cache with tag {tag}, index {index}")
                    line.tag = None
                    line.block = [0] * (source_cache.block_size // 4)
                    # Optionally update LRU status
                    if line in cache_set.lru:
                        cache_set.lru.remove(line)
                        cache_set.lru.appendleft(line)  # Move to LRU position
                    break

    def print_cache(self):
        print("Cache 1 (Data):")
        for i, cache_set in enumerate(self.cache1.sets):
            print(f"Set {i}:")
            for line in cache_set.lines:
                print(f"  Tag: {line.tag}, Block: {line.block}")

        print("\nCache Instruction:")
        for i, cache_set in enumerate(self.cache_instruction.sets):
            print(f"Set {i}:")
            for line in cache_set.lines:
                print(f"  Tag: {line.tag}, Block: {line.block}")

        print("\nCache 2 (L2):")
        for i, cache_set in enumerate(self.cache2.sets):
            print(f"Set {i}:")
            for line in cache_set.lines:
                print(f"  Tag: {line.tag}, Block: {line.block}")

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
            # self.print_cache()

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

        # print simulation Statistics
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