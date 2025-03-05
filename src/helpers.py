from data_instructions import DataInstruction
from memory import Memory


def execute_data_instruction(data_instructions: DataInstruction, data_values: int, memory) -> map:
    label_map = {}
    address = 1024 - data_values*4
    for data_instr in data_instructions:
        if data_instr.label:
            label_map[data_instr.label] = address
        for value in data_instr.values:
            memory.write_data_to_memory(address, value)
            address += 4
    return label_map
