from instructions import Instruction


def clean_line(line: str) -> str:
    comment_index = line.find('#')
    if comment_index != -1:
        line = line[0:comment_index]
    return line.strip()


def is_label(line: str) -> bool:
    if(line.find(':')==-1):
        return False
    return True  # Finds if Label has : in it


def extract_label(line: str) -> str:
    line=line.strip()
    cindex = line.find(':') # Finds the : index from the label
    if(line[cindex+1:]!=""):
        return line[0:cindex], line[cindex+1:]
    return line[0:cindex],""


def tokenize_instruction(line: str) -> list:
    parts = line.split()
    tokens = []
    for part in parts:
        tokens.extend(part.split(','))
    tokens = [token.strip() for token in tokens if token.strip()]
    return tokens


def parse_instruction_line(line: str) -> Instruction:
    tokens = tokenize_instruction(line)
    opcode = tokens[0].lower()
    instr = Instruction(opcode=opcode, original_line=line)
    if opcode in ["add", "sub"]:
        if len(tokens) == 4:
            instr.rd, instr.rs1, instr.rs2 = tokens[1], tokens[2], tokens[3]
        else:
            raise ValueError(f"Invalid syntax for add/sub:{line}")
    elif opcode in ["addi", "slli"]:
        if len(tokens) == 4:
            instr.rd, instr.rs1, instr.immediate = tokens[1], tokens[2], int(
                tokens[3])
        else:
            raise ValueError(f"Invalid Syntax for addi:{line}")
    elif opcode in ["bne", "beq", "bge"]:
        if len(tokens) == 4:
            instr.rs1, instr.rs2, instr.label = tokens[1], tokens[2], tokens[3]
        else:
            raise ValueError(f"Invalid syntax for bne:{line}")
    elif opcode in ["jal"]:
        if len(tokens) == 3:
            instr.rd, instr.label = tokens[1], tokens[2]
        else:
            raise ValueError(f"Invalid syntax for jal:{line}")
    elif opcode in ["jalr"]:
        if len(tokens) == 4:
            instr.rd, instr.rs1, instr.immediate = tokens[1], tokens[2], int(
                tokens[3])
        else:
            raise ValueError(f"Invalid syntax for jalr:{line}")
    elif opcode in ["lw", "sw"]:
        if len(tokens) == 3:
            if opcode == "lw":
                instr.rd = tokens[1]
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
    elif opcode in ["j"]:
        instr.label = tokens[1]
    else:
        raise ValueError(f"OpCode not implemented yet:{line}")
    return instr


def parse_assembly_file(file_path: str):
    instructions = []
    label_map = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
    instruction_counter = 0
    for line in lines:
        cline = clean_line(line)
        if not cline:  # Checks if clean_line is empty
            continue
        if is_label(cline):
            label,linstr = extract_label(cline)
            label_map[label] = instruction_counter
            linstr = clean_line(linstr)
            if linstr!="":
                instr = parse_instruction_line(linstr)
                if instr is not None:
                    instructions.append(instr)
                    instruction_counter += 1
        else: 
            instr = parse_instruction_line(cline)
            if instr is not None:
                instructions.append(instr)   
                instruction_counter += 1
    # We use two for loops because it is best to get all labels into the label map before trying to parse the instructions
    # for line in lines:
    #     cline = clean_line(line)
    #     if not cline or is_label(cline):
    #         continue
    #     instr = parse_instruction_line(cline)
    #     if instr is not None:
    #         instructions.append(instr)


    return instructions, label_map
