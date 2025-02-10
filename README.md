# StillOnPentium

This project is a multi-core simulator written in Python. The simulator emulates four processor cores executing a common assembly program in parallel with a shared memory space of 4KB.

## Project Structure
- **src/**: Simulator source code.
- **tests/**: Unit tests and sample assembly programs.
- **docs/**: Documentation and design documents.

## Meeting Minutes
Please refer to [docs/meeting_minutes.md](docs/meeting_minutes.md) for the meeting minutes.

## Getting Started
1. Clone the repository.
2. Navigate to the project directory.
3. Run the simulator using `python src/main.py`.

## Features (Phase 1)
- Supports instructions: ADD, SUB, BNE, JAL, LW, SW, and one additional immediate-type instruction.
- Four cores with a dedicated read-only core number register.
- Shared 4KB memory (1KB per core segment).

