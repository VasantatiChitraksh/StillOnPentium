
        .data
        as: .word 1 2 3 4
        aaa: .word 5,6
        def: .word 7 8 9 1
        .text
        start: add a1, a2, a3 #aass
        sub a4, a5, a6
        loop: addi a7, a8, 10
        bne a1, a2, loop
        j end
        lw a1, 0(a2)
        sw a3, 4(a4)
        end: j start
        