---
title: the magic of c
date: 2026-09-27
---

```c
#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c pattern < some_text_file

//K&R2 section 5.10: find -- print every input line that contains the
//pattern given as the program's first command-line argument.
//
//argc = how many words were typed on the command line, program name
//included; argv[] = those words, as strings. For `./cc-c 龙`:
//    argc    == 2
//    argv[0] == "./cc-c"
//    argv[1] == "龙"
//So "exactly one pattern given" is argc == 2, and the pattern is argv[1].
//
//strstr(s, t) (from <string.h>) returns a pointer to the first place t
//occurs inside s, or NULL if it doesn't occur at all.
//
//Fixed from the book's text, same as the section 5.6 program:
//
//1. getline() renamed my_getline() -- modern <stdio.h> already declares
//   a different getline(), so the book's name collides.
//
//2. `main(int argc, ...)` with no return type was legal in 1988 C
//   ("implicit int") but isn't anymore; now `int main`.
//
//3. The book's /* find: ... */ comment turned into // -- a /* */
//   comment inside this block would break it when it's archived later.
//
//main returns `found`, the number of matching lines. The shell can
//see it with `echo $?` right after running -- a program's return
//value from main is its "exit status".
#define MAXLINE 10000

int my_getline(char *line, int max);

//find:  print lines that match pattern from 1st arg
int main(int argc, char *argv[])
{
    char line[MAXLINE];
    int found = 0;

    if (argc != 2)
        printf("Usage: find pattern\n");
    else
        while (my_getline(line, MAXLINE) > 0)
            if (strstr(line, argv[1]) != NULL) {
                printf("%s", line);
                found++;
            }
    return found;
}

//my_getline: read one line (including '\n') into s, return its length
//(the pointer-walking version from exercise 5-6)
int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c 咎 < zhouyi.txt
元亨 无交害 匪咎 艱則无咎 大車以載 有攸往 公用亨于天子 小人弗克 匪其彭 厥孚交如 威如 吉 自天祐之 吉无不利
   - **匪咎 (fěi jiù):** "Not a mistake."
   - **艱則无咎 (jiān zé wú jiù):** "In difficulty, there is no blame."
   - **无咎 (wú jiù):** "No blame."
   - **无咎 (wú jiù):** "No blame."
6. **上九：有孚于飲酒，无咎，濡其首，有孚失是。**
   - **无咎 (wú jiù):** No blame.
2. **六二：過其祖，遇其妣；不及其君，遇其臣；无咎。**
4. **九四：无咎，弗過遇之。往厲必戒，勿用永貞。**
   - **无咎 (wú jiù)**: No blame.
   - **无咎 (wú jiù)**: No blame.
1. **初九：不出戶庭，无咎。**
3. **六三：不節若，則嗟若，无咎。**
5. **九五 (Jiǔ wǔ)**: 渙汗其大號，渙王居，无咎。
6. **上九 (Shàng jiǔ)**: 渙其血，去逖出，无咎。
**九二：巽在床下，用史巫紛若，吉，无咎。**
**"初九：遇其配主，雖旬无咎，往有尚。"**
- **雖旬无咎 (Suī xún wú jiù):** Although it takes ten days, there is no blame.
**"九三：豐其沛，日中見沬，折其右肱，无咎。"**
- **无咎 (Wú jiù):** No blame or fault.
**初六 (Chū Liù):** 鴻漸于干，小子厲，有言，无咎。
**六四 (Liù Sì):** 鴻漸于木，或得其桷，无咎。
**艮其背，不獲其身，行其庭，不見其人，无咎。**
- **无咎 (wú jiù)**: No blame.
**初六：艮其趾，无咎，利永貞。**
- **无咎 (wú jiù)**: No blame.
**六四：艮其身，无咎。**
- **无咎 (wú jiù)**: No blame.
**上六：震索索，視矍矍，征凶。震不于其躬，于其鄰，无咎。婚媾有言。**
#### 初六：鼎顛趾，利出否，得妾以其子，无咎。
- **无咎 (wú jiù)**: No blame.
2. **六二：巳日乃革之，征吉，无咎。**
4. **六四：井甃，无咎。**
- **困: 亨，貞，大人吉，无咎，有言不信。**
2. **九二：困于酒食，朱紱方來，利用享祀，征凶，无咎。**
2. **九二：孚乃利用禴，无咎。**
4. **六四：王用亨于岐山，吉无咎。**
- **初六：有孚不終，乃亂乃萃，若號一握為笑，勿恤，往无咎。**
- **六二：引吉，无咎，孚乃利用禴。**
- **六三：萃如，嗟如，无攸利，往无咎，小吝。**
- **九四：大吉，无咎。**
- **九五：萃有位，无咎。匪孚，元永貞，悔亡。**
- **上六：齎咨涕洟，无咎。**
**Text:** 包有魚，无咎，不利賓。
**Text:** 臀无膚，其行次且，厲，无大咎。
**Text:** 姤其角，吝，无咎。
1. **初九：壯于前趾，往不勝為咎。**
3. **九三：壯于頄，有凶。君子夬夬，獨行，遇雨，若濡，有慍，无咎。**
5. **九五：莧陸夬夬，中行无咎。**
   - **Text:** 利用為大作，元吉，无咎。
   - **Text:** 益之用凶事，无咎。有孚中行，告公用圭。
- **損: 有孚，元吉，无咎，可貞，利有攸往。曷之用，二簋可用享。**
1. **初九：巳事遄往，无咎，酌損之。**
4. **六四：損其疾，使遄有喜，无咎。**
6. **上九：弗損益之，无咎，貞吉，有攸往，得臣无家。**
- **无咎。**
### 初九 (chū jiǔ): 悔亡，喪馬勿逐，自復；見惡人无咎。
### 九二 (jiǔ èr): 遇主于巷，无咎。
### 九四 (jiǔ sì): 睽孤，遇元夫，交孚，厲无咎。
### 六五 (liù wǔ): 悔亡，厥宗噬膚，往何咎。
**初六：晉如，摧如，貞吉。罔孚，裕无咎。**
**上九：晉其角，維用伐邑，厲吉无咎，貞吝。**
- **恆: 亨，无咎，利貞，利有攸往。**
- **Text:** 初九：履錯然，敬之无咎。
- **Text:** 上九：王用出征，有嘉折首，獲匪其醜，无咎。
- **六四：樽酒簋貳，用缶，納約自牖，終无咎。**
- **九五：坎不盈，祗既平，无咎。**
- **藉用白茅，无咎。**
- **枯楊生華，老婦得士夫，无咎无譽。**
- **過涉滅頂，凶，无咎。**
4. **六四：顛頤，吉，虎視眈眈，其欲逐逐，无咎。**
**九四：可貞，无咎。**
- **无咎 (Wú jiù)**: No blame.
- **復: 亨。出入无疾，朋來无咎。反復其道，七日來復，利有攸往。**
3. **六三：頻復，厲无咎。**
**3. 六三：剝之，无咎。**
**上九：白賁，无咎。**
1. **初九：屨校滅趾，无咎。**
2. **六二：噬膚滅鼻，无咎。**
3. **六三：噬臘肉，遇毒；小吝，无咎。**
5. **六五：噬乾肉，得黃金，貞厲，无咎。**
- **Text:** 童觀，小人无咎，君子吝。
- **Text:** 觀我生，君子无咎。
- **Text:** 觀其生，君子无咎。
   - **Text:** 甘臨，无攸利。既憂之，无咎。
   - **Text:** 至臨，无咎。
   - **Text:** 敦臨，吉无咎。
- **Text:** 幹父之蠱，有子，考无咎，厲終吉。
- **Text:** 幹父之蠱，小有悔，无大咎。
- **元亨利貞，无咎 (yuán hēng lì zhēn, wú jiù)**: Great success, beneficial to be steadfast and upright, no blame.
- **隨有獲，貞凶。有孚在道，以明，何咎 (suí yǒu huò, zhēn xiōng. yǒu fú zài dào, yǐ míng, hé jiù)**:
  - **何咎 (hé jiù)**: What blame?
**上六：冥豫，成有渝，无咎。**
   - **匪咎 (Fěi Jiù)**: "No blame."
   - **艱則无咎 (Jiān Zé Wú Jiù)**: "In difficulty, there will be no blame."
   - **无咎 (Wú Jiù)**: "No blame."
   - **无咎 (Wú Jiù)**: "No blame."
- **初九：同人于門，无咎。**
4. **九四 (Jiǔ sì)**: 九四：有命，无咎，疇離祉。
- **Text:** 无平不陂，无往不復，艱貞无咎。勿恤其孚，于食有福。
- **素履，往无咎。**
2. **初九：復自道，何其咎，吉。**
5. **六四：有孚，血去惕出，无咎。**
- **Original Text**: 原筮元永貞，无咎。不寧方來，後夫凶。
   - **Text**: 有孚，比之，无咎。有孚盈缶，終來有它吉。
- **Judgment**: 貞，丈人，吉无咎。
  - **吉无咎 (Jí Wú Jiù)**: Good fortune without blame.
- **九二 (Jiǔ Èr)**: 在師中吉，无咎，王三錫命。
  - **无咎 (Wú Jiù)**: No blame.
- **六四 (Liù Sì)**: 師左次，无咎。
  - **无咎 (Wú Jiù)**: No blame.
- **六五 (Liù Wǔ)**: 田有禽，利執言，无咎。長子帥師，弟子輿尸，貞凶。
  - **无咎 (Wú Jiù)**: No blame.
1. **初九：需于郊。利用恆，无咎。**
**六四：括囊；无咎，无譽。**
- **无咎，无譽 (Wú jiù, wú yù)**: No blame, no praise. This implies keeping things contained and avoiding extremes.
4. **Line 3 (九三, Jiǔ Sān): 君子终日乾乾，夕惕若，厉，无咎 (Jūn Zǐ Zhōng Rì Qián Qián, Xī Tì Ruò, Lì, Wú Jiù)**
5. **Line 4 (九四, Jiǔ Sì): 或跃在渊，无咎 (Huò Yuè Zài Yuān, Wú Jiù)**
**1. 初九：无交害，匪咎，艱則无咎。**
**2. 九二：大車以載，有攸往，无咎。**
**4. 九四：匪其彭，无咎。**
```
