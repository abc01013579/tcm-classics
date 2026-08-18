---
title: test again
date: 2026-08-18
---

‘’’ #include <stdio.h>

int multiply(int a, int b) {
    int result = a * b;   // uses the copies of a and b
    return result;        // returns the result
}

int main() {
    int x = 3;
    int y = 4;
    int z = multiply(x, y);   // x and y are not modified
    
    printf("%d * %d = %d\n", x, y, z);
    return 0;
} ‘’’
