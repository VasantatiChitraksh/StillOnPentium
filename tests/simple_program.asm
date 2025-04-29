start:
    add x1, x0, x0      # x1 = 0 + 0
    addi x2, x0, 10     # x2 = 0 + 10
    add x3, x1, x2      # x3 = x1 + x2 => should be 10
    sub x4, x3, x1      # x4 = x3 - x1 => should be 10
    bne x4, x0, end   # if x4 != 0, jump to start (infinite loop for test)

end:
    addi x1,x1,2
    slli x6,x1,4
    sw x1,100(x10)
    sw x6,104(x10)
    addi x3 x1 1
    addi x5 x1 2
    addi x6 x1 3
    addi x7 x1 2
    addi x8 x1 8
    addi x9 x1 7
    addi x10 x1 8
    addi x11 x1 9