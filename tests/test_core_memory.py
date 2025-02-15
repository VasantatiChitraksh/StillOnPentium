import unittest
import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src")))
from memory import Memory
from core import Core
from instructions import Instruction

class TestCoreMemory(unittest.TestCase):
    def test_memory_read_write(self):
        mem = Memory()
        mem.write_word(0, 1234)
        self.assertEqual(mem.read_word(0), 1234)
        mem.write_word(2, 1122)
        self.assertEqual(mem.read_word(2), 1122)

    def test_core_registers(self):
        core = Core(core_id=1)
        core.set_register_value("x0", 999)
        self.assertEqual(core.get_register_value("x0"), 0)
        core.set_register_value("x1", 42)
        self.assertEqual(core.get_register_value("x1"), 42)

    def test_core_execute_add(self):
        core = Core(core_id=0)
        core.set_register_value("x3", 10)
        core.set_register_value("x4", 15)
        instr = Instruction(opcode="add", rd="x2", rs1="x3",
                            rs2="x4", original_line="add x2, x3, x4")
        core.execute_instruction(instr, None, {})
        self.assertEqual(core.get_register_value("x2"), 25)


if __name__ == '__main__':
    unittest.main()
