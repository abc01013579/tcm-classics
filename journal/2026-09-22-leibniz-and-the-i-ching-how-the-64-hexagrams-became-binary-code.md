---
title: Leibniz and the I Ching: How the 64 Hexagrams Became Binary Code
date: 2026-09-22
---

In April 1703 the Paris Mémoires de l'Académie Royale des Sciences published a short paper by Gottfried Wilhelm Leibniz titled "Explication de l'Arithmétique Binaire." In the margin of one diagram, Leibniz noted that the same number system he was describing — using only the digits 0 and 1 — had been discovered four thousand years earlier in China, by the legendary sage Fu Xi, and preserved in the 64 hexagrams of the I Ching.

The Jesuit letter of 1701
Leibniz had been working on binary representation for more than twenty years before he ever heard of the I Ching. As early as 1679 he had drafted a manuscript, De Progressione Dyadica, sketching the rules of base-2 arithmetic. In 1697 he had explained the system in a letter to Duke Rudolph August of Brunswick-Wolfenbüttel, even proposing a commemorative medal whose inscription would read imago creationis: God making "something out of nothing" by producing every integer from 0 and 1.

What he lacked was an interlocutor who could see what binary was for. He found one in Joachim Bouvet (1656–1730), a French Jesuit missionary who had spent more than a decade at the Kangxi Emperor's court in Beijing. Bouvet had been corresponding with Leibniz since 1697 about Chinese characters, mathematics, and philosophy. In a letter dated 4 November 1701, sent from Beijing, Bouvet enclosed a printed diagram: the Xiantian (Earlier Heaven) ordering of the 64 hexagrams attributed to Fu Xi.

The letter took nearly fourteen months to reach Leibniz in Hanover. When it arrived in early April 1703, he opened it with the instinct of a man who had been waiting for confirmation he could not have predicted.

What Leibniz saw at once
The Fu Xi sequence arranges the 64 hexagrams in a square grid of eight by eight, each hexagram built from six lines, each line either broken (yin, ⚋) or unbroken (yang, ⚊). What no Chinese commentator had ever quite framed in this way — and what leapt off the page at Leibniz — was that if you read yin as 0 and yang as 1, the diagram is a complete enumeration of the integers 0 through 63 in binary, read in a particular order.

Within days Leibniz had written back to Bouvet — and to Father Verjus in Paris, and to the President of the Académie. His letters from this period are almost giddy. He believed he had recovered the original meaning of an ancient text that the Chinese themselves had forgotten. "This shows," he wrote to Bouvet, "that the ancient Chinese have surpassed the modern in everything to do with philosophy."

The hexagrams as binary numbers
The translation is mechanical. Read each hexagram from bottom to top, the way the Chinese tradition counts the lines. Replace each broken line with 0 and each unbroken line with 1. The resulting six-bit string is the binary representation of an integer between 0 and 63.

Hexagram	Lines (bottom → top)	Binary	Decimal
2 — Kūn ䷁ (Earth)	⚋ ⚋ ⚋ ⚋ ⚋ ⚋	000000	0
24 — Fù ䷗ (Return)	⚊ ⚋ ⚋ ⚋ ⚋ ⚋	000001	1
7 — Shī ䷆ (The Army)	⚋ ⚊ ⚋ ⚋ ⚋ ⚋	000010	2
19 — Lín ䷒ (Approach)	⚊ ⚊ ⚋ ⚋ ⚋ ⚋	000011	3
…	…	…	…
43 — Guài ䷪ (Breakthrough)	⚊ ⚊ ⚊ ⚊ ⚊ ⚋	011111	31
1 — Qián ䷀ (Heaven)	⚊ ⚊ ⚊ ⚊ ⚊ ⚊	111111	63
The arrangement is mathematically complete: every six-bit binary number from 000000 to 111111 corresponds to exactly one hexagram. Nothing is repeated, nothing is missing. For Leibniz, this completeness was not a coincidence; it was evidence that whoever designed the hexagrams understood the same principle he had spent two decades working out alone.

The 1703 paper
Leibniz incorporated the Fu Xi diagram into the paper he submitted to the Paris Academy that spring. The full title is revealing: "Explication de l'Arithmétique Binaire, qui se sert des seuls caractères 0 et 1, avec des Remarques sur son utilité, et sur ce qu'elle donne le sens des anciennes figures chinoises de Fohy" — Explication of the Binary Arithmetic which uses only the characters 0 and 1, with remarks on its utility and on what it reveals of the meaning of the ancient Chinese figures of Fu Xi.

