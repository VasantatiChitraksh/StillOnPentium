.scratchpad
head: .word 1 2 3 4

.data
arr: .word 1 2 3 4 5

.text 
la x2 arr
lw x3 0(x2)
sw x3 4(x2)