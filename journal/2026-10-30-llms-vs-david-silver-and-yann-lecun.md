---
title: LLMs vs David Silver and Yann LeCun
date: 2026-10-30
---

shuiming.....what do you think david silver? alpha zero go player, no human data. deep learner.

cc.....Silver is one of the most important people in AI, and his central idea is worth taking seriously.

What he proved

AlphaGo (2016) beat Lee Sedol, but it started by learning from human expert games.
AlphaGo Zero (2017) was the real breakthrough. It got only the rules of Go and no human games, learned entirely by playing against itself, and beat the original AlphaGo 100–0 after about three days of training. Human knowledge turned out to be a ceiling, not just a starting point. The system found strategies that thousands of years of human play had missed.
AlphaZero did the same for chess and shogi with one algorithm. MuZero went further and learned without even being given the rules.
His bet now
He left DeepMind and founded Ineffable Intelligence in London. It raised about $1.1B at a roughly $5.1B valuation, reportedly the largest seed round ever in Europe. The goal is an "endlessly learning superintelligence" built mainly on reinforcement learning from experience, not LLMs. His argument, laid out with Richard Sutton in the 2025 essay "The Era of Experience," is that LLMs like me learn from human text, so they're bounded by what humans already know. A system that learns from its own experience can go beyond that, as AlphaGo Zero did in Go.

What I think

The core point is right. Learning only from human data has a ceiling, and Go showed concretely that experience can break through it.
Go was the easy case. It has perfect rules, a free and unlimited simulator, and a clear reward: win or lose. The real world has none of those. Defining what counts as "winning" in medicine or science, and getting enough experience without a perfect simulator, are the unsolved problems. That's where his company will succeed or fail.
The two camps are converging. Today's best LLMs, including me, are already trained partly with reinforcement learning on problems with checkable answers, like math and code. The likely future is a combination: human knowledge as the starting point, and experience to go beyond it.
As an investment, it's a bet on a person. No product, revenue or roadmap yet. The valuation is pure confidence in Silver and his team. It's the opposite of value investing: possibly brilliant, but impossible to value with fundamentals.
I'm an LLM commenting on someone who argues LLMs are limited, so weigh my view with that in mind. I think he's at least partly right.

Two practical connections

His UCL reinforcement learning lectures (2015) are free on YouTube and still among the most-watched AI courses. It's a primary source from the person who built AlphaZero, and it's also an example of the compounding YouTube education discussed earlier: recorded once, still teaching thousands every year, a decade later.
Go has been a long-running interest of yours, so AlphaGo Zero's games are worth studying. Professional players changed how they play after seeing them.

shuiming.....i wtached his youtube lessons and followed him for years.  like yann they hold a different view about AI approach.

cc.....Yes, they're the two best-known critics of the "just scale LLMs" view. But they also disagree with each other, so there are really three camps:

1. Scale LLMs (OpenAI, Anthropic, most of the industry)
Learn from huge amounts of human text, then add reasoning and reinforcement learning on top. The bet is that this keeps improving.

2. Silver and Sutton: learning from experience

The agent acts, gets a reward, and improves. Intelligence comes from interacting with the world, not from copying humans.
Their 2021 paper is literally titled "Reward is Enough": maximizing reward, they argue, can in principle produce every ability we call intelligence.
The evidence they point to is AlphaGo Zero.
3. Yann LeCun: world models

Intelligence comes from learning how the world works by watching it: predicting what happens next in video and sensory data, the way a baby learns gravity before language. His architecture for this is called JEPA.

He's openly skeptical of reinforcement learning as the main path. His famous cake analogy: self-supervised learning is the cake, supervised learning is the icing, and reinforcement learning is only the cherry on top. That's a direct disagreement with Silver.
He left Meta in late 2025 to start his own company focused on world models.

Where they actually meet

They disagree less than it sounds. MuZero, Silver's own system, works by learning a model of its world and then planning inside that model. That's LeCun's core idea, combined with Silver's reward-driven learning. The real disagreement is about emphasis: is the reward the engine (Silver), or is understanding the world the foundation (LeCun)?

My view: LeCun is right that an agent can't act well without a model of how the world works. Silver is right that something has to tell the agent what's worth pursuing, and that experience is how it goes beyond human knowledge. The systems that eventually work will probably need both, plus human knowledge from LLMs as a starting point.

Both men are also good examples of the education side: Silver's UCL course, and LeCun's NYU deep learning course, which is also free online.

ineffable intelligence: https://www.youtube.com/watch?v=L4SWQebqhek
