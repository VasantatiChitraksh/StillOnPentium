# Sample Assembly File for Testing

start:
    add x1, x2, x3   # R-type instruction
    sub x4, x1, x5
    bne x1, x6, loop
    jal x0, start

loop:
    lw x7, 0(x8)
    sw x7, 4(x8)
    addi x9, x9, 10
