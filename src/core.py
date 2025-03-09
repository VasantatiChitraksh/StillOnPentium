from instructions import Instruction
from memory import Memory
import simulator


class Core:
    def __init__(self, core_id: int):
        self.core_id = core_id
        self.registers = [0] * 33 #33 register is the special register which has core_id
        self.registers[32] = self.core_id
        self.register_active = [0] * 33
        self.pc = 0
        self.instruction_count = 0
        self.stall_count = 0
        self.IF_ID = None
        self.ID_EX = []
        self.EX_MEM = []
        self.MEM_WB = []
        self.labels_map = {}  # Added to store label mappings
        self.execution_time_remaining = 0
        self.execute_prev_done = True
        self.memory_remaining_time = 0
        self.mem_done = True
        self.isDF = False
        self.latency_map = {}

    def get_data_from_EX_MEM(self, rd) -> any:
        if not self.EX_MEM:
            return "False"
        if len(self.EX_MEM) == 1:
            return "False"
        if rd == self.EX_MEM[1] and self.EX_MEM[0] not in ["lw", "la"]:
            return self.EX_MEM[2]
        elif rd == self.EX_MEM[1] and self.EX_MEM[0] in ["lw", "la"]:
            return "False"
        return "False"

    def get_data_from_MEM_WB(self, rd) -> any:
        if not self.MEM_WB:
            return "False"
        if rd == self.MEM_WB[1]:
            return self.MEM_WB[2]
        return "False"

    def get_forwarded_data(self, rd)->any:
        if not self.isDF:
            return "False"
        data_from_EX_MEM = self.get_data_from_EX_MEM(rd)
        if data_from_EX_MEM == "False":
            return "False"
        elif data_from_EX_MEM == "False":
            data_from_MEM_WB = self.get_data_from_MEM_WB(rd)
            if data_from_MEM_WB == "False":
                return "False"
            else:
                return data_from_MEM_WB
        else:
            return data_from_EX_MEM
    
    def instr_decode_reg_fetch(self, instr: Instruction, fetch_ins):
        if self.execute_prev_done == False:
            return
        if not self.IF_ID:
            return
        # print("Decoding:", instr)
        opcode = instr.opcode
        decoded_ready = []
        decoded_ready.append(opcode)

        if opcode in ["add", "sub", "mul"]:
            decoded_ready.append(instr.rd)
            rd_id = int(instr.rd[1:])
            rs1_id = int(instr.rs1[1:])
            rs2_id = int(instr.rs2[1:])
            # print("RS1 ID:Value --- RS2 ID:Value",rs1_id,self.register_active[rs1_id],rs2_id,self.register_active[rs2_id])
            if self.register_active[rs1_id] > 0 or self.register_active[rs2_id] > 0:
                if self.register_active[rs1_id] > 0 and self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs1 and rs2",instr.rs1,instr.rs2)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs1_fwd_data == "False" or rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
                        decoded_ready.append(rs2_fwd_data)

                elif self.register_active[rs1_id] > 0:
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    if rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
                        decoded_ready.append(self.get_register_value(instr.rs2))
                    
                elif self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs2",instr.rs2)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(self.get_register_value(instr.rs1))
                        decoded_ready.append(rs2_fwd_data)
            else:
                decoded_ready.append(self.get_register_value(instr.rs1))
                decoded_ready.append(self.get_register_value(instr.rs2))
            self.register_active[rd_id] += 1

        elif opcode in ["addi", "jalr", "slli"]:
            decoded_ready.append(instr.rd)
            rd_id = int(instr.rd[1:])
            rs1_id = int(instr.rs1[1:])
            if self.register_active[rs1_id] > 0:
                if self.register_active[rs1_id] > 0:
                    # print("Stalling due to rs1",instr.rs1)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    if rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    elif rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
                        decoded_ready.append(instr.immediate)
            else:
                decoded_ready.append(self.get_register_value(instr.rs1))
                decoded_ready.append(instr.immediate)
            self.register_active[rd_id] += 1
            # print("ID:Value",instr.rd,self.get_register_value(instr.rd))

        elif opcode == "lw":
            rd_id = int(instr.rd[1:])
            decoded_ready.append(instr.rd)
            # print("Decoded Offset (instr_decode_reg_fetch):", instr.immediate)
            decoded_ready.append(int(instr.immediate))
            rs1_id = int(instr.rs1[1:])
            if self.register_active[rs1_id] > 0:
                if self.register_active[rs1_id] > 0:
                    # print("Stalling due to rs1",instr.rs1)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    if rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    elif rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
            else:
                decoded_ready.append(self.get_register_value(instr.rs1))
            self.register_active[rd_id] += 1
            # print(self.get_register_value(instr.rs1))

        elif opcode == "sw":
            rs1_id = int(instr.rs1[1:])
            rs2_id = int(instr.rs2[1:])
            if self.register_active[rs1_id] > 0 or self.register_active[rs2_id] > 0:
                if self.register_active[rs1_id] > 0 and self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs1 and rs2",instr.rs1,instr.rs2)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs1_fwd_data == "False" or rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs2_fwd_data)
                        decoded_ready.append(instr.immediate)
                        decoded_ready.append(rs1_fwd_data)
                elif self.register_active[rs1_id] > 0:
                    # print("Stalling due to rs1",instr.rs1)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    if rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(self.get_register_value(instr.rs2))
                        decoded_ready.append(instr.immediate)
                        decoded_ready.append(rs1_fwd_data)
                elif self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs2",instr.rs2)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs2_fwd_data)
                        decoded_ready.append(instr.immediate)
                        decoded_ready.append(self.get_register_value(instr.rs1))
            # For sw, store the source value, then immediate, then base register value:
            else:
                src_val = self.get_register_value(instr.rs2)
                imm_val = int(instr.immediate)
                base_val = self.get_register_value(
                    instr.rs1)  # Capture the base now
                decoded_ready.append(src_val)
                decoded_ready.append(imm_val)
                decoded_ready.append(base_val)
            # print("Decoded Offset (instr_decode_reg_fetch):", int(instr.immediate))
            # print("After decoding sent to ex stage", decoded_ready)

        elif opcode in ["bne", "bge", "beq"]:
            rs2_id = int(instr.rs2[1:])
            if instr.rs1 == "cid":
                rs1_id = rs2_id
            else:
                rs1_id = int(instr.rs1[1:])
            if self.register_active[rs1_id] > 0 or self.register_active[rs2_id] > 0:
                if self.register_active[rs1_id] > 0 and self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs1 and rs2",instr.rs1,instr.rs2)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs1_fwd_data == "False" or rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
                        decoded_ready.append(rs2_fwd_data)
                        decoded_ready.append(instr.label)
                elif self.register_active[rs1_id] > 0:
                    # print("Stalling due to rs1",instr.rs1)
                    rs1_fwd_data = self.get_forwarded_data(instr.rs1)
                    if rs1_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(rs1_fwd_data)
                        decoded_ready.append(self.get_register_value(instr.rs2))
                        decoded_ready.append(instr.label)
                elif self.register_active[rs2_id] > 0:
                    # print("Stalling due to rs2",instr.rs2)
                    rs2_fwd_data = self.get_forwarded_data(instr.rs2)
                    if rs2_fwd_data == "False":
                        self.stall_count += 1
                        return
                    else:
                        decoded_ready.append(self.get_register_value(instr.rs1))
                        decoded_ready.append(rs2_fwd_data)
                        decoded_ready.append(instr.label)
            else:
                decoded_ready.append(self.get_register_value(instr.rs1))
                decoded_ready.append(self.get_register_value(instr.rs2))
                decoded_ready.append(instr.label)

        elif opcode in ["la", "jal"]:
            rd_id = int(instr.rd[1:])
            decoded_ready.append(instr.rd)
            decoded_ready.append(instr.label)
            self.register_active[rd_id] += 1

        elif opcode == "j":
            decoded_ready.append(instr.label)

        self.ID_EX = decoded_ready
        if self.ID_EX[0] in ["lw", "sw", "la"]:
            self.execution_time_remaining = 0
        elif self.ID_EX[0] in self.latency_map:
            self.execution_time_remaining = self.latency_map[self.ID_EX[0]]-1
        else:
            self.execution_time_remaining = 0
        self.execute_prev_done = False
        # # print("making if true",id(simulator.Simulator.fetch_ins),simulator.Simulator.fetch_ins)
        simulator.Simulator.fetch_ins[self.core_id] = True
        # # print(" after making if true",id(fetch_ins),fetch_ins)
        self.IF_ID = None

    def execute(self):
        EX_Stage = self.ID_EX
        if not EX_Stage:
            return

        if not self.mem_done:
            return

        if self.execution_time_remaining > 0:
            self.execution_time_remaining -= 1
            return

        opcode = EX_Stage[0]
        # print("EX:", EX_Stage)
        execute_ready = []
        execute_ready.append(opcode)

        if opcode in ["add", "sub", "mul"]:
            execute_ready.append(EX_Stage[1])
            out = 0
            if opcode == "add":
                out = int(EX_Stage[2]) + int(EX_Stage[3])
            elif opcode == "sub":
                out = int(EX_Stage[2]) - int(EX_Stage[3])
            elif opcode == "mul":
                out = int(EX_Stage[2]) * int(EX_Stage[3])
            execute_ready.append(out)

        elif opcode in ["addi", "jalr", "slli"]:
            execute_ready.append(EX_Stage[1])
            if opcode == "addi":
                out = int(EX_Stage[2]) + int(EX_Stage[3])
            elif opcode == "slli":
                out = int(EX_Stage[2]) << int(EX_Stage[3])
            elif opcode == "jalr":
                offset = int(EX_Stage[3])
                if offset % 4 != 0:
                    # print("Offset should be a multiple of 4")
                    exit()
                new_pc = int(EX_Stage[2]) + offset
                simulator.Simulator.new_pc[self.core_id] = new_pc
                simulator.Simulator.pc_changed[self.core_id] = True
                out = self.pc + 4
            execute_ready.append(out)

        elif opcode in ["lw", "sw"]:
            offset = int(EX_Stage[2])
            # print("Offset Before Execution:", offset)
            if offset % 4 != 0:
                # print(offset)
                # print("Offset should be a multiple of 4")
                exit()
            effective_addr = int(EX_Stage[3]) + offset
            execute_ready.append(EX_Stage[1])
            execute_ready.append(effective_addr)

        elif opcode in ["bne", "bge", "beq"]:
            label = EX_Stage[3]
            if (opcode == "bne" and int(EX_Stage[1]) != int(EX_Stage[2])) or \
               (opcode == "bge" and int(EX_Stage[1]) >= int(EX_Stage[2])) or \
               (opcode == "beq" and int(EX_Stage[1]) == int(EX_Stage[2])):
                new_pc = self.labels_map[label]
                simulator.Simulator.new_pc[self.core_id] = new_pc
                simulator.Simulator.pc_changed[self.core_id] = True

        elif opcode in ["la", "jal"]:
            label = EX_Stage[2]
            if opcode == "la":
                label_value = self.labels_map[label]
                destination_addr = label_value
                execute_ready.append(EX_Stage[1])
                execute_ready.append(destination_addr)
            elif opcode == "jal":
                new_pc = self.labels_map[label]
                simulator.Simulator.new_pc[self.core_id] = new_pc
                simulator.Simulator.pc_changed[self.core_id] = True
                out = self.pc + 1
                execute_ready.append(EX_Stage[1])
                execute_ready.append(out)

        elif opcode == "j":
            label = EX_Stage[1]
            new_pc = self.labels_map[label]
            simulator.Simulator.new_pc[self.core_id] = new_pc
            simulator.Simulator.pc_changed[self.core_id] = True

        self.ID_EX = []
        self.execute_prev_done = True
        self.mem_done = False
        if opcode in ["lw", "sw", "la"] and opcode in self.latency_map:
            self.memory_remaining_time = self.latency_map[opcode]-1
        else:
            self.memory_remaining_time = 0
        self.EX_MEM = execute_ready

    def memory_access(self, memory):
        MEM_Stage = self.EX_MEM
        if not MEM_Stage:
            return

        if self.memory_remaining_time > 0:
            self.memory_remaining_time -= 1
            return
        opcode = MEM_Stage[0]
        # print("MEM:", MEM_Stage)
        memory_ready = []
        memory_ready.append(opcode)

        if opcode == "lw":
            effective_addr = int(MEM_Stage[2])
            memory_value = memory.read_word(effective_addr)
            memory_ready.append(MEM_Stage[1])
            memory_ready.append(memory_value)
            self.MEM_WB = memory_ready
        elif opcode == "sw":
            effective_addr = int(MEM_Stage[2])
            value = int(MEM_Stage[1])
            memory.write_word(effective_addr, value)
            self.MEM_WB = memory_ready
        else:
            self.MEM_WB = MEM_Stage
        self.EX_MEM = []
        self.mem_done = True
        return

    def write_back(self):
        WB_Stage = self.MEM_WB
        if not WB_Stage:
            return

        opcode = WB_Stage[0]
        # print("WB:", WB_Stage)

        if opcode in ["add", "sub", "mul", "addi", "jalr", "slli", "lw", "la", "jal"]:
            value = int(WB_Stage[2])
            reg_id = int(WB_Stage[1][1:])
            # print(reg_id)
            self.set_register_value(WB_Stage[1], value)
            self.register_active[reg_id] -= 1
        
        self.instruction_count += 1
        self.MEM_WB = []

    def execute_instruction(self, memory, fetch_ins):
        # print("---new_cycle--- core id:",self.core_id)
        self.write_back()
        self.memory_access(memory)
        self.execute()
        if self.IF_ID is not None:
            self.instr_decode_reg_fetch(self.IF_ID, fetch_ins)

    def get_register_value(self, reg: str) -> int:
        index = int(reg[1:])
        return self.registers[index]

    def set_register_value(self, reg: str, value: int):
        index = int(reg[1:])
        if index == 0:
            return
        self.registers[index] = value
