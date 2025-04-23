.data
arr:    .word 0x1 0x2 0x3 0x4 0x5 0x6 0x7 0x8 0x9 0xa 0xb 0xc 0xd 0xe 0xf 0x10 0x11 0x12

.text
    la x1, arr          # x1 points to arr[0]

    # Load from arr[0] -> cache line 0 (arr[0], arr[1])
    lw x2, 0(x1)
    addi a0, x2, 0
    li a7, 1
    ecall

    # Load from arr[2] -> cache line 1 (arr[2], arr[3])
    lw x3, 8(x1)
    addi a0, x3, 0
    li a7, 1
    ecall

    # Load from arr[4] -> cache line 2 (arr[4], arr[5])
    lw x4, 16(x1)
    addi a0, x4, 0
    li a7, 1
    ecall

    # Load from arr[6] -> cache line 3 (arr[6], arr[7])
    lw x5, 24(x1)
    addi a0, x5, 0
    li a7, 1
    ecall

    # Load from arr[8] -> 5th unique cache line (arr[8], arr[9]) -> evict LRU (arr[0])
    lw x6, 32(x1)
    addi a0, x6, 0
    li a7, 1
    ecall

    lw x6, 40(x1)
    addi a0, x6, 0
    li a7, 1
    ecall

    lw x6, 48(x1)
    addi a0, x6, 0
    li a7, 1
    ecall

    lw x6, 56(x1)
    addi a0, x6, 0
    li a7, 1
    ecall

    lw x6, 64(x1)
    addi a0, x6, 0
    li a7, 1
    ecall

    # Re-access arr[0] -> should now be a cache miss (reloaded into cache)
    lw x7, 0(x1)
    addi a0, x7, 0
    li a7, 1
    ecall

    # Exit
    li a7, 10
    ecall
