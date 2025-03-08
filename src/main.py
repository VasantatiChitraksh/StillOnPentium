import sys
from simulator import Simulator

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python run.py <assembly_file>")
    else:
        assembly_file = sys.argv[1]
        simulator = Simulator()
        simulator.run_simulator(assembly_file)