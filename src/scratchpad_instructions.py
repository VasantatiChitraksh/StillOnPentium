from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ScratchInstruction:
    label: str                  # Variable name
    directive: str              # Data directive (.word, .byte, .asciiz, etc.)
    values: List[str]           # Values assigned to the variable
    original_line: Optional[str] = None  # Debugging
