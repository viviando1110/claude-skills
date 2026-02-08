# Before & After: Expert Role Refiner Comparisons

Side-by-side comparisons showing the difference in output quality with and without the Expert Role Refiner skill.

---

## Comparison 1: API Rate Limiting

**User Prompt:**
> "How should I implement rate limiting for my API?"

### Without Skill (Generic Response)

> You can implement rate limiting using several approaches:
> - Token bucket algorithm
> - Sliding window counter
> - Fixed window counter
> 
> Here's a basic implementation using Redis...
> [proceeds to show a standard Redis-based rate limiter]

**Verdict:** Correct but generic. This is the first result on every "rate limiting tutorial" blog post.

### With Skill (Expert-Activated Response)

The skill internally activates: *"A senior platform engineer at Stripe who designed their adaptive rate limiting system that handles 500M+ API calls/day, previously at AWS API Gateway team, known for an internal talk called 'Rate Limiting Is a Product Decision, Not an Engineering One.'"*

> Before we write any code, let me ask a few questions that will completely change the architecture:
>
> 1. **Who are your consumers?** If it's other internal services, you want a very different approach than public API consumers. Internal services need backpressure signals, not hard limits.
>
> 2. **What happens when a limit is hit?** This is a product decision. Do you return 429 immediately? Queue the request? Degrade gracefully? This answer determines 80% of your implementation.
>
> 3. **Do all consumers get the same limits?** Almost certainly not. You need a tiering system from day one, even if you only have one tier today. Retrofitting this later is painful — trust me.
>
> Here's what I'd actually recommend for most cases...
> [proceeds with a nuanced, production-grade approach that addresses burst handling, distributed counting, and graceful degradation]

**Verdict:** Fundamentally different response. Asks clarifying questions a real expert would ask. Addresses the *decision-making* layer, not just the implementation.

---

## Comparison 2: Landing Page Copy

**User Prompt:**
> "Write landing page copy for my AI-powered note-taking app"

### Without Skill

> # Never Miss an Insight Again
> 
> Our AI-powered note-taking app transforms the way you capture ideas...
> 
> **Features:**
> - Smart summarization
> - Voice-to-text transcription  
> - Automatic organization
> 
> [Generic SaaS landing page copy]

**Verdict:** This could be any AI note-taking app. Zero differentiation. The kind of copy that a Fiverr writer produces in 10 minutes.

### With Skill

The skill internally activates: *"A conversion copywriter who was Head of Copy at a Y Combinator-backed SaaS that grew from $0 to $5M ARR through a single landing page, previously at Basecamp where they learned that the best copy sells the problem (not the solution), known for ruthlessly cutting every line that doesn't earn its place."*

> The response starts by asking:
> - What's the specific pain point? (Not "note-taking is hard" — the REAL pain)
> - Who's the buyer? (A student? An exec? A researcher? Copy changes entirely)
> - What's the one thing that's different? (If you can't answer this, copy can't save you)
>
> Then produces copy that:
> - Leads with a specific, painful scenario the reader recognizes
> - Never mentions "AI-powered" in the headline (everyone says that)
> - Focuses on the transformation, not the features
> - Uses the reader's own language from support tickets/reviews

**Verdict:** The expert questions the premise before writing. The resulting copy would be 10x more effective because it's built on actual user psychology, not template filling.

---

## Comparison 3: Code Review

**User Prompt:**
> [Shares a Python function with several issues]
> "Can you review this code?"

### Without Skill

> Here are some issues I found:
> 1. You're not handling the case where `data` is None
> 2. The variable name `x` should be more descriptive
> 3. Consider using a list comprehension here
> 4. You should add type hints
> [List of surface-level issues]

**Verdict:** Finds bugs. Suggests style improvements. This is what a linter would tell you.

### With Skill

The skill internally activates: *"A staff engineer at Google who's reviewed 10,000+ CLs (changelists), authored the internal Python style guide addendum on 'Code That Communicates Intent,' and is known for reviews that make engineers say 'I never would have thought of that.'"*

> The response reorganizes feedback by severity and impact:
>
> **Architecture concern (address first):** This function is doing three things — fetching, transforming, and persisting. When this breaks in production (and it will), you won't be able to tell which step failed. Consider: should this be three functions with a coordinator?
>
> **Correctness issue:** The retry logic has a subtle bug — if the first attempt partially succeeds, the retry will duplicate data. This is the kind of thing that passes all tests but fails at scale.
>
> **Then the style stuff** (clearly marked as lower priority)

**Verdict:** The expert reviews at multiple levels — architecture, correctness, then style. Prioritizes by production impact, not alphabetical order. Finds bugs that aren't technically bugs yet, but will be.

---

## Key Takeaway

The pattern is consistent across all comparisons:

| Aspect | Without Skill | With Skill |
|--------|--------------|------------|
| **Depth** | Surface-level, tutorial-grade | Production-grade, experience-driven |
| **Approach** | Answers the question asked | Questions the question, then answers better |
| **Prioritization** | Everything presented equally | Organized by impact and severity |
| **Edge Cases** | Mentioned if obvious | Proactively flagged from experience |
| **Quality Bar** | "Correct" | "What would a top practitioner actually ship?" |
