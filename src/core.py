from pipeline_register import PipelineRegister
from instructions import Instruction


class Core:
    def __init__(self, core_id: int):
        self.core_id = core_id
        self.registers = [0]*32
        self.register_active = [0]*32
        self.pc = 0
        self.instruction_count = 0
        self.fetch_possible = True
        self.stall_count = 0
        self.pipeline_registers = [PipelineRegister() for _ in range(4)]
        # IF_ID = 0, ID_EX = 1, EX_MEM = 2, MEM_WB = 3
# ---------------------------------------------------INSTRUCTION DECODE AND REGISTER FETCH---------------------------------------------------#

    def instr_decode_reg_fetch(self, instr: Instruction, label_map: dict):
        if not self.pipeline_registers[0].isUsed:
            return
        self.pipeline_registers[1].isUsed = True
        self.pipeline_registers[1].pc = self.pc
        self.pipeline_registers[1].instruction = self.pipeline_registers[0].instruction
        self.pipeline_registers[1].opcode = self.pipeline_registers[0].instruction.opcode
        opcode = self.pipeline_registers[1].opcode

        if opcode in ['add', 'sub', 'mul']:
            if self.register_active[int(instr.rs1[1:])] > 0 or self.register_active[int(instr.rs2[1:])] > 0:
                self.stall_count += 1
                return
            self.register_active[int(instr.rd[1:])] += 1
            self.pipeline_registers[1].rs1 = self.get_register_value(instr.rs1)
            self.pipeline_registers[1].rs2 = self.get_register_value(instr.rs2)
            self.pipeline_registers[1].rd = instr.rd

        elif opcode == 'div':
            if self.register_active[int(instr.rs1[1:])] > 0 or self.register_active[int(instr.rs2[1:])] > 0:
                self.stall_count += 1
                return
            self.register_active[int(instr.rd[1:])] += 1
            self.pipeline_registers[1].rs1 = self.get_register_value(instr.rs1)
            self.pipeline_registers[1].rs2 = self.get_register_value(instr.rs2)
            self.pipeline_registers[1].rd = instr.rd

            if (self.pipeline_registers[1].rs2 == 0):
                raise ValueError("Division by zero")

        elif opcode in ['addi', 'slli', 'lw']:
            if self.register_active[int(instr.rs1[1:])] > 0:
                self.stall_count += 1
                return
            self.register_active[int(instr.rd[1:])] += 1
            self.pipeline_registers[1].rs1 = self.get_register_value(instr.rs1)
            self.pipeline_registers[1].immediate = instr.immediate
            self.pipeline_registers[1].rd = instr.rd

        elif opcode in ['beq', 'bne', 'bge']:
            if self.register_active[int(instr.rs1[1:])] > 0 or self.register_active[int(instr.rs2[1:])] > 0:
                self.stall_count += 1
                return
            self.pipeline_registers[1].rs1 = self.get_register_value(instr.rs1)
            self.pipeline_registers[1].rs2 = self.get_register_value(instr.rs2)
            self.pipeline_registers[1].branch_taken = False
            self.pipeline_registers[1].branch_target = instr.label

        elif opcode == 'sw':  # sw rs2, immediate(rs1)
            if self.register_active[int(instr.rs1[1:])] > 0 or self.register_active[int(instr.rs2[1:])] > 0:
                self.stall_count += 1
                return
            self.pipeline_registers[1].rs1 = self.get_register_value(instr.rs1)
            self.pipeline_registers[1].immediate = instr.immediate
            self.pipeline_registers[1].rs2 = self.get_register_value(instr.rs2)
        elif opcode == 'li':  # load immediate
            self.pipeline_registers[1].immediate = instr.immediate
            self.pipeline_registers[1].rd = instr.rd
        elif opcode == 'nop':
            pass
        elif opcode == 'la':
            self.register_active[int(instr.rd[1:])] += 1
            self.pipeline_registers[1].label = instr.label
            self.pipeline_registers[1].rd = instr.rd
        elif opcode == 'jal':  # jal rd, offset
            self.register_active[int(instr.rd[1:])] += 1
            self.pipeline_registers[1].label = instr.label
            self.pipeline_registers[1].rd = instr.rd
            self.pipeline_registers[1].jump_return_address = self.pc + 1
            target_label = instr.label
            if self.pipeline_registers[1].label not in label_map:
                raise ValueError(f"Undefined label: {target_label}")
        elif opcode == 'j':
            self.pipeline_registers[1].label = instr.label
            target_label = instr.label
            if target_label not in label_map:
                raise ValueError(f"Undefined label: {target_label}")
        else:
            raise NotImplementedError(
                f"Still haven't implement the opcode {opcode}")

        self.fetch_possible = True
        self.pipeline_registers[0] = PipelineRegister()
