# StillOnPentium
Authors: Chitraksh,Sandeep
ID: CS23B054, CS23B050

---
## Output Report

### Algorithms

We have to implement Strided array addition without using scratchpad memory and then using Strided array addition using scratchpad memory. In which we will take a stride and then add elements in the array by striding and sum this again and again 100 times.

### Codes

```asm=
Algorithm - 1

.data
arr: .word 1, 2, 3, 4, 5 .... 9981, ... 10000
sum: .word 0, 0, 0, 0, 0

.text
add x1,x0,cid  #x1 = cid
add x2,x0,x0   #x2 = s
addi x3,x0,100 #x3 = x
addi x4,x0,4   #x4 = 4
la x5,arr      #x5 = arr base
la x6,sum      #x6 = sum base
addi x7,x0,0   #x7 = i
addi x8,x0,25  #x8 = 25
addi x30,x0,100 #x30 = 100


loop1:
    beq x7 x30 next2
    addi x7 x7 1
    addi x12 x0 0
    loop2:
    beq x12 x30 loop1
    mul x13 x4 x1 
    add x13 x13 x6
    lw x2 0(x13)

    mul x14 x3 x12
    mul x14 x14 x4
    add x14 x14 x5
    lw x15 0(x14)

    add x2 x2 x15

    sw x2,0(x13) 
    addi x12 x12 1
    j loop2

next2:
    beq x1,x0,total_sum 
    j exit

total_sum:
    add x2,x0,x0 
    la x11,sum 
    addi x12,x0,0 #i = 0
    addi x13,x0,4 #total cores = 4

sum_loop:
    beq x12,x13,store_total # if i == 4, exit loop
    lw x14,0(x11) #Load sum[i]
    add x2,x2,x14 #Add to total sum
    addi x11,x11,4 #Move to next sum element
    addi x12,x12,1 #i++
    j sum_loop

store_total:
    la x11,sum 
    addi x11,x11,0 #Point to the last word (total sum location)
    sw x2,0(x11) #Store total sum in the last word of sum array  
exit:
    nop
   
```

```asm=
Algorithm - 2

.data
arr: .word 1 2 3 4 .... 9889 ... 10000
sum: .word 0, 0, 0, 0, 0

.text
add x1,x0,cid  #x1 = cid
add x2,x0,x0   #x2 = s
addi x3,x0,100 #x3 = x
addi x4,x0,4   #x4 = 4
la x5,arr      #x5 = arr base
la x6,sum      #x6 = sum base
addi x7,x0,0   #x7 = i
addi x8,x0,25  #x8 = 25
la x11 spm_arr
addi x30,x0,100 #x30 = 100

loop1:
    beq x7 x30 next
    mul x9 x3 x7
    mul x9 x9 x4
    add x9 x9 x5
    lw x10 0(x9)
    sw_spm x10 0(x11)
    addi x11 x11 4
    addi x7 x7 1
    j loop1

next:
    addi x7 x0 0
    la x11 spm_arr
    loop2:
        beq x7 x30 next2
        addi x7 x7 1
        addi x12 x0 0
        loop3:
        beq x12 x30 loop2
        mul x13 x4 x1 
        add x13 x13 x6
        lw x2 0(x13)

        mul x14 x12 x4
        add x14 x14 x11
        lw_spm x15 0(x14)

        add x2 x2 x15

        sw x2,0(x13) 
        addi x12 x12 1
        j loop3

next2:
    beq x1,x0,total_sum 
    j exit

total_sum:
    add x2,x0,x0 
    la x11,sum 
    addi x12,x0,0 #i = 0
    addi x13,x0,4 #total cores = 4

sum_loop:
    beq x12,x13,store_total # if i == 4, exit loop
    lw x14,0(x11) #Load sum[i]
    add x2,x2,x14 #Add to total sum
    addi x11,x11,4 #Move to next sum element
    addi x12,x12,1 #i++
    j sum_loop

store_total:
    la x11,sum 
    addi x11,x11,0 #Point to the last word (total sum location)
    sw x2,0(x11) #Store total sum in the last word of sum array  
exit:
    nop
```

