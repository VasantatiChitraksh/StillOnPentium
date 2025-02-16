
from instructions import Instruction


class Core:
    def __init__(self, core_id: int):
        self.core_id = core_id
        self.registers = [0]*32
        self.pc = 0
        self.program = []
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
        elif opcode == 'beq':
            rs1_val = self.get_register_value(instr.rs1)
            rs2_val = self.get_register_value(instr.rs2)

            if rs1_val == rs2_val:
                # Jump to label's instruction index
                new_pc = label_map[instr.label]
                self.pc = new_pc
            else:
                self.pc += 1

            self.instruction_count += 1
            return
        elif opcode == 'bne':
            rs1_val = self.get_register_value(instr.rs1)
            rs2_val = self.get_register_value(instr.rs2)

            if rs1_val != rs2_val:
                # Jump to label's instruction index
                new_pc = label_map[instr.label]
                self.pc = new_pc
            else:
                self.pc += 1

            self.instruction_count += 1
            return
        elif opcode == 'bge':
            rs1_val = self.get_register_value(instr.rs1)
            rs2_val = self.get_register_value(instr.rs2)

            if rs1_val >= rs2_val:
                # Jump to label's instruction index
                new_pc = label_map[instr.label]
                self.pc = new_pc
            else:
                self.pc += 1

            self.instruction_count += 1
            return
        elif opcode == 'jal':
            target_label = instr.label
            if target_label not in label_map:
                raise ValueError(f"Undefined label: {target_label}")

            target_address = label_map[target_label]
            return_address = self.pc + 1
            self.set_register_value(instr.rd, return_address)

            # Jump to the label
            self.pc = target_address
            self.instruction_count += 1
            return
        elif opcode == 'lw':
            base = self.get_register_value(instr.rs1)
            address = base + instr.immediate
            word = memory.read_word(address, self.core_id)
            self.set_register_value(instr.rd, word)
        elif opcode == 'sw':
            base = self.get_register_value(instr.rs1)
            address = base + instr.immediate
            value = self.get_register_value(instr.rs2)
            memory.write_word(address, value, self.core_id)
        elif opcode == 'slli':
            rs1_val = self.get_register_value(instr.rs1)
            shift_amount = instr.immediate
            result = rs1_val << shift_amount
            self.set_register_value(instr.rd, result)
        elif opcode == 'j':
            target_label = instr.label
            if target_label not in label_map:
                raise ValueError(f"Undefined label: {target_label}")

            target_address = label_map[target_label]
            self.pc = target_address
            self.instruction_count += 1
            return
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
