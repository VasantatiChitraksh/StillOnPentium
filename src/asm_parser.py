from instructions import Instruction
from data_instructions import DataInstruction
from scratchpad_instructions import ScratchInstruction

def clean_line(line: str) -> str:
    comment_index = line.find('#')
    if comment_index != -1:
        line = line[0:comment_index]
    return line.strip()


def is_label(line: str) -> bool:
    if (line.find(':') == -1):
        return False
    return True  # Finds if Label has : in it

def extract_label(line: str) -> str:
    line = line.strip()
    cindex = line.find(':')  # Finds the : index from the label
    if (line[cindex+1:] != ""):
        return line[0:cindex], line[cindex+1:]
    return line[0:cindex], ""


def extract_label_with_address(line: str) -> str:
    line = line.strip()
    cindex = line.find(':')  # Finds the : index from the label
    if (line[cindex+1:] != ""):
        return line[0:cindex], line[cindex+1:]
    return line[0:cindex], ""


def tokenize_instruction(line: str) -> list:
    parts = line.split()
    tokens = []
    for part in parts:
        tokens.extend(part.split(','))
    tokens = [token.strip() for token in tokens if token.strip()]
    return tokens


def parse_instruction_line(line: str) -> Instruction:
    # if the line starts with .data but if it starts with .data somewhere in between the code give error then invoke a different parse line until corresponding .text is found
    # if the line starts with .text then start parsing the instructions

    tokens = tokenize_instruction(line)
    opcode = tokens[0].lower()
    instr = Instruction(opcode=opcode, original_line=line)
    if opcode in ["add", "sub","mul","div"]:
        if len(tokens) == 4:
            if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
            if tokens[2] == "cid" and tokens[3] == "cid":
                instr.rd, instr.rs1, instr.rs2 = tokens[1], "x32", "x32"
            elif tokens[2] == "cid" or tokens[3] == "cid":
                if tokens[2] == "cid":
                    instr.rd, instr.rs2,instr.rs1 = tokens[1], tokens[3] , "x32"
                else:
                    instr.rd, instr.rs1,instr.rs2 = tokens[1], tokens[2] , "x32"
            else:
                instr.rd, instr.rs1, instr.rs2 = tokens[1], tokens[2], tokens[3]
        else:
            raise ValueError(f"Invalid syntax for add/sub:{line}")
    elif opcode in ["addi", "slli"]:
        if len(tokens) == 4:
            if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
            if tokens[2] == "cid":
                instr.rd, instr.rs1, instr.immediate = tokens[1], "x32", int(tokens[3])
            else:
                instr.rd, instr.rs1, instr.immediate = tokens[1], tokens[2], int(tokens[3])
        else:
            raise ValueError(f"Invalid Syntax for addi:{line}")
    elif opcode in ["li"]:
        if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
        if len(tokens) == 3:
            instr.rd, instr.immediate = tokens[1], int(tokens[2])
        else:
            raise ValueError(f"Invalid syntax for li:{line}")
    elif opcode in ["nop"]:
        pass
    elif opcode in ["bne", "beq", "bge"]:
        if len(tokens) == 4:
            if tokens[1] == "cid" and tokens[2] == "cid":
                instr.rs1, instr.rs2, instr.label = "x32", "x32", tokens[3]
            elif tokens[1] == "cid" or tokens[2] == "cid":
                if tokens[1] == "cid":
                    instr.rs1, instr.rs2, instr.label = "x32", tokens[2], tokens[3]
                else:
                    instr.rs1, instr.rs2, instr.label = tokens[1], "x32", tokens[3]
            else:
                instr.rs1, instr.rs2, instr.label = tokens[1], tokens[2], tokens[3]
        else:
            raise ValueError(f"Invalid syntax for bne:{line}")
    elif opcode in ["jal"]:
        if len(tokens) == 3:
            if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
            instr.rd, instr.label = tokens[1], tokens[2]
        else:
            raise ValueError(f"Invalid syntax for jal:{line}")
    elif opcode in ["jalr"]:
        if len(tokens) == 4:
            if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
            instr.rd, instr.rs1, instr.immediate = tokens[1], tokens[2], int(
                tokens[3])
        else:
            raise ValueError(f"Invalid syntax for jalr:{line}")
    elif opcode in ["la"]:
        if len(tokens) == 3:
            if tokens[1] == "a0" or tokens[1] == "a7":
                if tokens[1] == "a0":
                    tokens[1] = "x10"
                else:
                    tokens[1] = "x17"
            instr.rd, instr.label = tokens[1], tokens[2]
        else:
            raise ValueError(f"Invalid syntax for la:{line}")
    elif opcode in ["lw", "sw"]:
        if len(tokens) == 3:
            if opcode == "lw":
                instr.rd = tokens[1]
            else:
                if tokens[1] == "cid":
                    instr.rs2 = "x32"
                else:
                    instr.rs2 = tokens[1]
            try:
                offset, rest = tokens[2].split('(')
                instr.immediate = int(offset)
                instr.rs1 = rest[:-1]
            except Exception as e:
                raise ValueError(f"Invalid memory format for lw/sw:{line}")
        else:
            raise ValueError(f"Invalid syntax for lw/sw:{line}")
    
    elif opcode in ["lw_spm","sw_spm"]:
        if len(tokens) == 3:
            if opcode == "lw_spm":
                instr.rd = tokens[1]
            else:
                if tokens[1] == "cid":
                    instr.rs2 = "x32"
                else:
                    instr.rs2 = tokens[1]
            try:
                offset, rest = tokens[2].split('(')
                instr.immediate = int(offset)
                instr.rs1 = rest[:-1]
            except Exception as e:
                raise ValueError(f"Invalid memory format for lw_spm/sw_spm:{line}")
        else:
            raise ValueError(f"Invalid syntax for lw_spm/sw_spm:{line}")
    
    elif opcode in ["j"]:
        instr.label = tokens[1]
    elif opcode in ["ecall"]:
        pass
    elif opcode in ["sync"]:
        pass
    else:
        raise ValueError(f"OpCode not implemented yet:{line}")
    return instr

