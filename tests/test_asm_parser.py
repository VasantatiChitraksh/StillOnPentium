import unittest
import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src")))


# Now import the necessary modules
from asm_parser import clean_line, tokenize_instruction, parse_instruction_line, parse_assembly_file
from instructions import Instruction

class TestASMParser(unittest.TestCase):

    def test_clean_line(self):
        line = "add x1, x2, x3  # add operation"
        cleaned = clean_line(line)
        self.assertEqual(cleaned, "add x1, x2, x3")

    def test_tokenize_instruction(self):
        line = "add x1, x2, x3"
        tokens = tokenize_instruction(line)
        self.assertEqual(tokens, ["add", "x1", "x2", "x3"])

    def test_parse_instruction_line_add(self):
        line = "add x1, x2, x3"
        instr = parse_instruction_line(line)
        self.assertEqual(instr.opcode, "add")
        self.assertEqual(instr.rd, "x1")
        self.assertEqual(instr.rs1, "x2")
        self.assertEqual(instr.rs2, "x3")

    def test_label_mapping(self):
        # Use a multi-line string to simulate a file.
        instructions, label_map = parse_assembly_file('tests/sample.asm')
        print(instructions)
        print(label_map)


if __name__ == '__main__':
    unittest.main()
