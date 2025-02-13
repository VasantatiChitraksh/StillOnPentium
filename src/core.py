
from instructions import Instruction


class Core:
    def __init__(self, core_id: int):
        self.core_id = core_id
        self.registers = [0]*32
        self.pc = 0
        self.instruction_count = 0
        self.stall_count = 0

    def execute_instruction(self, instr: Instruction, memory, label_map: dict):
        opcode = instr.opcode

        if opcode == 'add':
            rs1_val = self.get_register_value(instr.rs1)
            rs2_val = self.get_register_value(instr.rs2)

            rd = instr.rd
            self.set_register_value(rd, rs1_val+rs2_val)
        elif opcode == 'sub':
            rs1_val = self.get_register_value(instr.rs1)
            rs2_val = self.get_register_value(instr.rs2)

            rd = instr.rd
            self.set_register_value(rd, rs1_val-rs2_val)
        elif opcode == 'addi':
            rs1_val = self.get_register_value(instr.rs1)
            self.set_register_value(instr.rd, rs1_val+instr.immediate)
        elif opcode == 'bne':
            if self.get_register_value(instr.rs1) != self.get_register_value(instr.rs2):
                self.pc = label_map[instr.label]
                self.instruction_count += 1
                return
        elif opcode == 'jal':
            return_adrs = self.pc + 1
            self.set_register_value(instr.rd, return_adrs)
            pc = label_map[instr.label]
            self.instruction_count += 1
            return
        elif opcode == 'lw':
            base = self.get_register_value(instr.rs1)
            address = base + instr.immediate
            word = memory.read_word(address)
            self.set_register_value(instr.rd, word)
        elif opcode == 'sw':
            base = self.get_register_value(instr.rs1)
            address = base + instr.immediate
            value = self.get_register_value(instr.rs2)
            memory.write_word(address, value)
        else:
            raise NotImplementedError(
                f"Still haven't implement the opcode {opcode}")

        self.pc += 1
        self.instruction_count += 1

    def get_register_value(self, reg: str) -> int:
        index = int(reg[1:])
        return self.registers[index]

    def set_register_value(self, reg: str, value: int):
        index = int(reg[1:])
        if index == 0:
            return
        self.registers[index] = value