"What is amazing in this reckoning is that this arithmetic by 0 and 1 is found to contain the mystery of the lines of an ancient King and philosopher named Fohy, who is believed to have lived more than 4000 years ago, and whom the Chinese regard as the founder of their empire and their sciences."

— Leibniz, Explication de l'Arithmétique Binaire, 1703
Modern scholars are more cautious than Leibniz about the historical claim. The Fu Xi sequence is not strictly a counting system in any ancient Chinese text we possess; its mathematical interpretation was the Song dynasty philosopher Shao Yong's eleventh-century arrangement, not necessarily Fu Xi's intention. Leibniz, communicating across an enormous cultural gap, may have read more into the diagram than was originally there.

And yet the diagram is what he said it is. The correspondence holds. Whether the ancient Chinese intended binary arithmetic or merely a cosmological taxonomy, the structure they produced is identical to the one Leibniz produced from pure mathematics.

From Fu Xi to silicon
The binary system Leibniz formalized in 1703 sat dormant for two and a half centuries. It was George Boole's algebra (1854), Claude Shannon's master's thesis at MIT (1937), and the engineering decisions of John von Neumann and his colleagues in the 1940s that turned binary from a mathematical curiosity into the substrate of every digital computer on earth.

The line of descent from Fu Xi's hexagrams to your phone's processor is therefore neither a direct causal chain nor a poetic flourish. Leibniz did not borrow his binary system from China; he had it already. But he recognized the same system in the Chinese diagram, and he treated that recognition as significant. He was right to.

That a 3,000-year-old book of philosophy and divination should turn out to share its formal structure with the foundation of modern computing is the kind of fact that makes Jung's later category of synchronicity hard to dismiss. The same hexagrams that an ancient diviner cast with yarrow stalks now run, in a different form, beneath every search query and every line of code.

Frequently asked questions
Did Leibniz get the idea of binary numbers from the I Ching?
No. Leibniz had been developing binary arithmetic for more than twenty years before he saw the I Ching — his manuscript De Progressione Dyadica dates to 1679, and he described the system in a 1697 letter. When the Jesuit Joachim Bouvet sent him the Fu Xi diagram of the 64 hexagrams in 1701, Leibniz recognized his own binary system in it; he did not borrow it from China.

What year did Leibniz connect the I Ching to binary code?
The key year is 1703. Bouvet's letter enclosing the Fu Xi diagram was dated 4 November 1701 and reached Leibniz in Hanover in early April 1703. That spring Leibniz published "Explication de l'Arithmétique Binaire" in the Paris Académie's Mémoires, noting that the ancient Chinese figures of Fu Xi encoded the same arithmetic of 0 and 1.

How do the 64 hexagrams correspond to binary numbers?
Read each hexagram's six lines from bottom to top, replacing a broken line (yin) with 0 and an unbroken line (yang) with 1. The result is a six-bit binary number from 000000 to 111111 — the integers 0 to 63. In the Fu Xi (Xiantian) arrangement every six-bit value appears exactly once, so the diagram is a complete enumeration of 0–63 in binary.

Who sent Leibniz the I Ching diagram?
Joachim Bouvet (1656–1730), a French Jesuit missionary at the Kangxi Emperor's court in Beijing. He had corresponded with Leibniz since 1697 and enclosed the printed Fu Xi (Earlier Heaven) diagram of the 64 hexagrams in his letter of 4 November 1701.

Does the I Ching really contain binary code, or is that a myth?
The mathematical correspondence is real: the Fu Xi arrangement is structurally identical to a binary count from 0 to 63. But modern scholars caution that no ancient Chinese text treats the hexagrams as a counting system — the mathematical ordering comes from the Song-dynasty philosopher Shao Yong in the eleventh century, not necessarily Fu Xi's original intent. Leibniz may have read more arithmetic into the diagram than was first there, even though the formal structure genuinely matches.

note: this entry is a result of google search, not owner's own.

![Leibniz and the I Ching: How the 64 Hexagrams Became Binary Code](/static/journal/2026-09-22-leibniz-and-the-i-ching-how-the-64-hexagrams-became-binary-code.webp)
