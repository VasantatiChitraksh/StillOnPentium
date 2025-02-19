.text 
la x1,arr         # Load array address
addi x2,x0,10     # n = 10
addi x3,x0,9      # n-1 = 9
addi x4,x0,0      # i = 0 (outer loop counter)

loop1:
    bge x4,x3,out
    addi x5,x0,0      # j = 0 (inner loop counter)
    sub x6,x3,x4      # n-1-i (inner loop limit)
    
loop2:
    beq x5,x6,next_iter   # If j == n-1-i, go to next iteration
    
    # Calculate address and load arr[j]
    slli x7,x5,2          # j * 4 (byte offset)
    add x8,x1,x7          # address of arr[j]
    lw x9,0(x8)           # load arr[j]
    
    # Calculate address and load arr[j+1]
    addi x10,x5,1         # j + 1
    slli x11,x10,2        # (j+1) * 4
    add x12,x1,x11        # address of arr[j+1]
    lw x13,0(x12)         # load arr[j+1]
    
    bge x9,x13,swap       # if arr[j] >= arr[j+1], swap
    addi x5,x5,1          # increment j
    j loop2
    
swap:
    sw x9,0(x12)          # store arr[j] in arr[j+1]'s position
    sw x13,0(x8)          # store arr[j+1] in arr[j]'s position
    addi x5,x5,1          # increment j
    j loop2
    
next_iter:addi x4,x4, 1          # increment i
    j loop1
    
out:
    nop

.data
arr: .word 1 5 2 4 7 2 6 8 1 0