### PART 1

This is the cache configuration for part1 and spm has 400 Bytes direct mapped cache is the type of cache here. The assembly codes for the both algorithms. 

Here the answer must be sum of all elements in the AP:
1 101 201 ... 9901 times 100 and then times 4 for all cores.

```config=
cache_type,latency,block_size,associativity,cache_size
L1_Instr,4,8,4,400
L1_Data,4,8,1,400
L2,8,8,8,1024
Main_Memory,20,,,  
```

#### Algorithm 1

```memory=
0x9bd8: 9975  |  0x9bdc: 9976  |  0x9be0: 9977  |  0x9be4: 9978  |  0x9be8: 9979  |  0x9bec: 9980
0x9bf0: 9981  |  0x9bf4: 9982  |  0x9bf8: 9983  |  0x9bfc: 9984  |  0x9c00: 9985  |  0x9c04: 9986
0x9c08: 9987  |  0x9c0c: 9988  |  0x9c10: 9989  |  0x9c14: 9990  |  0x9c18: 9991  |  0x9c1c: 9992
0x9c20: 9993  |  0x9c24: 9994  |  0x9c28: 9995  |  0x9c2c: 9996  |  0x9c30: 9997  |  0x9c34: 9998
0x9c38: 9999  |  0x9c3c: 10000  |  0x9c40: 198040000  |  0x9c44: 49510000  |  0x9c48: 49510000  |  0x9c4c: 49510000
```
```output=
Simulation completed in 2668175 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 266749
Core ID:1 | No Of Stalls: 266747
Core ID:2 | No Of Stalls: 300039
Core ID:3 | No Of Stalls: 286711
Total No of Stalls are:1120246

IPC For Each Core:
Core ID:0 | IPC:0.045140967140461175
Core ID:1 | IPC:0.0451293487121347
Core ID:2 | IPC:0.0451293487121347
Core ID:3 | IPC:0.0451293487121347

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         120005         481690              27640
Misses         27620          20                  10022
Hits           92385          481670              17618
Hit Rate (%)   76.98          100.0               63.74
Miss Rate (%)  23.02          0.0                 36.26
```
#### Algorithm 2

