# "You're a Software Engineer" Is Ruining Your AI Outputs

## How a 30-second mental trick activates a completely different Claude

---

I've been prompting LLMs for thousands of hours. Building skills, testing workflows, shipping tools.

And the single biggest quality jump I've ever found isn't a fancy framework. It's not chain-of-thought. It's not some 47-step mega-prompt.

It's *how you define the role.*

Most people get this catastrophically wrong.

---

## The Problem With Generic Roles

Here's what 99% of people type:

> "You are a software engineer. Help me optimize this function."

Sounds reasonable, right?

It's actually the worst thing you can do.

Here's why: **thousands of people prompted the exact same thing before you.** When you say "you're a software engineer," you're activating the most generic, averaged-out training signal possible. You're getting the median output of every "software engineer" interaction Claude has ever seen.

You're not getting an expert. You're getting a composite sketch.

It's like asking "a doctor" for medical advice vs. asking the head of cardiology at Johns Hopkins who spent 15 years researching exactly your condition. Same title. Completely different knowledge.

---

## The Cheat Code: Hyper-Specific Role Activation

I built a Claude Skill that goes absolutely hard on role definitions.

Instead of "you're a software engineer," it runs an internal loop that finds the *exact* top 0.1% specialist who would destroy your specific task.

The difference in output quality is... honestly kind of shocking.

Here's the mental model:

**Generic role** → activates the middle of the bell curve → averaged, safe, expected output

**Hyper-specific role** → activates the tail of the distribution → deep, nuanced, expert-level output

Same model. Same temperature. Same everything. Completely different results.

---

## What "Hyper-Specific" Actually Looks Like

This is the part where most guides fail. They tell you to "be specific" but never show you *how specific.*

Let me show you.

### ❌ BAD: Generic Role

> "You are an experienced backend developer."

This activates... nothing special. It's the default. You might as well not have said it.

### ✅ GOOD: Hyper-Specific Role

> "You are a staff engineer at Cloudflare who built the Workers runtime, debugged V8 isolate memory leaks in production at 3am during a major outage, and now consults on edge computing architecture for latency-sensitive financial trading applications."

Read that again. Feel the difference?

That's not a title. That's a *career trajectory.* It includes:

