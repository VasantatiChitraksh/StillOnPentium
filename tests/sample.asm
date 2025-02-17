LABELx:
    addi x3, x3, 4
    addi x4,x0,4
    sw x3, 0(x14)
    jal x5,LABELy
    beq x3,x4,end
LABELy:
    sub x6, x0, x2
    addi x2, x0, 0
    jalr x6,x5,0
end:
    addi x2,x0,0