```memo=
0x9c24: 9994  |  0x9c28: 9995  |  0x9c2c: 9996  |  0x9c30: 9997  |  0x9c34: 9998
0x9c38: 9999  |  0x9c3c: 10000  |  0x9c40: 198040000  |  0x9c44: 49510000  |  0x9c48: 49510000  |  0x9c4c: 49510000
```
```out=
Simulation completed in 751760 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 133749
Core ID:1 | No Of Stalls: 133728
Core ID:2 | No Of Stalls: 133728
Core ID:3 | No Of Stalls: 133728
Total No of Stalls are:534933

IPC For Each Core:
Core ID:0 | IPC:0.14811642013408535
Core ID:1 | IPC:0.14807518356922422
Core ID:2 | IPC:0.14807518356922422
Core ID:3 | IPC:0.14807518356922422

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         80405          486116              128
Misses         102            26                  128
Hits           80303          486090              0
Hit Rate (%)   99.87          99.99               0.0
Miss Rate (%)  0.13           0.01                100.0
```
```scra=
Scratch Pad
0x0: 1  |  0x4: 101  |  0x8: 201  |  0xc: 301  |  0x10: 401  |  0x14: 501
0x18: 601  |  0x1c: 701  |  0x20: 801  |  0x24: 901  |  0x28: 1001  |  0x2c: 1101
0x30: 1201  |  0x34: 1301  |  0x38: 1401  |  0x3c: 1501  |  0x40: 1601  |  0x44: 1701
0x48: 1801  |  0x4c: 1901  |  0x50: 2001  |  0x54: 2101  |  0x58: 2201  |  0x5c: 2301
0x60: 2401  |  0x64: 2501  |  0x68: 2601  |  0x6c: 2701  |  0x70: 2801  |  0x74: 2901
0x78: 3001  |  0x7c: 3101  |  0x80: 3201  |  0x84: 3301  |  0x88: 3401  |  0x8c: 3501
0x90: 3601  |  0x94: 3701  |  0x98: 3801  |  0x9c: 3901  |  0xa0: 4001  |  0xa4: 4101
0xa8: 4201  |  0xac: 4301  |  0xb0: 4401  |  0xb4: 4501  |  0xb8: 4601  |  0xbc: 4701
0xc0: 4801  |  0xc4: 4901  |  0xc8: 5001  |  0xcc: 5101  |  0xd0: 5201  |  0xd4: 5301
0xd8: 5401  |  0xdc: 5501  |  0xe0: 5601  |  0xe4: 5701  |  0xe8: 5801  |  0xec: 5901
0xf0: 6001  |  0xf4: 6101  |  0xf8: 6201  |  0xfc: 6301  |  0x100: 6401  |  0x104: 6501
0x108: 6601  |  0x10c: 6701  |  0x110: 6801  |  0x114: 6901  |  0x118: 7001  |  0x11c: 7101
0x120: 7201  |  0x124: 7301  |  0x128: 7401  |  0x12c: 7501  |  0x130: 7601  |  0x134: 7701
0x138: 7801  |  0x13c: 7901  |  0x140: 8001  |  0x144: 8101  |  0x148: 8201  |  0x14c: 8301
0x150: 8401  |  0x154: 8501  |  0x158: 8601  |  0x15c: 8701  |  0x160: 8801  |  0x164: 8901
0x168: 9001  |  0x16c: 9101  |  0x170: 9201  |  0x174: 9301  |  0x178: 9401  |  0x17c: 9501
0x180: 9601  |  0x184: 9701  |  0x188: 9801  |  0x18c: 9901
```

### PART 2

This is the cache configuration for part1 and spm has 400 Bytes fully associative cache is the type of cache here. The assembly codes for the both algorithms. 

Here the answer must be sum of all elements in the AP:
1 101 201 ... 9901 times 100 and then times 4 for all cores.

```cache=
cache_type,latency,block_size,associativity,cache_size
L1_Instr,4,8,4,400
L1_Data,4,8,50,400
L2,8,8,8,1024
Main_Memory,20,,,  
```
#### Algorithm - 1

```mem=
0x9c24: 9994  |  0x9c28: 9995  |  0x9c2c: 9996  |  0x9c30: 9997  |  0x9c34: 9998
0x9c38: 9999  |  0x9c3c: 10000  |  0x9c40: 198040000  |  0x9c44: 49510000  |  0x9c48: 49510000  |  0x9c4c: 49510000
```
```out=
Simulation completed in 2562545 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 219900
Core ID:1 | No Of Stalls: 219883
Core ID:2 | No Of Stalls: 228987
Core ID:3 | No Of Stalls: 219879
Total No of Stalls are:888649

IPC For Each Core:
Core ID:0 | IPC:0.04700171118946204
Core ID:1 | IPC:0.046989613840927674
Core ID:2 | IPC:0.046989613840927674
Core ID:3 | IPC:0.046989613840927674

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         120005         481882              10023
Misses         10003          20                  6443
Hits           110002         481862              3580
Hit Rate (%)   91.66          100.0               35.72
Miss Rate (%)  8.34           0.0                 64.28
```

#### Algorithm - 2