1. **A specific institution** (Cloudflare — implies scale, performance obsession)
2. **A signature accomplishment** (built Workers — not just used them, built them)
3. **Battle scars** (V8 memory leaks at 3am — they've seen real production pain)
4. **Current context** (latency-sensitive finance — they care about microseconds)

Every detail is doing work. Every detail primes a different region of knowledge.

---

## The Four Attributes That Matter

Through extensive testing, I've found four attributes that consistently produce the best role activations:

### 1. Specific Institution or Context

Not "a company." The *type* of company that implies the right experience.

- "at a FAANG company" → good
- "at Stripe's payment infrastructure team" → much better
- "at a Series A startup that went from 0 to $10M ARR" → different but equally powerful

The institution sets the *operating context.* Stripe implies correctness and financial rigor. A startup implies scrappiness and pragmatism. Choose based on what the task needs.

### 2. Signature Accomplishment

What makes this person the top 0.1%, not just "experienced"?

- "built distributed systems" → generic
- "designed the internal event sourcing framework that processes 2B events/day" → specific enough to activate real expertise

The accomplishment should be *directly relevant* to the task at hand.

### 3. Battle Scars

What problems have they personally debugged, shipped through, or failed at?

This is the secret weapon. Battle scars activate a completely different kind of knowledge — the stuff that doesn't make it into documentation or tutorials. The "I learned this the hard way at 3am" knowledge.

- "experienced with databases" → generic
- "spent a year migrating a 20TB Postgres cluster with zero downtime while the CEO was breathing down their neck" → now we're talking

### 4. Working Style

How do they think and communicate? This shapes the output's character.

- "known for unusually clear technical writing" → you get clear explanations
- "famous for saying 'the best code is no code'" → you get minimalist solutions
- "obsessive about the gap between 'works in a notebook' and 'works at scale'" → you get production-hardened advice

---

## Real Examples, Real Differences

Let me show you what this looks like in practice across different domains.

### Example: Optimizing a React Component

**Generic prompt:**
> "You're a frontend developer. Optimize this React component."

**What you get:** The usual suspects. `useMemo` here, `useCallback` there, maybe a `React.memo` wrapper. Fine. Correct. Boring. Every tutorial says the same thing.

**Refined role:**
> A principal frontend engineer at Vercel who co-authored key sections of the React Server Components RFC, previously led performance optimization at Instagram (reducing INP by 40% across the feed), specializes in reconciliation algorithm internals, and is known for solutions that are embarrassingly simple in hindsight.

**What you get now:** A fundamentally different response. This expert looks at your component through the lens of reconciliation cost. They question whether the component should exist at all. They might suggest moving the computation to the server. They propose architectural changes instead of micro-optimizations.

Same question. Completely different answer. The second one is what a real senior engineer at Vercel would actually tell you.

### Example: Writing a Cold Email

**Generic prompt:**
> "You're a sales expert. Write a cold outreach email."

**What you get:** A template. "I noticed your company is doing X... I wanted to reach out because..." Delete-on-sight material.

**Refined role:**
> A founding AE at a developer tools startup who personally closed the first 50 enterprise accounts by writing cold emails that averaged a 40% reply rate — their secret was treating every email like a piece of investigative journalism about the prospect's specific technical pain.

**What you get now:** The expert refuses to write a template. They ask about the recipient first. They want to see the prospect's GitHub, their blog posts, their conference talks. They produce something that reads like a thoughtful note from a peer, not a sales email.

### Example: Database Schema Design

**Generic prompt:**
> "You're a database expert. Design a schema for an events platform."

**What you get:** A nicely normalized schema. Primary keys, foreign keys, junction tables. Textbook correct, production-naive.

**Refined role:**
> A staff database engineer who spent 6 years at Timescale building time-series optimizations, previously scaled Ticketmaster's event catalog from 10M to 500M listings, and is known internally for a doc called "Every Schema Decision Is a Performance Decision You'll Live With for 5 Years."

**What you get now:** They ask about read/write ratios before writing a single line. They consider partitioning by date range. They design for the query patterns, not the data model. They warn you about the specific decisions that seem fine at 1M rows but become catastrophic at 100M.

---

## The "Top 0.1%" Quality Checkpoint

Here's the simplest version of this technique that you can use immediately, even without the full skill:

Before Claude writes its response, make it ask:

> "What would a top 0.1% person in this specific field think about this problem?"

That single question changes everything. It forces consideration of:
- Edge cases a generalist would miss
- Non-obvious approaches the asker didn't think to request
- Quality standards that separate "fine" from "exceptional"

You can use this as a system prompt addition right now:

```
Before responding, identify the specific type of top 0.1% expert 
who would nail this task. Not a generic title — a specific career 
trajectory with battle scars relevant to this exact problem. 
Then respond as that expert would.
```

That's it. Three sentences. Massive quality improvement.

---

## The Skill: Automating This Process

I packaged this entire workflow into a Claude Skill that does the refinement automatically.

When Claude has the skill loaded, here's what happens internally for every substantive task:

**Step 1: Task Decomposition**
Breaks down the real domain, sub-problem, and implicit quality criteria.

**Step 2: Expert Identification**
Asks: "If I could call ONE person on Earth who would destroy this task, who would they be?" Then defines them with all four attributes.

**Step 3: Refinement Loop**
Pressure-tests the expert: Is this specific enough? Do they have the right adjacent knowledge? Would a true 0.1% practitioner approach this differently?

**Step 4: Activate and Execute**
Adopts the expert as a lens. Thinks like them. Communicates like them. Applies their judgment. Uses their quality bar as a continuous checkpoint.

The entire process is invisible. The user just asks a question and gets a notably better answer. No "I'm now activating expert mode" theater.

---

## Why This Actually Works (The Training Data Argument)

LLMs are trained on internet text. That text contains a distribution of expertise levels:

- **The vast middle:** Tutorial-level content, Stack Overflow answers, generic blog posts
- **The tail:** Conference talks by principal engineers, research papers by domain experts, internal design docs that leaked, deep technical blog posts by practitioners

When you say "you're a software engineer," you're sampling from the middle. That's where most "software engineer" content lives.

When you define a hyper-specific expert, you're essentially constructing a *query* that points at the tail of the distribution. You're telling the model: "I want the kind of response that a person with THIS specific background would write."

It's not magic. It's just better retrieval from the model's training distribution.

---

## Common Mistakes

**Over-specifying for simple tasks.** If someone asks "what's the capital of France," you don't need a "top 0.1% geographer who specializes in European political boundaries." Scale the refinement to the complexity.

**Making up fake people.** The expert should be a plausible archetype, not a named real person. "A staff engineer at Cloudflare who built Workers" is great. "Kent C. Dodds" is not — you're now constrained to one person's specific opinions.

**Forgetting cross-domain knowledge.** The best experts aren't just deep — they have unusual cross-domain connections. A database expert who understands compiler optimizations. A marketer who groks developer psychology. The intersection is where the magic lives.

**Treating it as roleplay.** The expert is a *lens*, not a character. Claude isn't pretending to be someone else. It's using the expert definition to activate the most relevant knowledge patterns. It's still Claude — just Claude with a very powerful frame of reference.

---

## Get the Skill

The full skill is open source and ready to use:

→ [skills/expert-role-refiner/SKILL.md](../skills/expert-role-refiner/SKILL.md)

Drop it into a Claude Project, Claude Code, or paste it directly into a conversation.

Then try it on whatever you're working on right now.

I promise the output will feel different.

---

*If this was useful, the repo has more skills coming. Star it, contribute your own, or just steal the ideas and make better things.*
