## **Phase One: Multi-Core RISC-V Simulator in Python**

### **1. Requirements Analysis & Initial Setup**

- **Review the Specification:**
  - **Multi-Core Architecture:**  
    - 4 processor cores.
    - Each core has its own register file and a read-only “core number” register.
    - All cores share the same memory (4KB total, divided as 1KB per core).
  - **Instruction Set:**  
    - Mandatory: `ADD`, `SUB`, `BNE`, `JAL`, `LW`, `SW`
    - One additional instruction of your choice (and possibly some immediate-type instructions).
  - **Assembly Input:**  
    - Read instructions from an assembly file (code need not be stored in simulated memory).
  - **Execution Model:**  
    - All cores run the same code concurrently, with each instruction taking one clock cycle.
    - Later extension: potential support for functions via `jal`/`jalr`.

- **Project Setup:**
  - Initialize a Git repository.
  - Create a basic project structure (directories for source code, tests, documentation, etc.).
  - Set up a README (remember to include the meeting minutes template as required).

---

### **2. High-Level Design**

- **Architecture Components:**
  - **Processor (Core) Class:**  
    - Contains a register file (32 registers if mimicking RISC-V, with one register dedicated to storing the core number).
    - Has a program counter (PC) and methods to execute instructions.
  - **Memory Module:**
    - Simulate 4KB memory.
    - Implement access control so that each core “owns” its 1KB segment (if needed for later extensions), while keeping a shared view for load/store operations.
  - **Instruction Parser & Decoder:**
    - Read and parse the assembly file.
    - Convert each instruction line into an internal representation (an object or a tuple with opcode and operands).
  - **Simulator (Controller) Class:**
    - Instantiate the 4 cores and shared memory.
    - Maintain the simulation loop: in each cycle, each core fetches and executes the next instruction.
    - Handle branch targets and jumps (maintaining labels mapping).
  - **I/O Module:**
    - For Phase One, output the final register states and memory dump after execution.
    - (Later: provide hooks for a web interface.)

- **Instruction Set Implementation:**
  - **Arithmetic:**  
    - `ADD rd, rs1, rs2`  
    - `SUB rd, rs1, rs2`
  - **Branching & Jumping:**  
    - `BNE rs1, rs2, LABEL`
    - `JAL rd, LABEL`
  - **Memory Operations:**  
    - `LW rd, offset(rs1)`
    - `SW rs2, offset(rs1)`
  - **Additional Instruction:**  
    - Decide on one extra (for example, `ADDI rd, rs1, immediate`) or any other immediate type.
    
- **Execution Cycle:**
  - Each instruction takes one cycle.  
  - Simulate each core “in lock-step” (one instruction per core per cycle) even though they do not interact for now.

---

### **3. Detailed Implementation Plan & Timeline**

**Day 1: Project Kick-Off and Setup**
- **Morning:**
  - Set up the git repository with the required README and project structure.
  - Re-read the RISC-V manual sections related to the supported instructions.
- **Afternoon:**
  - Create design sketches (class diagrams) for the Processor, Memory, and Simulator classes.
  - Decide on the internal representation for instructions and how to map labels.

**Day 2: Building the Assembly Parser & Instruction Representation**
- Write a parser in Python that:
  - Reads an assembly file line-by-line.
  - Removes comments and tokenizes instructions.
  - Builds a mapping for labels to instruction addresses.
- Create data structures (e.g., classes or namedtuples) to represent an instruction.

**Day 3: Implementing the Core and Memory Modules**
- **Core (Processor) Class:**
  - Initialize registers (including the special read-only core number register).
  - Implement methods to execute individual instructions.
- **Memory Module:**
  - Create a memory array (e.g., a list or bytearray) with 4KB size.
  - Implement methods for `LW` and `SW` that validate addresses and simulate memory access.
  
**Day 4: Instruction Execution Engine**
- Implement the execution loop for a single core:
  - Fetch, decode, and execute instructions sequentially.
  - Ensure that branches (`BNE` and `JAL`) update the program counter correctly.
- Write unit tests for each instruction to validate correct behavior.

**Day 5: Multi-Core Simulation Integration**
- Extend the simulation to instantiate 4 cores.
- Develop a controller that:
  - Loads the same set of instructions for all cores.
  - Executes one instruction per core per cycle.
  - Manages the program counter independently for each core.
- Test with simple assembly programs (e.g., basic arithmetic, looping constructs).

**Day 6: Testing with Bubble Sort and Debugging**
- Load a bubble sort assembly program and run it on all cores.
- Print the final state of registers for each core.
- Dump the memory contents.
- Debug any issues with synchronization or memory accesses.
- Optionally, add logging for each cycle to track instruction execution.

**Day 7: Final Polishing & Documentation**
- Refactor the code for clarity and maintainability.
- Update the README with detailed instructions, design decisions, and meeting minutes.
- Commit the final version for Phase One.
- Prepare notes for the next phase (web integration) including possible frameworks (Flask/Django for the backend, and a JavaScript frontend).

---

### **4. Future Considerations (For Later Phases)**
- **Web Simulator:**
  - Design a simple web interface that can load an assembly file, start/stop execution, and display register/memory states in real time.
  - Look into Python web frameworks (Flask/Django) for serving the simulator.
- **App Deployment:**
  - Explore cross-platform tools (e.g., Electron, or mobile app frameworks) for packaging the simulator.
- **Advanced Features:**
  - Single stepping, breakpoints, and graphical visualization of cores and memory.
  - Extend the instruction set as needed.

---

### **5. Summary & Next Steps**
- **Immediate Start (Tomorrow):**
  - Begin with project setup, repository initialization, and design discussions.
  - Set up a simple parser to read assembly files and map labels.
- **Milestone:**
  - By the end of Day 3, have a working prototype that simulates a single core.
  - By Day 5–6, integrate the multi-core simulation and test with provided examples.
- **Final Deliverable for Phase One:**
  - A command-line Python simulator that reads an assembly file, simulates 4 cores running in parallel (with shared memory), and prints out final register and memory states after executing the bubble sort (or any provided) program.

This plan should give you a clear roadmap to get started on Phase One tomorrow and ensure you have a solid foundation for later web and app-based versions. Happy coding!