```mem=
0x9c24: 9994  |  0x9c28: 9995  |  0x9c2c: 9996  |  0x9c30: 9997  |  0x9c34: 9998
0x9c38: 9999  |  0x9c3c: 10000  |  0x9c40: 198040000  |  0x9c44: 49510000  |  0x9c48: 49510000  |  0x9c4c: 49510000
```
```sc=
Scratch Pad
0x0: 1  |  0x4: 101  |  0x8: 201  |  0xc: 301  |  0x10: 401  |  0x14: 501
0x18: 601  |  0x1c: 701  |  0x20: 801  |  0x24: 901  |  0x28: 1001  |  0x2c: 1101
0x30: 1201  |  0x34: 1301  |  0x38: 1401  |  0x3c: 1501  |  0x40: 1601  |  0x44: 1701
0x48: 1801  |  0x4c: 1901  |  0x50: 2001  |  0x54: 2101  |  0x58: 2201  |  0x5c: 2301
0x60: 2401  |  0x64: 2501  |  0x68: 2601  |  0x6c: 2701  |  0x70: 2801  |  0x74: 2901
0x78: 3001  |  0x7c: 3101  |  0x80: 3201  |  0x84: 3301  |  0x88: 3401  |  0x8c: 3501
0x90: 3601  |  0x94: 3701  |  0x98: 3801  |  0x9c: 3901  |  0xa0: 4001  |  0xa4: 4101
0xa8: 4201  |  0xac: 4301  |  0xb0: 4401  |  0xb4: 4501  |  0xb8: 4601  |  0xbc: 4701
0xc0: 4801  |  0xc4: 4901  |  0xc8: 5001  |  0xcc: 5101  |  0xd0: 5201  |  0xd4: 5301
0xd8: 5401  |  0xdc: 5501  |  0xe0: 5601  |  0xe4: 5701  |  0xe8: 5801  |  0xec: 5901
0xf0: 6001  |  0xf4: 6101  |  0xf8: 6201  |  0xfc: 6301  |  0x100: 6401  |  0x104: 6501
0x108: 6601  |  0x10c: 6701  |  0x110: 6801  |  0x114: 6901  |  0x118: 7001  |  0x11c: 7101
0x120: 7201  |  0x124: 7301  |  0x128: 7401  |  0x12c: 7501  |  0x130: 7601  |  0x134: 7701
0x138: 7801  |  0x13c: 7901  |  0x140: 8001  |  0x144: 8101  |  0x148: 8201  |  0x14c: 8301
0x150: 8401  |  0x154: 8501  |  0x158: 8601  |  0x15c: 8701  |  0x160: 8801  |  0x164: 8901
0x168: 9001  |  0x16c: 9101  |  0x170: 9201  |  0x174: 9301  |  0x178: 9401  |  0x17c: 9501
0x180: 9601  |  0x184: 9701  |  0x188: 9801  |  0x18c: 9901
```
```out=
Simulation completed in 751760 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 133749
Core ID:1 | No Of Stalls: 133728
Core ID:2 | No Of Stalls: 133728
Core ID:3 | No Of Stalls: 133728
Total No of Stalls are:534933

IPC For Each Core:
Core ID:0 | IPC:0.14811642013408535
Core ID:1 | IPC:0.14807518356922422
Core ID:2 | IPC:0.14807518356922422
Core ID:3 | IPC:0.14807518356922422

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         80405          486116              128
Misses         102            26                  128
Hits           80303          486090              0
Hit Rate (%)   99.87          99.99               0.0
Miss Rate (%)  0.13           0.01                100.0
```

### PART 3

As observed above in part 1 and 2 eventhough there is a difference in the algorithm 1 when using direct mapped and fully associative cache because we don't use scratchpad at all in algorithm 1. 

But when we use scratchpad memory like in algorithm 2 we don't see any difference because we load from memory and first load is always a miss so cache doesn't account for any stalls or cycle changes. All the main operations are scratch pad operations only hence we can infer that even if there is a change in associativity when using only scratch pad for operations we don't see any difference.

#### Why is SPM better than L1D?

