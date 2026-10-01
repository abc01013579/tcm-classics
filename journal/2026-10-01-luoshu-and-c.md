---
title: luoshu and c
date: 2026-10-01
---

```c
#include <stdio.h>

#define SIZE 3

// 验证是否是幻方
int is_magic_square(int arr[SIZE][SIZE]) {
    int target_sum = 0;

    // 1. 计算第一行的和作为基准
    for (int j = 0; j < SIZE; j++) {
        target_sum += arr[0][j];
    }

    // 2. 检查每一行
    for (int i = 0; i < SIZE; i++) {
        int row_sum = 0;
        for (int j = 0; j < SIZE; j++) {
            row_sum += arr[i][j];
        }
        if (row_sum != target_sum) return 0; // 0 表示 False
    }

    // 3. 检查每一列
    for (int j = 0; j < SIZE; j++) {
        int col_sum = 0;
        for (int i = 0; i < SIZE; i++) {
            col_sum += arr[i][j];
        }
        if (col_sum != target_sum) return 0;
    }

    // 4. 检查主对角线 (左上到右下)
    int diag1_sum = 0;
    for (int i = 0; i < SIZE; i++) {
        diag1_sum += arr[i][i];
    }
    if (diag1_sum != target_sum) return 0;

    // 5. 检查副对角线 (右上到左下)
    int diag2_sum = 0;
    for (int i = 0; i < SIZE; i++) {
        diag2_sum += arr[i][SIZE - 1 - i];
    }
    if (diag2_sum != target_sum) return 0;

    return 1; // 1 表示 True
}

int main() {
    int luoshu[SIZE][SIZE] = {
        {4, 9, 2},
        {3, 5, 7},
        {8, 1, 6}
    };

    if (is_magic_square(luoshu)) {
        printf("Valid magic square!\n");
    } else {
        printf("Not a magic square.\n");
    }

    return 0;
}
```
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
Valid magic square!
