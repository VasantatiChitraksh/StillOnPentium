import unittest
import sys
import os
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src")))
from asm_parser import parse_assembly_file, Instruction, DataInstruction

class TestAsmParser(unittest.TestCase):

    def test_labels_and_instructions(self):
        assembly_code = """
        .data
        as: .word 1 2 3 4
        aaa: .word 5,6
        def: .word 7 8 9 1
        .text
        start: add a1, a2, a3 #aass
        sub a4, a5, a6
        loop: addi a7, a8, 10
        bne a1, a2, loop
        j end
        lw a1, 0(a2)
        sw a3, 4(a4)
        end: j start
        """

        # Write the mock assembly code to a temporary file
        with open('test.asm', 'w') as f:
            f.write(assembly_code)

        # Parse the assembly file
        instructions, label_map, data_instructions, data_values = parse_assembly_file('test.asm')

        i = 0
        for inst in instructions:
            print("Instruction "+str(i),end = " :")
            print(inst)
            i+=1
        for label in label_map:
            print(label+"|"+str(label_map[label]))
        for data in data_instructions:
            print(data)
        print(data_values)

if __name__ == '__main__':
    unittest.main()