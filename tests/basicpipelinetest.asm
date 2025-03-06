.data
label1: .word 100
label2: .word 200

.text
# Test la
la x1, label1       # x1 should be set to the address of label1
la x2, label2 