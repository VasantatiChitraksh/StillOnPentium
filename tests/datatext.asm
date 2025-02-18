.data
plis: .word 10,11,12
pli1s: .word 10,11,12
.text
la x5,plis
lw x6,0(x5)
addi x5,x5,4
lw x7,0(x5)