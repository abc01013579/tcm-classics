---
title: print our own hexagrams
date: 2026-09-27
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//compile with: gcc -Wall -Wextra hexagrams_big.c -o hexagrams_big
//run with:     ./hexagrams_big         all 64, four to a row
//         or:  ./hexagrams_big 30      just one hexagram, drawn large

//Draw the 64 hexagrams of the Zhouyi line by line, instead of printing
//the tiny one-character Unicode symbols ䷀ ... ䷿ (U+4DC0 + n - 1):
//
//    yang (1):  ━━━━━━━━━━━        yin (0):  ━━━━   ━━━━
//
//Each hexagram is stored as ONE 6-bit number -- yin/yang as 0/1:
//bit 0 is the bottom line (初), bit 5 the top line (上). Drawing it is
//bit-testing, the same idea as putbits(): (lines >> k) & 1 for each k.
//The Zhouyi counts lines from the bottom up but we print top-down, so
//the loop runs k = 5, 4, ..., 0.
//
//The table comes from yijing_app's yijing_core.py (HEXAGRAM_KEYS,
//listed bottom line first), checked two ways: all 64 values are
//different, and in King Wen order every even hexagram is the one
//before it turned upside down -- or its opposite, when turning it over
//changes nothing (乾/坤, 頤/大過, 坎/離, 中孚/小過).
//
//Example: 屯 (3) = 0x11 = 010001 -> lines from bottom: 1 0 0 0 1 0,
//i.e. 震 (thunder, 100) below and 坎 (water, 010) above.

static const unsigned char lines[64] = {
    0x3F, 0x00, 0x11, 0x22, 0x17, 0x3A, 0x02, 0x10,     //  1 -  8
    0x37, 0x3B, 0x07, 0x38, 0x3D, 0x2F, 0x04, 0x08,     //  9 - 16
    0x19, 0x26, 0x03, 0x30, 0x29, 0x25, 0x20, 0x01,     // 17 - 24
    0x39, 0x27, 0x21, 0x1E, 0x12, 0x2D, 0x1C, 0x0E,     // 25 - 32
    0x3C, 0x0F, 0x28, 0x05, 0x35, 0x2B, 0x14, 0x0A,     // 33 - 40
    0x23, 0x31, 0x1F, 0x3E, 0x18, 0x06, 0x1A, 0x16,     // 41 - 48
    0x1D, 0x2E, 0x09, 0x24, 0x34, 0x0B, 0x0D, 0x2C,     // 49 - 56
    0x36, 0x1B, 0x32, 0x13, 0x33, 0x0C, 0x15, 0x2A      // 57 - 64
};

static const char *names[64] = {
    "乾", "坤", "屯", "蒙", "需", "訟", "師", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "无妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
};

#define PER_ROW 4
#define CELL    16          //columns per hexagram: 11 for the bar + gap

#define YANG "━━━━━━━━━━━"
#define YIN  "━━━━   ━━━━"

void header(int n);
void draw_one(int n);

int main(int argc, char *argv[])
{
    int first, n, k;

    if (argc > 1) {                         //one hexagram, drawn large
        n = atoi(argv[1]);
        if (n < 1 || n > 64) {
            printf("usage: hexagrams_big [1-64]\n");
            return 1;
        }
        draw_one(n);
        return 0;
    }

    for (first = 1; first <= 64; first += PER_ROW) {
        for (n = first; n < first + PER_ROW; n++)
            header(n);
        putchar('\n');
        for (k = 5; k >= 0; k--) {          //top line first
            for (n = first; n < first + PER_ROW; n++)
                printf("%s     ", (lines[n-1] >> k) & 1 ? YANG : YIN);
            putchar('\n');
        }
        putchar('\n');
    }
    return 0;
}

//header:  print "n name" padded to CELL columns. A Chinese character
//is 3 UTF-8 bytes but takes 2 columns on screen, so the width on screen
//is (digits) + 1 space + (bytes / 3 * 2) -- not strlen().
void header(int n)
{
    int width;

    width = printf("%d ", n);                       //printf returns chars printed
    printf("%s", names[n-1]);
    width += strlen(names[n-1]) / 3 * 2;
    while (width++ < CELL)
        putchar(' ');
}

//draw_one:  one hexagram, with the line names beside each line
void draw_one(int n)
{
    static const char *pos[6] = { "初", "二", "三", "四", "五", "上" };
    int k, yang;

    printf("\n  第%d卦  %s\n\n", n, names[n-1]);
    for (k = 5; k >= 0; k--) {
        yang = (lines[n-1] >> k) & 1;
        printf("  %s    %s%s\n\n", yang ? YANG : YIN,
               k == 0 || k == 5 ? pos[k] : (yang ? "九" : "六"),
               k == 0 || k == 5 ? (yang ? "九" : "六") : pos[k]);
    }
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra hexagrams_big.c -o hexagrams_big
win@DESKTOP-MEIH88T:~/webdev-projects$  ./hexagrams_big 30

  第30卦  離

  ━━━━━━━━━━━    上九

  ━━━━   ━━━━    六五

  ━━━━━━━━━━━    九四

  ━━━━━━━━━━━    九三

  ━━━━   ━━━━    六二

  ━━━━━━━━━━━    初九

win@DESKTOP-MEIH88T:~/webdev-projects$  ./hexagrams_big 14

  第14卦  大有

  ━━━━━━━━━━━    上九

  ━━━━   ━━━━    六五

  ━━━━━━━━━━━    九四

  ━━━━━━━━━━━    九三

  ━━━━━━━━━━━    九二

  ━━━━━━━━━━━    初九

```
