## High-Level Design

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
