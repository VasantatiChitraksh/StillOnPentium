# Simple Program for Testing Execution Engine

start:
    add x1, x0, x0      # x1 = 0 + 0
    addi x2, x0, 10     # x2 = 0 + 10
    add x3, x1, x2      # x3 = x1 + x2 => should be 10
    sub x4, x3, x1      # x4 = x3 - x1 => should be 10
    bne x4, x0, end   # if x4 != 0, jump to start (infinite loop for test)

end:
    addi x1,x1,2