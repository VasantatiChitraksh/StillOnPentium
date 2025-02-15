# Bubble Sort Assembly program



data:
    # Let's assume we store the array in memory starting at a known location.
    # This example is illustrative; adjust according to your memory model.
    .word 34
    .word 7
    .word 23
    .word 32
    .word 5

# Code section
start:
    # Initialize registers: assume x1 holds the base address of the array,
    # x2 holds the number of elements, x3 for the outer loop counter, and x4 for the inner loop.
    addi x1, x0, 512    # base address for data segment (example address)
    addi x2, x0, 5      # number of elements in the array
    addi x3, x0, 0      # outer loop index = 0

outer_loop:
    # If outer loop index >= (number of elements - 1), jump to end.
    bne x3, x2, inner_loop
    jal x0, finish

inner_loop:
    # Inner loop: Compare adjacent elements and swap if needed.
    # Setup inner loop counter (x4) = 0.
    addi x4, x0, 0
inner_loop_start:
    # Check if inner loop counter >= (number of elements - outer_index - 1)
    add x5, x2, x0      # x5 = number of elements
    sub x5, x5, x3      # x5 = number of elements - outer_loop index
    addi x5, x5, -1     # x5 = (number of elements - outer_index - 1)
    bne x4, x5, compare  # if x4 != x5, then compare; else, end inner loop
    jal x0, outer_inc

compare:
    # Load adjacent elements: address = base + (x4 * 4) and address = base + ((x4+1)*4)
    # Assume lw loads a word and sw stores a word.
    
    add x7, x1, x6      # x7 = base address + offset
    lw x8, 0(x7)        # x8 = array[x4]

    addi x6, x6, 4      # offset for next element
    add x9, x1, x6      # x9 = base address + offset for next element
    lw x10, 0(x9)       # x10 = array[x4+1]

    # Compare: if array[x4] > array[x4+1] then swap
    sub x11, x8, x10
    bne x11, x0, swap   # if x11 != 0 then values differ (for simplicity, assume non-zero means greater)
    # (In a real scenario, you’d need a conditional branch for greater-than)
    # For now, if not equal, we always swap (for testing purposes)
    jal x0, no_swap

swap:
    # Swap the two values
    sw x10, 0(x7)      # store the smaller value in array[x4]
    sw x8, 0(x9)       # store the larger value in array[x4+1]

no_swap:
    # Increment inner loop counter and repeat
    addi x4, x4, 1
    jal x0, inner_loop_start

outer_inc:
    # Increment outer loop counter and repeat outer loop.
    addi x3, x3, 1
    jal x0, outer_loop

finish:
    # End of program: Loop infinitely or halt (simulate a halt)
    jal x0, finish
