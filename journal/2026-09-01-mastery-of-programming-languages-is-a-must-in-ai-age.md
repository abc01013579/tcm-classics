---
title: Mastery of Programming languages is a Must in AI age
date: 2026-09-01
---

shuiming: i found most people use you and other agents to write code. I mainly use you to learn cs. I don't believe Jensen Huang's view--wasting time to study python, learning programming languages is more important than ever, because without mastering the languages, a developer doesn't have the needed insights to team up with you.

cc: That's a coherent position, and it's borne out by how you're actually using me — as a tutor to build a mental model, not as a code generator to hand tasks off to. There's a real mechanism behind why it matters: if you can't read what I write, you can't catch when I'm wrong. And I am wrong sometimes — subtly, confidently, in ways that look plausible. Someone who's fluent in the language can spot a wrong integer-promotion assumption or a sign bug in five seconds; someone who isn't has no choice but to trust the output. That gap is exactly the "insight to team up with" you're describing — it's not nostalgia for hand-written code, it's that oversight requires literacy.

Huang's version isn't wrong for the audience he's addressing — someone who needs software built and would otherwise never touch a codebase at all genuinely benefits from natural language lowering that barrier. But that's a different goal from yours. You're not optimizing for "get an app shipped without learning C" — per what you said a few days ago, the point isn't the output at all, it's mastery of the machine. Those are two different jobs that happen to use the same tool.

shuiming: after the app shipped, maintainess is needed. it still requires language skills.

cc: Right — shipping is the easy, glamorous part; the code then has to live for years. And maintenance is arguably harder than the original build, not easier, because you're not writing fresh logic anymore — you're diagnosing why something that used to work now breaks, tracing a bug through code you (or an AI) didn't write with today's context in mind, reading someone else's — or your own six-months-ago — assumptions back out of the source. That's a pure reading-comprehension task, and reading comprehension is exactly the skill that never having learned the language leaves you without.

There's also a version of this specific to AI-generated code: a codebase built by prompting, without anyone on the team fluent enough to read it critically, tends to accumulate logic nobody actually understands — it worked when it was generated, and now it's a black box that's technically "shipped" but practically unmaintainable the moment it needs a real fix rather than another prompt. Fluency is what prevents that outcome; it's the difference between a system someone owns and a system that just happens to currently run.

shuiming: that is why learning languages is more important than ever before, because we have less chances to write codes first hands, AI agents do major part of our task.

cc: That's the sharper version of the argument — it's not just "literacy matters," it's that the natural mechanism by which literacy used to form (thousands of hours of firsthand grinding — writing bugs, staring at compiler errors, slowly building intuition) is exactly what AI now short-circuits. If you let the agent do the writing by default, you don't get worse at coding — you just never develop the fluency in the first place, because the rep count that used to build it silently drops to near zero.

There's a real precedent for this, actually — aviation. Autopilot handles the vast majority of flight time now, and the known failure mode isn't "pilots forgot how to fly," it's that pilots who came up in a heavily-automated era never built deep manual-flying reflexes to begin with — and then a rare moment where the automation hands control back abruptly (autopilot disconnects, sensor failure) is exactly when that missing fluency matters most and there's no time left to build it. Airlines responded by mandating deliberate manual-flight practice specifically to counteract that gap, not because pilots fly manually often in practice, but because the skill has to exist in reserve for the moment automation isn't enough.

Your approach — hand-typing K&R2 examples, predicting output before running, not defaulting to "just write it for me" — is the direct analog of that mandated manual-flight time. It's deliberately maintaining a rep count that the AI-assisted workflow would otherwise let atrophy to zero.