def parse_data_instruction_line(line: str) -> DataInstruction:
    tokens = tokenize_instruction(line)
    
    # Check if tokens list is empty
    if not tokens:
        raise ValueError(f"Invalid data instruction (empty tokens): {line}")

    # Handle special case for partial_sum: .word 0 0 0 0 0
    if ":" in tokens[0] and len(tokens) == 1:
        label = tokens[0].rstrip(':')
        # Return a placeholder instruction and 0 value count
        return DataInstruction(label=label, directive=".word", values=[], original_line=line), 0
    
    # Regular case with label: .word value1 value2...
    if len(tokens) >= 2 and tokens[1] == ".word":
        label = tokens[0].rstrip(':')
        directive = ".word"
        values = [int(val, 0) for val in tokens[2:]]
        return DataInstruction(label=label, directive=directive, values=values, original_line=line), len(tokens) - 2
    
    # Case with label:.word value1 value2...
    elif len(tokens) >= 1 and ".word" in tokens[0]:
        cindex = tokens[0].find(":")
        label = tokens[0][0:cindex]
        directive = ".word"
        values = [int(val, 0) for val in tokens[1:]]
        return DataInstruction(label=label, directive=directive, values=values, original_line=line), len(tokens) - 1
    
    # Case with just a label (no values)
    elif ":" in tokens[0]:
        label = tokens[0].rstrip(':')
        return DataInstruction(label=label, directive=".word", values=[], original_line=line), 0
    
    else:
        raise ValueError(f"Invalid data instruction: {line}")
    
def parse_scratch_pad(line: str) -> ScratchInstruction:
    tokens = tokenize_instruction(line)
    
    # Check if tokens list is empty
    if not tokens:
        raise ValueError(f"Invalid scratch instruction (empty tokens): {line}")
        
    # Handle special case for empty directive
    if len(tokens) == 1 and ":" in tokens[0]:
        label = tokens[0].rstrip(':')
        return ScratchInstruction(label=label, directive=".word", values=[], original_line=line), 0

    if len(tokens) >= 2 and tokens[1] == ".word":
        label = tokens[0].rstrip(':')
        directive = ".word"
        values = [int(val, 0) for val in tokens[2:]]
        return ScratchInstruction(label=label, directive=directive, values=values, original_line=line), len(tokens) - 2
    
    elif len(tokens) >= 1 and ".word" in tokens[0]:
        cindex = tokens[0].find(":")
        label = tokens[0][0:cindex]
        directive = ".word"
        values = [int(val, 0) for val in tokens[1:]]
        return ScratchInstruction(label=label, directive=directive, values=values, original_line=line), len(tokens) - 1
    
    else:
        raise ValueError(f"Invalid scratch instruction: {line}")
    
def parse_assembly_file(file_path: str):
    instructions = []
    global_label_map = {}
    data_instructions = []
    scratch_instructions = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    instruction_counter = 0
    in_data_section = False
    in_text_section = True
    in_scratch_section = False
    data_values = 0
    scratch_value = 0

    for line in lines:
        cline = clean_line(line)
        if not cline:  # Skip empty lines
            continue

        if cline == '.data':
            in_data_section = True
            in_text_section = False
            in_scratch_section = False
            continue
        elif cline == '.text':
            in_data_section = False
            in_text_section = True
            in_scratch_section = False
            continue
        elif cline == '.scratchpad':
            in_data_section = False
            in_text_section = False
            in_scratch_section = True
            continue

        if in_data_section:
            try:
                data_instr, i = parse_data_instruction_line(cline)
                if data_instr:
                    data_instructions.append(data_instr)
                    data_values += i
            except ValueError as e:
                print(f"Error parsing data instruction: {e}")
                
        elif in_text_section:
            try:
                if is_label(cline):
                    label, linstr = extract_label(cline)
                    global_label_map[label] = instruction_counter
                    linstr = clean_line(linstr)
                    if linstr:
                        instr = parse_instruction_line(linstr)
                        if instr:
                            instructions.append(instr)
                            instruction_counter += 1
                else:
                    instr = parse_instruction_line(cline)
                    if instr:
                        instructions.append(instr)
                        instruction_counter += 1
            except ValueError as e:
                print(f"Error parsing text instruction: {e}")
                
        elif in_scratch_section:
            try:
                scratch_instr, i = parse_scratch_pad(cline)
                if scratch_instr:
                    scratch_instructions.append(scratch_instr)
                    scratch_value += i
            except ValueError as e:
                print(f"Error parsing scratch instruction: {e}")

    return instructions, global_label_map, data_instructions, data_values, scratch_instructions, scratch_value