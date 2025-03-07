from data_instructions import DataInstruction
from pipeline_register import PipelineRegister
from instructions import Instruction
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


def instruction_fetch(instructions: any, Cores: any, core_id: int, pc: int):
    if(pc) >= len(instructions):
        return
    instr = instructions[pc]
    # if core_id == 0:
    #     print(pc,instr)
    Cores[core_id].pipeline_registers[0].instruction = instr
    Cores[core_id].pipeline_registers[0].isUsed = True
    if Cores[core_id].pipeline_registers[2].branch_taken:
        Cores[core_id].pc = Cores[core_id].pipeline_registers[2].pc
        Cores[core_id].pipeline_registers[0] = PipelineRegister()
        Cores[core_id].pipeline_registers[1] = PipelineRegister()
        
    else:
        Cores[core_id].pc +=1