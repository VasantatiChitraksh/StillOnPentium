addi x20,x0,600
addi x14,x0,1
sw x14,0(x20)
addi x14,x0,5
sw x14,4(x20)
addi x14,x0,2
sw x14,8(x20)
addi x14,x0,4
sw x14,12(x20)
addi x14,x0,7
sw x14,16(x20)
addi x14,x0,2
sw x14,20(x20)
addi x14,x0,6
sw x14,24(x20)
addi x14,x0,8
sw x14,28(x20)
addi x14,x0,1
sw x14,32(x20)
addi x14,x0,10
sw x14,36(x20)

addi x14,x20,0 #Load base address of array
addi x5,x0,10     #n = 10
addi x10,x0,9   #n = 10 - 1
addi x11,x0,0    #i = 0
addi x19,x0,4   #4bytes
addi x30,x0,0 #k = 0 for printing

loop1:
    beq x11,x10,end
    addi x13,x0,0 
    sub x12,x10,x11  #n-1-i
    addi x11,x11,1   #j = 0
loop2:
    beq x13, x12, loop1  # If j == n-1-i, go back to loop1
    slli x20, x13, 2     # j * 4 (index offset)
    add x21, x14, x20    # Base + offset
    lw x15, 0(x21)       # Load arr[j]
    
    addi x16,x13,1
    slli x20,x16,2 
    add x22,x14,x20
    lw x17,0(x22)    #load arr[j+1]
    
    bge x15,x17,if
    addi x13,x13,1
    j loop2
if:
    addi x13,x13,1
    sw x15,0(x22)
    sw x17,0(x21)
    j loop2
end:
    addi x30,x0,1431655765