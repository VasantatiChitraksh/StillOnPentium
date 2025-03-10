# High-Level Design

## Phase 2

### Modules:
- **Core Class:**
  - Attributes: registers (including a read-only core number), program counter (PC), active registers(for hazard checking), pipeline registers (IF_ID, ID_EX, etc.), stall count
  - Methods: Pipeline stages in execute_instruction() (instr_decode_reg_fetch(), execute(), memory_access(), write_back()), get/set register values, get_forwaded_data() (for data forwarding) 
- **Memory Class:**
  - Attributes: memory array (4KB)
  - Methods: read(address), write(address, value)
- **Instruction Parser:**
  - Methods: parse_file(filename) -> list of instructions, label mapping
- **Simulator Controller:**
  - Attributes: list of cores, shared memory
  - Methods: run_simulation(), cycle(), display_state(), instruction_fetch() (A single instruction fetch unit)

### Data Flow:
- The **main file** reads the argument from the cmd line and sends the file name to **Simulator Controller**
- The **Simulator Controller** loads an assembly file using the **Instruction Parser**.
- **Instruction Parser** converts the instructions into the dataclass **instruction**
- **Simulator Controller** uses instruction fetch unit to send instructions to the cores
- Each **Core** executes instructions and interacts with the **Memory** as needed.
- At the end, **main** visualises the state of the memory and registers

## Phase 1

### Modules:
- **Core Class:**
  - Attributes: registers (including a read-only core number), program counter (PC)
  - Methods: execute_instruction(), fetch(), decode(), etc.
- **Memory Class:**
  - Attributes: memory array (4KB)
  - Methods: read(address), write(address, value)
- **Instruction Parser:**
  - Methods: parse_file(filename) -> list of instructions, label mapping
- **Simulator Controller:**
  - Attributes: list of cores, shared memory
  - Methods: run_simulation(), cycle(), display_state()

### Data Flow:
- The **Simulator Controller** loads an assembly file using the **Instruction Parser**.
- The parsed instructions are fed to each **Core** instance.
- Each **Core** executes instructions and interacts with the **Memory** as needed.
