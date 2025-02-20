# StillOnPentium

This project is a multi-core simulator written in Python. The simulator emulates four processor cores executing a common assembly program in parallel with a shared memory space of 4KB.

## Project Structure
- **src/**
  - **simulator.py**:Multi Core Execution
  - **execution_engine.py**:Single Core Execution
  - **core.py**: Core Module
  - **asm_parser.py**: Assembly Code Parser
  - **memory.py**: To Handle Memory
  - **instruction.py**:Instruction Dataclass
  - **data_instructions.py**: .data Section
- **tests/**: Unit tests and sample assembly programs.
  - **bubble_sort.asm**
  - **test_core_memory.py**
- **docs/**
  - **design.md**
  - **meeting_minutes.md**

## Meeting Minutes
Please refer to [docs/meeting_minutes.md](docs/meeting_minutes.md) for the meeting minutes.

## Getting Started
1. Clone the repository.
2. Navigate to the project directory.
3. Run the simulator using `python src/main.py`.

## Features (Phase 1)
- Supports instructions:
  - ADD, SUB, ADDI
  - BNE, BEQ, BGE
  - JAL, JALR, J
  - LW, SW
  - LI, LA
  - NOP
- Supports .data and .text sections with data section being created at the end of memory
- Four cores with a dedicated read-only core number register.
- Shared 4KB memory (1KB per core segment).
- Each core uses bounded access to use its own memory(1kb)
- Integrated high level Parser and DataClasses to have a structured way of storing the instructions.
- Used Matplotlib for simulations and understandability. 

