---
title: digit bit and bytes
date: 2026-09-24
---

shuiming.....bit digit bytes in details.

deepseek.....Let’s break down **bits**, **digits**, and **bytes** in detail, including how they relate to the memory units shown in commands like `free -h`.

---

## 1. Bit (Binary Digit)

- **Definition**: A **bit** is the smallest unit of data in computing.
- It is short for **binary digit** and can have only two possible values: **0** or **1**.
- All digital data (text, images, programs, memory contents) is ultimately stored and processed as a series of bits.

**Example**
The number `1011` is four bits. It represents the decimal number `11` (1×8 + 0×4 + 1×2 + 1×1).

---

## 2. Digit

In everyday language, a **digit** is a single symbol used to represent numbers (0–9 in decimal). In computing, we primarily use:

- **Binary digit (bit)** – base‑2, symbols 0 and 1.
- **Hexadecimal digit** – base‑16, symbols 0–9 and A–F (often used to represent groups of 4 bits compactly).
- **Decimal digit** – base‑10, symbols 0–9 (used when we talk about “kilobytes” = 1000 bytes, for example).

So when you hear “digit” in computing, it usually refers to a **bit** (binary digit) unless otherwise specified.

---

## 3. Byte

- **Definition**: A **byte** is a unit of digital information that consists of **8 bits** (in modern systems – historically, the size of a byte could vary, but 8 bits is now the universal standard).
- **Why 8 bits?**
  - Early computers used 6‑bit or 7‑bit codes (e.g., ASCII was originally 7 bits).
  - 8 bits became popular because it can represent 256 different values (2⁸ = 256), which is enough to encode all English letters, digits, punctuation, and many control characters.
  - It also aligns nicely with powers of two, which is fundamental in binary hardware.
- **Smallest addressable unit**: In most computer architectures, each **byte has its own unique memory address**. You cannot directly address a single bit – you must read/write entire bytes (or multiples of bytes) at once.
- **Abbreviation**: Usually denoted by uppercase **B** (as in KB, MB, GB, where B = byte). Be careful: lowercase **b** normally means **bit**.

**Examples of byte usage**
- One ASCII character (like `A`) typically occupies **1 byte** (8 bits).
- An image file of 5 MB is approximately 5 million bytes.

---

## 4. Units for Large Amounts: Decimal vs Binary Prefixes

When dealing with memory, storage, or file sizes, we use prefixes like kilo, mega, giga, tera, etc. But there are **two different systems** in use:

| Prefix | Decimal (SI) | Binary (IEC) | Factor (Decimal) | Factor (Binary) |
|--------|--------------|--------------|------------------|-----------------|
| Kilo   | KB           | KiB          | 10³ = 1,000      | 2¹⁰ = 1,024     |
| Mega   | MB           | MiB          | 10⁶ = 1,000,000  | 2²⁰ = 1,048,576 |
| Giga   | GB           | GiB          | 10⁹ = 1,000,000,000 | 2³⁰ = 1,073,741,824 |
| Tera   | TB           | TiB          | 10¹² = 1,000,000,000,000 | 2⁴⁰ = 1,099,511,627,776 |

- **Decimal (SI) prefixes** (KB, MB, GB) are based on powers of 10, used mainly by hard drive manufacturers and some software (like Windows incorrectly).
- **Binary (IEC) prefixes** (KiB, MiB, GiB) are based on powers of 2, used by most operating systems and technical tools to accurately describe memory sizes because computers work in binary.

**Important**
- **1 KiB = 1024 bytes**
- **1 KB = 1000 bytes**

The difference becomes significant at larger sizes:
1 GiB ≈ 1.074 GB (about 7.4% larger).

---

## 5. What `free -h` Uses

The command `free -h` (or `free --human`) displays memory sizes using **binary prefixes** (KiB, MiB, GiB) by default. That’s why you saw `5.7Gi`, `2.2Gi`, etc. If you want decimal (SI) units, you can use `free -h --si`, which will show `5.7G` (meaning 5.7 gigabytes = 5.7 × 10⁹ bytes) instead.

**From your earlier output**:
```
Mem:           5.7Gi       2.2Gi       1.3Gi       3.5Mi       2.3Gi       3.5Gi
```
- `5.7Gi` = 5.7 × 2³⁰ bytes = 6,118,115,328 bytes (approximately 6.12 GB decimal).
- `3.5Mi` = 3.5 × 2²⁰ bytes = 3,670,016 bytes.

So the memory values are shown in **gibibytes** and **mebibytes**, not gigabytes/megabytes.

---

## 6. Why This Matters

- **Memory capacities** (RAM, cache) are typically expressed in **GiB** or **MiB** because RAM is addressed in binary multiples (address lines correspond to powers of two).
- **Storage devices** (HDD, SSD) are often marketed using **GB** (decimal), which makes a 1 TB drive appear larger than it actually is when measured in TiB (a 1 TB drive is about 0.909 TiB).
- **Network speeds** are commonly measured in **bits per second** (Mbps, Gbps), not bytes. To convert: 8 bits = 1 byte, so a 100 Mbps connection transfers at most 12.5 MB per second (before overhead).

---

## Summary Table

| Term            | Meaning                                       | Size / Value         |
|-----------------|-----------------------------------------------|----------------------|
| **Bit**         | Single binary digit (0 or 1)                  | Smallest unit        |
| **Byte**        | 8 bits                                        | 1 B = 8 b            |
| **Kilobyte (KB)** | 1000 bytes (decimal)                        | 10³ bytes            |
| **Kibibyte (KiB)**| 1024 bytes (binary)                         | 2¹⁰ bytes            |
| **Megabyte (MB)** | 1,000,000 bytes                            | 10⁶ bytes            |
| **Mebibyte (MiB)**| 1,048,576 bytes                           | 2²⁰ bytes            |
| **Gigabyte (GB)** | 1,000,000,000 bytes                       | 10⁹ bytes            |
| **Gibibyte (GiB)**| 1,073,741,824 bytes                      | 2³⁰ bytes            |

---

## Final Word

- A **bit** is a single binary digit.
- A **byte** is 8 bits and is the standard unit of memory/storage.
- When you see **GiB, MiB, KiB**, it’s the **binary** (power‑of‑2) measurement – which is what `free -h` shows.
- The term “digit” in computing usually refers to a **binary digit** (bit), but can also mean a decimal digit in other contexts.
