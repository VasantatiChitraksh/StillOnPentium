li x8 128 #has the size of the L1 cache
li x9 4 #has the size of the word
li x8 32 #it maintains the value of X=(size of the cache)/(size of word)

addi x21 x0 0
addi x22 x0 100

Loop:
    beq x22 x21 done
    jal x1 Add
    addi x21 x21 1
    j Loop

Add:
    la x18 arr
    bne CID 0 afterSum0
    addi x23 x0 0 #i=0
    addi x24 x0 25 #first 25
    lw x25 13804(x0) #sum
    Loop0:
        beq x23 x24 done0
        lw x30 0(x18)
        add x25 x25 x30
        addi x18 x18 128
        addi x23 x23 1
        j Loop0

    done0:
        sw x25 13804(x0) #sum
        j afterSum0
    
    afterSum0:
    SYNC
    bne CID 1 afterSum1
    addi x23 x0 0 #i=0
    addi x24 x0 25 #second 25
    lw x25 13808(x0) #
    addi x18 x0 3200
    Loop1:
        beq x23 x24 done1
        lw x30 0(x18)
        add x25 x25 x30
        addi x18 x18 128
        addi x23 x23 1
        j Loop1
    
    done1:
        sw x25 13808(x0) #sum
        j afterSum1
    
    afterSum1:
    SYNC
    bne CID 2 afterSum2
    addi x23 x0 0 #i=0
    addi x24 x0 25 #second 25
    lw x25 13812(x0) #
    addi x18 x0 6400
    Loop2:
        beq x23 x24 done2
        lw x30 0(x18)
        add x25 x25 x30
        addi x18 x18 128
        addi x23 x23 1
        j Loop2
    
    done2:
        sw x25 13812(x0) #sum
        j afterSum2

    afterSum2:
    SYNC
    bne CID 2 afterSum3
    addi x23 x0 0 #i=0
    addi x24 x0 25 #second 25
    lw x25 13816(x0) #
    addi x18 x0 9600
    Loop3:
        beq x23 x24 done3
        lw x30 0(x18)
        add x25 x25 x30
        addi x18 x18 128
        addi x23 x23 1
        j Loop3
    
    done3:
        sw x25 13816(x0) #sum
        j afterSum3

    afterSum3:
        jr x1

done:
    SYNC
    bne CID 0 Finish
    lw x22 13804(x0)
    lw x23 13808(x0)
    lw x24 13812(x0)
    lw x25 13816(x0)
    add x23 x22 x23
    add x24 x24 x23
    add x25 x25 x24
    sw x25 13804(x0)

    li x17 1
    lw x10 13804(x0)
    ecall

Finish: