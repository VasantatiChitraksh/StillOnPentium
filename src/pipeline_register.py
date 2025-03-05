class PipelineRegister:
    def __init__(self):
        self.PC = 0                # Program Counter
        self.instruction = None     # Current instruction
        self.opcode = None
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.func3 = None
        self.func7 = None
        self.execute_result = None  # ALU computation result
        self.mem_value = None       # Memory read value
        self.cid = None             # Compute unit ID
        self.valid = False          # Indicates if instruction is active
        self.stalled = False        # Indicates if instruction is stalled
        self.flushed = False        # Indicates if instruction is flushed
        self.branch_taken = False
        self.branch_target = None
        self.rd_ready = False
        self.rs1_ready = False
        self.rs2_ready = False
        self.mem_ready = False
