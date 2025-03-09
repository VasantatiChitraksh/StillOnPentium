.data
arr: .word 1 2

.text
la x1 arr
lw x2 0(x1)

sw x2 4(x1)

sw x2 0(x3)
lw x4 0(x3)