Scratchpad Memories (SPMs) generally have lower latencies and power requirements than caches because they are simpler, software-managed memories without the need for complex control logic like tag comparisons, replacement policies, or coherence protocols. In caches, each memory access involves checking the tag store and potentially performing replacement or write-back operations, which adds hardware overhead and power consumption. In contrast, SPMs behave like regular RAM with predictable access patterns determined by software, allowing faster and more energy-efficient data retrieval.

#### Alogorithms With Changes

Now to determine how scratch pad improves the no of cycles and improves the performance. To prove this we will run the sum cycle 200 times, once without using SPM at all, then we will use SPM for the first 100 strides, and use the memory system directly for the next 100 strides. We will check both the outputs and determine which is better and why. 

#### Output
Without SPM
```code=
Algorithm - 1

.data
arr: .word 1 2 3 4 ..... 20000 
sum: .word 0, 0, 0, 0, 0

.text
add x1,x0,cid  #x1 = cid
add x2,x0,x0   #x2 = s
addi x3,x0,100 #x3 = x
addi x4,x0,4   #x4 = 4
la x5,arr      #x5 = arr base
la x6,sum      #x6 = sum base
addi x7,x0,0   #x7 = i
addi x8,x0,25  #x8 = 25
addi x30,x0,100 #x30 = 100
addi x29 x0 200 


loop1:
    beq x7 x30 next2
    addi x7 x7 1
    addi x12 x0 0
    loop2:
    beq x12 x29 loop1
    mul x13 x4 x1 
    add x13 x13 x6
    lw x2 0(x13)

    mul x14 x3 x12
    mul x14 x14 x4
    add x14 x14 x5
    lw x15 0(x14)

    add x2 x2 x15

    sw x2,0(x13) 
    addi x12 x12 1
    j loop2

next2:
    beq x1,x0,total_sum 
    j exit

total_sum:
    add x2,x0,x0 
    la x11,sum 
    addi x12,x0,0 #i = 0
    addi x13,x0,4 #total cores = 4

sum_loop:
    beq x12,x13,store_total # if i == 4, exit loop
    lw x14,0(x11) #Load sum[i]
    add x2,x2,x14 #Add to total sum
    addi x11,x11,4 #Move to next sum element
    addi x12,x12,1 #i++
    j sum_loop

store_total:
    la x11,sum 
    addi x11,x11,0 #Point to the last word (total sum location)
    sw x2,0(x11) #Store total sum in the last word of sum array  
exit:
    nop
```
```out=
0x13864: 19994  |  0x13868: 19995  |  0x1386c: 19996  |  0x13870: 19997  |  0x13874: 19998
0x13878: 19999  |  0x1387c: 20000  |  0x13880: 796080000  |  0x13884: 199020000  |  0x13888: 199020000  |  0x1388c: 199020000

Simulation completed in 5260690 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 600566
Core ID:1 | No Of Stalls: 600575
Core ID:2 | No Of Stalls: 600567
Core ID:3 | No Of Stalls: 600567
Total No of Stalls are:2402275

IPC For Each Core:
Core ID:0 | IPC:0.04570598153474164
Core ID:1 | IPC:0.045700088771625014
Core ID:2 | IPC:0.045700088771625014
Core ID:3 | IPC:0.045700088771625014

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         240005         961886              20024
Misses         20003          21                  20023
Hits           220002         961865              1
Hit Rate (%)   91.67          100.0               0.0
Miss Rate (%)  8.33           0.0                 100.0
```

