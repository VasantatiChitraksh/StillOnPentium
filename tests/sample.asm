LABELx:
    addi x3, x3, 4
    addi x4,x0,4
    sw x3, 0(x14)
    beq x3,x4,end
LABELy:
    sub x6, x0, x2
    addi x2, x0, 0
    j LABELx

end:
    addi x2,x0,0
