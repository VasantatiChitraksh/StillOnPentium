import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Now import Instruction
from instructions import Instruction

# Test example
inst = Instruction(opcode="ADD", rd="x1", rs1="x2", rs2="x3")
print(inst)