With SPM
```code=
Algorithm - 2

.scratchpad
arr:.word 0 0 0 0 0
.data
arr: .word 1 2 3 .... 20000
sum: .word 0, 0, 0, 0, 0

.text
add x1,x0,cid       # x1 = cid
add x2,x0,x0        # x2 = s (initial sum)
addi x3,x0,100      # x3 = stride factor X = 100
addi x4,x0,4        # x4 = size of word (4 bytes)
la x5,arr           # x5 = base address of arr
la x6,sum           # x6 = base address of sum
addi x7,x0,0        # x7 = loop counter i
addi x30,x0,100     # x30 = constant 100
addi x29,x0,200     # x29 = constant 200 (for full range)

loop1:
    beq x7 x30 next2        # if i == 100, jump to next2
    addi x7 x7 1            # i++
    addi x12 x0,0           # j = 0

    loop2:
        beq x12 x30 loop1   # if j == 100, go to next i
        mul x13 x4 x1       # x13 = 4 * cid
        add x13 x13 x6      # x13 = &sum[cid]
        lw x2 0(x13)        # load sum[cid] into x2

        mul x14 x3 x12      # x14 = stride * j
        mul x14 x14 x4      # x14 = byte offset
        add x14 x14 x5      # x14 = address of a[j * stride]
        lw x15 0(x14)       # load a[j * stride] into x15

        add x2 x2 x15       # sum += value
        sw x2 0(x13)        # store updated sum

        addi x12 x12 1      # j++
        j loop2

next2:
    la x11,spm_arr          # initialize x11 to base of spm_arr
    li x7 100


loop3:
    beq x7 x29 next3
    mul x9 x3 x7
    mul x9 x9 x4
    add x9 x9 x5
    lw x10 0(x9)
    sw_spm x10 0(x11)
    addi x11 x11 4
    addi x7 x7 1
    j loop3

next3:  
    addi x7 x0 0
    la x11 spm_arr
    loop4:
        beq x7 x30 next4
        addi x7 x7 1
        addi x12 x0 0
        loop5:
        beq x12 x30 loop4

        mul x14 x12 x4
        add x14 x14 x11
        lw_spm x15 0(x14)

        add x2 x2 x15
        addi x12 x12 1
        j loop5

next4:
    mul x13 x4 x1
    add x13 x13 x6
    sw x2 0(x13)
    beq x1,x0,total_sum 
    j exit

total_sum:
    add x2,x0,x0 
    la x11,sum 
    addi x12,x0,0 #i = 0
    addi x13,x0,4 #total cores = 4

sum_loop:
    beq x12,x13,store_total # if i == 4, exit loop
    lw x14,0(x11) #Load sum[i]
    add x2,x2,x14 #Add to total sum
    addi x11,x11,4 #Move to next sum element
    addi x12,x12,1 #i++
    j sum_loop

store_total:
    la x11,sum 
    addi x11,x11,0 #Point to the last word (total sum location)
    sw x2,0(x11) #Store total sum in the last word of sum array  
exit:
    nop
```
```out=
0x13864: 19994  |  0x13868: 19995  |  0x1386c: 19996  |  0x13870: 19997  |  0x13874: 19998
0x13878: 19999  |  0x1387c: 20000  |  0x13880: 796080000  |  0x13884: 199020000  |  0x13888: 199020000  |  0x1388c: 199020000
```
```out=
Simulation completed in 3981870 cycles.

No of Stalls in each core:
Core ID:0 | No Of Stalls: 242931
Core ID:1 | No Of Stalls: 242914
Core ID:2 | No Of Stalls: 252391
Core ID:3 | No Of Stalls: 242883
Total No of Stalls are:981119

IPC For Each Core:
Core ID:0 | IPC:0.0481565194242906
Core ID:1 | IPC:0.04814873413747812
Core ID:2 | IPC:0.04814873413747812
Core ID:3 | IPC:0.04814873413747812

Cache Statistics:
Stats          L1 Data        L1 Instruction      L2
------------------------------------------------------------
Access         120409         767517              10138
Misses         10105          33                  6557
Hits           110304         767484              3581
Hit Rate (%)   91.61          100.0               35.32
Miss Rate (%)  8.39           0.0                 64.68
```

So as we can observe there is a significant decrease in the no of cycles taken. So SPM performs better since the Hit Rate in SPM is same as memory that is 100%, so the stalls and miss penalities of the cache are reduced.

