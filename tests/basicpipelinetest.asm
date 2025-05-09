.data 
arr: .word 0x1 0x2 0x3 0x4 0x5

.text
beq x0 cid exit
addi x2 x0 2

goto:
    sync
    addi x4 x0 5
    addi a0 x0 5

exit:
    li a7 1
    ecall