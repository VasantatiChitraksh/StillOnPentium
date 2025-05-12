# StillOnPentium

This project is a multi-core simulator written in Python. The simulator emulates four processor cores executing a common assembly program in parallel with a shared memory space of 128KB.

## Project Structure
- **Phase_1_Output/**: Output Files of phase 1
- **Phase_2_Output/**: Output Files of phase 2
- **Phase_3_Output/**:
  - **[output.md](Phase_3_Output/output.md)**: The phase 3 outputs and analysis
  - **[Report.md](Phase_3_Output/Report.md)**: The phase 3 implementation report
- **src/**
  - **main.py**: Main Simulator file
  - **simulator.py**: Multi Core Execution
  - **core.py**: Core Module
  - **asm_parser.py**: Assembly Code Parser
  - **memory.py**: To Handle Memory
  - **instructions.py**:Instruction Dataclass
  - **data_instructions.py**: .data Section
  - **scratchpad_instructions.py** : .scratchpad Section
  - **cache.py**: Cache Class
  - **cache_parameters.csv**: Input file for cache details
- **tests/**: Unit tests and sample assembly programs.
- **docs/**
  - **design.md**
  - **meeting_minutes.md**

## Meeting Minutes
Please refer to [docs/meeting_minutes.md](docs/meeting_minutes.md) for the meeting minutes.

## Getting Started
1. Clone the repository.
2. Navigate to the project directory.
3. Run the simulator using `python src/main.py [assembly_filename].asm ./cache_parameters.csv`.(Make sure the assembly file to be run is in the root directory or in the tests folder)
4. For e.g., `python src/main.py tests/bubble_sort.asm src/cache_parameters.csv` or `python src/main.py tests/sample.asm src/cache_parameters.csv`


## Features (Phase 3)
- L1 cache implemented with seperate instruction and data caches
- L2 cache implemented
- Added Latencies to all cache and implemented a proper memory hierarchy with "lru" and "nru" replacement policies.
- Implemented SYNC to synchronize all the compute units
- ScratchPad feature for frequently used data.

## Features (Phase 2)
- The cores now follow the five stages of the RISC-V pipeline with a single instruction fetch unit for all the cores
- Hazards are detected and stalls are made when needed
- Option to enable/disable Data Forwarding in pipeline
- Variable latencies for instructions
- CID(core id) register for all cores and can be used in assembly code

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

