---
title: pointer is very interesting
date: 2026-09-19
---

shuiming...int a = 42 underneath, there is memory address assigned to it.?

cc...Yes, exactly. When the compiler processes int a = 42;, two things happen:

At compile time, it reserves 4 bytes (sizeof(int)) for a — either a fixed spot in the data/bss segment (if a is global/static) or an offset within whatever stack frame is active when that line runs (if a is local).

At runtime, that reservation becomes a real address in the process's virtual address space, and the bit pattern for 42 gets written into those 4 bytes.

&a is literally "tell me that address." a by itself means "go read the 4 bytes at that address and interpret them as an int." Let's look at the actual bytes sitting there.

shuming...so we are using a = 42 , b = 98 as assignment in other languages,  we just assume it works, and didn't dig deep into its roots.

cc...That's exactly the right thing to notice, and it's the whole reason working through K&R2 at this level of depth pays off — most languages are specifically designed to let you write a = 42 without ever thinking about bytes, addresses, or reservation. That's not laziness on your part, it's the language doing its job: Python, Java, JavaScript all interpose a runtime between your code and the machine precisely so you don't have to think about this.

But here's the layer that makes the C model worth having: that runtime hasn't eliminated addresses and pointers, it's just hidden them from you. In Python, a = 42 doesn't reserve a 4-byte box named a the way C does — it creates an integer object somewhere on the heap (with its own header, reference count, type tag, arbitrary precision digits...), and a is a name bound to a reference to that object — which, underneath the CPython interpreter, is a pointer. a = 98 doesn't overwrite those bytes in place; it points a at a different object entirely, possibly leaving the old 42 object to be garbage collected. Assignment in Python is "which object does this name point to," not "what bytes live at this fixed spot" — a fundamentally different mechanism than C's, but still built out of addresses and pointers one level down, in the interpreter's own C source.

So the honest picture isn't "C has pointers and other languages don't" — it's "every language is doing address-based memory manipulation somewhere; C just refuses to hide it from you." That's the trade C makes: no safety net, but nothing left mysterious either. Once you can read int a = 42; and see "4 bytes, this address, this bit pattern" without effort, you're equipped to reason about what's actually happening underneath assignment, references, and garbage collection in whatever higher-level language you touch next — you'll just usually choose not to think at that level, because most of the time you don't need to.

```c
/*
#include <stdio.h>
#define FOCUS 1
#define SQUARE(x) ((x) * (x))

int main() {
    int a = 5;
#ifdef FOCUS
    printf("Focus mode is ON. Square of %d is %d.\n", a, SQUARE(a));
#else
    printf("Focus mode is OFF.\n");
#endif
    return 0;
}


#include <stdio.h>

int main() {
    int a = 42; // 在 RAM 里放一个数字 42
    int b = 99;

    // %p 用于打印指针（地址）
    printf("变量 a 的值: %d, 变量 a 的内存地址: %p\n", a, (void*)&a);
    printf("变量 b 的值: %d, 变量 b 的内存地址: %p\n", b, (void*)&b);

    // 定义一个指针 p，把 a 的门牌号交给它
    int *p = &a;
    printf("指针 p 自己存放的内容（即a的地址）: %p\n", (void*)p);
    printf("顺着 p 找到的物理内存里的值: %d\n", *p);

    return 0;
}


#include <stdio.h>

int main() {
    int arr[] = {10, 20, 30};

    int *p = arr; // 指向数组第一个元素（门牌号 0 号位）

    printf("p 指向的值: %d, p 的内存地址: %p\n", *p, (void*)p);

    p++; // 指针加 1

    printf("p++ 后指向的值: %d, p 的内存地址: %p\n", *p, (void*)p);
    printf("两次地址相差的字节数: %ld\n", (char*)p - (char*)arr); // 强制转为char指针来计算字节差

    return 0;
}

#include <stdio.h>
#include <stdlib.h> // 需要 malloc

int main() {
    // 栈内存：系统自动分配，函数结束自动回收
    // gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c

    int stack_var = 5;
    printf("栈变量 stack_var 的地址: %p\n", (void*)&stack_var);

    // 堆内存：手动向操作系统申请 10 个 int 的空间
    int *heap_arr = (int*)malloc(10 * sizeof(int));
    if (heap_arr == NULL) return 1; // 无咎：必须检查申请是否成功

    printf("堆内存首地址 heap_arr 指向的地址: %p\n", (void*)heap_arr);

    // 写入数据
    heap_arr[0] = 100;
    printf("堆内存里的值: %d\n", heap_arr[0]);

    // 无咎原则：用完必须手动还给系统，否则这块物理内存就被你永久占用了
    free(heap_arr);
    heap_arr = NULL; // 防止悬垂指针（野指针）

    return 0;
}
*/

#include <stdio.h>

// 传值：把数据的副本传进来（相当于把仓库里的货复制了一份给函数）
void pass_by_value(int x) {
x = 999;
}

// 传址：把仓库的门牌号传进去，函数直接去原仓库改货
void pass_by_pointer(int *x) {
*x = 999;
}

int main() {
int a = 10;
int b = 10;

pass_by_value(a);
printf("传值后 a 的值: %d (没变)\n", a);

pass_by_pointer(&b); // 把 b 的真实物理地址交给函数
printf("传址后 b 的值: %d (变了！)\n", b);

return 0;
}


```
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
Focus mode is ON. Square of 5 is 25

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
变量 a 的值: 42, 变量 a 的内存地址: 0x7fff29d7d358
变量 b 的值: 99, 变量 b 的内存地址: 0x7fff29d7d35c
指针 p 自己存放的内容（即a的地址）: 0x7fff29d7d358
顺着 p 找到的物理内存里的值: 42

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
p 指向的值: 10, p 的内存地址: 0x7ffdce4c78cc
p++ 后指向的值: 20, p 的内存地址: 0x7ffdce4c78d0
两次地址相差的字节数: 4

win@DESKTOP-MEIH88T:~/webdev-projects$ // gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
-bash: //: Is a directory
win@DESKTOP-MEIH88T:~/webdev-projects$  gcc -Wall -Wextra ccc-c.c -o ccc-
c && ./ccc-c
栈变量 stack_var 的地址: 0x7ffd99f6aefc
堆内存首地址 heap_arr 指向的地址: 0x5c517617c420
堆内存里的值: 100

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c && ./ccc-c
ccc-c.c: In function ‘pass_by_value’:
ccc-c.c:84:24: warning: parameter ‘x’ set but not used [-Wunused-but-set-parameter]
   84 | void pass_by_value(int x) {
      |                    ~~~~^
传值后 a 的值: 10 (没变)
传址后 b 的值: 999 (变了！)
