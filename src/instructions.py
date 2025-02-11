#src/instructions.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Instruction:
    opcode:str
    rd: Optional[str]=None      #Destination Register
    rs1: Optional[str]=None     #Source Register 1
    rs2: Optional[str]=None     #Source Register 2
    immediate: Optional[int]=None   #For immediate Instructions
    label: Optional[str]=None       #For Jump and branch Instructions
    original_line: Optional[str]=None   #debugging
    
