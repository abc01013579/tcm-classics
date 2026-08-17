---
title: just a test
date: 2026-08-17
---

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/*

float fahr_to_celsius(float fahr);   //prototype: lets main() call fahr_to_celsius() before its definition below

int main()
{
    float fahr, lower, upper, step;

    lower = 0;
    upper = 300;
    step = -20;

    for (fahr = upper; fahr >= lower; fahr = fahr + step)
        printf("%3.0f %6.1f\n", fahr, fahr_to_celsius(fahr));

    return 0;
}

float fahr_to_celsius(float fahr)
{
    return (5.0 / 9.0) * (fahr - 32.0);
}
