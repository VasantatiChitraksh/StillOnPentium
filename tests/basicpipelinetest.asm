.data
arr: .word 0x2 0x3

.text
la x12 arr
lw x1 0(x12)
lw x2 4(x12)
addi x3 x0 3
addi x2 x2 0
sw x3 0(x12)
sw x2 4(x12)

loop:
addi x5 x5 2
bne x3 x2 end
addi x3 x2 1
j loop
end: addi x4 x0 5
add x0 x0 x0
add x0 x0 x0