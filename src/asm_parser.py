from instructions import Instruction
from data_instructions import DataInstruction


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
    elif opcode in ["li"]:
        if len(tokens) == 3:
            instr.rd, instr.immediate = tokens[1], int(tokens[2])
        else:
            raise ValueError(f"Invalid syntax for li:{line}")
    elif opcode in ["nop"]:
        pass
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
    elif opcode in ["la"]:
        if len(tokens) == 3:
            instr.rd, instr.label = tokens[1], tokens[2]
        else:
            raise ValueError(f"Invalid syntax for la:{line}")
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


# def parse_data_section(lines: list) -> tuple:
#     data_instructions = []
#     label_map = {}
#     data_start = -1
#     data_end = -1

#     # Find the range of the .data section
#     for i, line in enumerate(lines):
#         cline = clean_line(line)
#         if not cline:
#             continue
#         if cline.startswith(".data"):
#             data_start = i + 1  # Start after .data
#         elif cline.startswith(".text"):
#             data_end = i  # Stop before .text
#             break

#     # If .text isn't found, use length of lines as end
#     if data_end == -1:
#         data_end = len(lines)

#     # Ensure valid range before iterating
#     if data_start == -1:
#         raise ValueError("Invalid or missing .data section!")

#     lines = lines[data_start:data_end]

#     i = 0
#     while i < len(lines):
#         cline = clean_line(lines[i])
#         if not cline:
#             i += 1
#             continue

#         tokens = tokenize_instruction(cline)
#         if not tokens:
#             i += 1
#             continue

        

#         # Handle label
#         label = tokens[0].strip(":")

#         # Case 1: Single address value
#         if len(tokens) == 3 and tokens[2].isdigit():
#             label_map[label] = int(tokens[2])
#             print(f"Processed label: {label} with address: {tokens[2]}")
#             i += 1
#             continue

#         # Case 2: Array values
#         elif len(tokens) >= 3 and tokens[1] == ".word":
#             values = []
#             for value in tokens[2:]:
#                 try:
#                     values.append(int(value))
#                 except ValueError:
#                     raise ValueError(
#                         f"Invalid numeric value in data section: {value}")

#             data_instructions.append({
#                 'label': label,
#                 'directive': ".word",
#                 'values': values,
#                 'original_line': cline
#             })
#             # print(f"Processed label: {label} with values: {values}")
#         else:
#             raise ValueError(f"Invalid data section line: {cline}")
#         i +=1
#     return data_instructions, label_map

def parse_data_instruction_line(line: str) -> DataInstruction:
    tokens = tokenize_instruction(line)
    if tokens[1] == ".word":
        label = tokens[0].rstrip(':')
        directive = ".word"
        values = [int(val) for val in tokens[2:]]
        return DataInstruction(label=label, directive=directive, values=values, original_line=line),len(tokens)-2
    else:
        raise ValueError(f"Invalid data instruction: {line}")
    


def parse_assembly_file(file_path: str):
    instructions = []
    global_label_map = {}
    data_instructions = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    instruction_counter = 0
    in_data_section = False
    in_text_section = True
    data_values = 0

    for line in lines:
        cline = clean_line(line)
        if not cline:  # Skip empty lines
            continue

        if cline == '.data':
            in_data_section = True
            in_text_section = False
            continue
        elif cline == '.text':
            in_data_section = False
            in_text_section = True
            continue

        if in_data_section:
            data_instr,i = parse_data_instruction_line(cline)
            if data_instr:
                data_instructions.append(data_instr)
                data_values += i

        elif in_text_section:
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
    



    return instructions, global_label_map, data_instructions, data_values