# ---------------------------------------------------EXECUTE---------------------------------------------------#

    def execute(self, instr: Instruction, memory, label_map: dict):
        if not self.pipeline_registers[1].isUsed:
            return
        self.pipeline_registers[2].isUsed = True
        self.pipeline_registers[2].pc = self.pipeline_registers[1].pc
        self.pipeline_registers[2].instruction = self.pipeline_registers[1].instruction
        self.pipeline_registers[2].opcode = self.pipeline_registers[1].instruction.opcode
        opcode = self.pipeline_registers[2].opcode
        if opcode == 'add':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 + \
                self.pipeline_registers[2].rs2

        elif opcode == 'sub':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 - \
                self.pipeline_registers[2].rs2

        elif opcode == 'mul':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 * \
                self.pipeline_registers[2].rs2

        elif opcode == 'div':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 // self.pipeline_registers[2].rs2

        elif opcode == 'addi':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].immediate = self.pipeline_registers[1].immediate
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 + \
                self.pipeline_registers[2].immediate

        elif opcode == 'slli':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].immediate = self.pipeline_registers[1].immediate
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 << self.pipeline_registers[2].immediate

        elif opcode == 'beq':
            # self.pipeline_registers[2].rs1 = self.get_register_value(self.pipeline_registers[1].instruction.rs1)
            # self.pipeline_registers[2].rs2 = self.get_register_value(self.pipeline_registers[1].instruction.rs2)
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            if self.core_id == 0:
                print("Check in ex beq",self.pipeline_registers[2].rs1, self.pipeline_registers[2].rs2)
            self.pipeline_registers[2].branch_target = self.pipeline_registers[1].branch_target
            self.pipeline_registers[2].branch_taken = (self.pipeline_registers[2].rs1 == self.pipeline_registers[2].rs2)
            if self.pipeline_registers[2].branch_taken:
                self.pipeline_registers[2].pc = label_map[instr.label]

        elif opcode == 'bne':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].branch_target = self.pipeline_registers[1].branch_target
            self.pipeline_registers[2].branch_taken = self.pipeline_registers[2].rs1 != self.pipeline_registers[2].rs2
            if self.pipeline_registers[2].branch_taken:
                self.pipeline_registers[2].pc = label_map[instr.label]

        elif opcode == 'bge':
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].branch_target = self.pipeline_registers[1].branch_target
            self.pipeline_registers[2].branch_taken = self.pipeline_registers[2].rs1 >= self.pipeline_registers[2].rs2
            if self.pipeline_registers[2].branch_taken:
                self.pipeline_registers[2].pc = label_map[instr.label]

        elif opcode == 'lw':  # lw rd, immediate(rs1)
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].immediate = self.pipeline_registers[1].immediate
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 + \
                self.pipeline_registers[2].immediate

        elif opcode == 'sw':  # sw rs2, immediate(rs1)
            self.pipeline_registers[2].rs1 = self.pipeline_registers[1].rs1
            self.pipeline_registers[2].immediate = self.pipeline_registers[1].immediate
            self.pipeline_registers[2].rs2 = self.pipeline_registers[1].rs2
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].rs1 + \
                self.pipeline_registers[2].immediate

        elif opcode == 'li':  # load rd, immediate
            self.pipeline_registers[2].immediate = self.pipeline_registers[1].immediate
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[2].immediate

        elif opcode == 'nop':
            pass

        elif opcode == 'la':
            self.pipeline_registers[2].label = self.pipeline_registers[1].label
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = label_map[self.pipeline_registers[2].label]

        elif opcode == 'jal':  # jal rd, offset
            self.pipeline_registers[2].label = self.pipeline_registers[1].label
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].jump_return_address = self.pipeline_registers[1].jump_return_address
            self.pipeline_registers[2].branch_taken = True
            self.pipeline_registers[2].pc = label_map[self.pipeline_registers[2].label]

        elif opcode == 'jalr':  # jalr rd, immediate(rs1)
            self.pipeline_registers[2].label = self.pipeline_registers[1].label
            self.pipeline_registers[2].rd = self.pipeline_registers[1].rd
            self.pipeline_registers[2].execute_result = self.pipeline_registers[1].rs1 + \
                self.pipeline_registers[1].immediate
            self.pipeline_registers[2].branch_taken = True
            self.pipeline_registers[2].pc = self.pipeline_registers[2].execute_result

        elif opcode == 'j':
            self.pipeline_registers[2].label = self.pipeline_registers[1].label
            self.pipeline_registers[2].pc = label_map[self.pipeline_registers[2].label]
            self.pipeline_registers[2].branch_taken = True
        
        self.pipeline_registers[1] = PipelineRegister()
 # ---------------------------------------------------MEMORY ACCESS---------------------------------------------------#

    def memory_access(self, memory):
        if not self.pipeline_registers[2].isUsed:
            return
        self.pipeline_registers[3].isUsed = True
        self.pipeline_registers[3].pc = self.pipeline_registers[2].pc
        self.pipeline_registers[3].instruction = self.pipeline_registers[2].instruction
        self.pipeline_registers[3].opcode = self.pipeline_registers[2].opcode
        opcode = self.pipeline_registers[3].opcode
        if opcode in ['add', 'sub', 'mul', 'div']:
            self.pipeline_registers[3].rd = self.pipeline_registers[2].rd
            self.pipeline_registers[3].execute_result = self.pipeline_registers[2].execute_result
        if opcode in ['addi', 'slli']:
            self.pipeline_registers[3].rd = self.pipeline_registers[2].rd
            self.pipeline_registers[3].execute_result = self.pipeline_registers[2].execute_result
        if opcode in ['beq', 'bne', 'bge']:
            pass
        if opcode in ['lw', 'li']:
            self.pipeline_registers[3].rd = self.pipeline_registers[2].rd
            self.pipeline_registers[3].mem_result = memory.read_word(
                self.pipeline_registers[2].execute_result, self.core_id)
        if opcode == 'sw':
            self.pipeline_registers[3].rs2 = self.pipeline_registers[2].rs2
            self.pipeline_registers[3].mem_result = memory.write_word(
                self.pipeline_registers[2].execute_result, self.pipeline_registers[2].rs2, self.core_id)
        if opcode == 'nop':
            pass
        if opcode == 'la':
            self.pipeline_registers[3].rd = self.pipeline_registers[2].rd
            self.pipeline_registers[3].execute_result = self.pipeline_registers[2].execute_result
        if opcode in ['jal', 'jalr']:
            self.pipeline_registers[3].rd = self.pipeline_registers[2].rd
            self.pipeline_registers[3].jump_return_address = self.pipeline_registers[2].jump_return_address

        self.pipeline_registers[2] = PipelineRegister()
