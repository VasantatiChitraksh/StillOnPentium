# Meeting Minutes


### 10th Mar 2025
### Members : K Sandeep, V Chitraksh
- Final Bug Checking
---

### 9th Mar 2025
### Members : K Sandeep, V Chitraksh
- Data forwarding, Variable latency implemented
- Structural Hazards associated with global Instruction Fetch unit are also shown in simulator now
---

### 8th Mar 2025
### Members : K Sandeep, V Chitraksh
- As PipelineRegister classes were causing too many bugs, we decided to change the structure to reduce the bugs
- Implemented Hazard detection and stalls
---

### 7th Mar 2025
### Members : K Sandeep, V Chitraksh
- Split the execute_instruction() into 4 stages(excluding IF)
- Flushing implemented for branch and jump instructions
- Decided on further plans to implement hazard detection, stalls and data forwarding
---


### 6th Mar 2025
### Members : K Sandeep, V Chitraksh
- Designed a global instruction fetch unit
- Decided to make a PipelineRegister class to act as pipeline registers between the stages
---

### 4th Mar 2025
### Members : K Sandeep, V Chitraksh
- Started work on phase 2
- Discussion on structure of the program and listed the tasks to be completed
---

### 3rd Mar 2025
### Members : K Sandeep, V Chitraksh
- Discussed the requirements of phase 2 and the required changes that have to be implemented
- Drafted a rough day to day plan of tasks to do
---
## Phase 2 Start

### 19th Feb 2025
### Members : K Sandeep, V Chitraksh

- Met and discussed about future phases, whether our phase 1 is serving as a good foundation.
- Debugged and got everything ready for the phase 1 submission.
---

### 17th Feb 2025
### Members : K Sandeep, V Chitraksh

- Decided to include .data and .text segments, and execute memory instructions before other instrcutions.
- Bubble sort with .data is executing properly.
---

### 16th Feb 2025
### Members : K Sandeep, V Chitraksh

- Made a decision to include slli,beq,j as it is used in bubble sort and modified code accordingly
- Bubble sort is now working correctly
---
### 15th Feb 2025
### Members : K Sandeep, V Chitraksh

- Made simulator module which has 4 cores
- Each core uses bounded access in the shared memory
- Tested simulator with sample_program.asm
- Made a deadline to make the simulator run bubble sort by 16th Feb
---
### 13th Feb 2025
### Members : K Sandeep, V Chitraksh

- Made memory module and core module
- Tested both modules
---
### 11th Feb 2025
### Members : K Sandeep, V Chitraksh

- Made a parser which changes given human code and makes it cleaner. Also throws errors for code with incorrect syntax, unsupported opcodes
- Tested the parser with sample.asm
---
### 10th Feb 2025
### Members : K Sandeep, V Chitraksh

- Finalise Idea
- Had a discussion regarding the language to be used for the simulator
- Decided to use Python as it has simple and readable code
- Made a decision to support add,sub,addi,lw,sw,bne,jal
- Made a plan with daily tasks describing what to do on a particular day
---
## Phase 1 Start
