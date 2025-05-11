.scratchpad
head: .word 1 2 3 4 5 6 7 8 9 10 11 12 26 27 28 29 30 31 32 33 34 35 36 37 51 52 53 54 55 56 57 58 59 60 61 62 76 77 78 79 80 81 82 83 84 85 86 87

.data 
arr: .word 13 14 15 16 17 18 19 20 21 22 23 24 25 38 39 40 41 42 43 44 45 46 47 48 49 50 63 64 65 66 67 68 69 70 71 72 73 74 75 88 89 90 91 92 93 94 95 96 97 98 99 100

partial_sum: .word 0 0 0 0 0

.text
add x2  x0  cid                  # Load cid (passed externally)

la x1  arr                       # Base address of arr
la x12  head                     # Base address of scratchpad (DO NOT offset)
la x30  partial_sum              # Address to store partial sum

# Calculate offset for arr based on cid
# Each cid processes 13 elements from normal memory
addi x3  x0  13                  # Each cid gets 13 elements from arr
mul x4  x3  x2                   # offset = 13 * cid
slli x4  x4  2                   # Convert to byte offset (x4)
add x1  x1  x4                   # x1 = &arr[cid * 13]

# Calculate offset for scratchpad based on cid
# Each cid processes 12 elements from scratchpad
addi x5  x0  12                  # Each cid gets 12 elements from scratchpad
mul x6  x5  x2                   # offset = 12 * cid
slli x6  x6  2                   # Convert to byte offset (x4)
add x12  x12  x6                 # x12 = &head[cid * 12]

# Calculate offset for partial_sum based on cid
addi x3  x0  4                   # 4 bytes per word
mul x4  x3  x2                   # offset = 4 * cid
add x30  x30  x4                 # x30 = &partial_sum[cid]

# Sum from scratchpad (head) first: 12 elements per cid
addi x25  x0  12                 # 12 elements per cid from scratchpad
addi x26  x0  0                  # i = 0
addi x27  x0  0                  # sum_head = 0

loop_spm:
    beq x25  x26  next           # If i == 12  move to next section
    slli x28  x26  2             # i * 4 (byte offset)
    add x29  x12  x28            # address = head + offset + i*4
    lw_spm x13  0(x29)           # load from scratchpad
    add x27  x27  x13            # accumulate sum
    addi x26  x26  1             # i++
    j loop_spm

next:
    addi x5  x0  13              # 13 elements per cid from arr
    addi x6  x0  0               # i = 0
    add x7  x0  x27              # Initialize sum with scratchpad sum

loop:
    beq x5  x6  end              # if i == 13  end loop
    slli x20  x6  2              # i * 4 (byte offset)
    add x21  x1  x20             # addr = arr + offset + i*4
    lw x8  0(x21)                # load element from memory
    add x7  x7  x8               # sum += element
    addi x6  x6  1               # i++
    j loop

end:
    sw x7  0(x30)                # partial_sum[cid] = sum
    
    # Add a sync barrier to ensure all cores have computed their partial sums
    sync
    
    beq x2  x0  all              # if cid == 0  sum all partial sums
    j finish

all:
    addi x9  x0  4               # sum 4 partial sums (for 4 cores)
    addi x10  x0  0              # i = 0
    addi x11  x0  0              # total sum = 0
    la x30  partial_sum          # reset base addr

loop2:
    beq x9  x10  finish2
    slli x20  x10  2             # i * 4 (byte offset)
    add x21  x30  x20            # addr = partial_sum + i*4
    lw x8  0(x21)                # load partial sum
    add x11  x11  x8             # total += partial_sum[i]
    addi x10  x10  1             # i++
    j loop2

finish2:
    # store final total sum in memory
    add x31  x0  x11             # Store in x31 for reference
    addi x21  x30  20            # Get address right after partial_sum array
    sw x11  0(x21)               # Store final sum

    # print result
    add x10  x0  x11
    addi x17 x0  1 
    ecall

finish:
    add x0 x0 x0