# ---------------------------------------------------WRITE BACK---------------------------------------------------#

    def write_back(self):
        if not self.pipeline_registers[3].isUsed:
            return
        opcode = self.pipeline_registers[3].opcode
        # beq,bne,bge,sw,nop,j do not need write back
        if opcode in ['add', 'sub', 'mul', 'div']:
            self.register_active[int(self.pipeline_registers[3].rd[1:])] -= 1
            self.set_register_value(
                self.pipeline_registers[3].rd, self.pipeline_registers[3].execute_result)
        elif opcode in ['addi', 'slli']:
            self.register_active[int(self.pipeline_registers[3].rd[1:])] -= 1
            self.set_register_value(
                self.pipeline_registers[3].rd, self.pipeline_registers[3].execute_result)
        elif opcode in ['lw', 'li']:
            self.register_active[int(self.pipeline_registers[3].rd[1:])] -= 1
            self.set_register_value(
                self.pipeline_registers[3].rd, self.pipeline_registers[3].mem_result)
        elif opcode == 'la':
            self.register_active[int(self.pipeline_registers[3].rd[1:])] -= 1
            self.set_register_value(
                self.pipeline_registers[3].rd, self.pipeline_registers[3].execute_result)
        elif opcode in ['jal']:
            self.register_active[int(self.pipeline_registers[3].rd[1:])] -= 1
            self.set_register_value(
                self.pipeline_registers[3].rd, self.pipeline_registers[3].jump_return_address)

        self.pipeline_registers[3] = PipelineRegister()
# ---------------------------------------------------EXECUTE INSTRUCTION------------------------------------------------

    def execute_instruction(self, instr: Instruction, memory, label_map: dict):
        if self.core_id == 0:
            print("Executing wb")
        self.write_back()
        if self.core_id == 0:
            print("Executing mem")
        self.memory_access(memory)
        if self.core_id == 0:
            print("Executing exe")
        self.execute(instr,memory, label_map)
        if self.core_id == 0:
            print("Executing decode")
        self.instr_decode_reg_fetch(instr, label_map)
        self.instruction_count += 1

    def get_register_value(self, reg: str) -> int:
        index = int(reg[1:])
        return self.registers[index]

    def set_register_value(self, reg: str, value: int):
        index = int(reg[1:])
        if index == 0:
            return
        self.registers[index] = value
