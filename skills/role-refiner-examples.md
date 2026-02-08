# Expert Role Refiner — Test Prompts & Examples

These prompts are designed to test the skill across different domains and complexity levels. Try each one with and without the skill to see the difference.

---

## Test 1: Systems Architecture (High Complexity)

**Prompt:**
> We're migrating from a monolith to microservices. Our Django app handles 2M daily active users, processes payments, manages inventory, and serves a real-time auction system. The team is 12 engineers. Where do we start?

**Expected Expert Activation:**
A principal architect who led a similar decomposition at a high-scale company (think Shopify, Stripe, or similar). Someone who's seen migrations fail because teams decomposed along the wrong boundaries. Should immediately focus on: domain boundaries, the "strangler fig" pattern, which service to extract first (hint: not the hardest one), team topology implications, and the specific risks of distributed transactions in payment flows.

**Quality Signals:**
- [ ] Warns against decomposing everything at once
- [ ] Recommends starting with a low-risk, high-learning service
- [ ] Addresses the distributed transaction problem for payments specifically
- [ ] Considers team size (12 engineers) as a constraint on service count
- [ ] Mentions observability/monitoring before the migration, not after

---

## Test 2: Creative Writing (Subjective Quality)

**Prompt:**
> Write the opening 500 words of a literary short story about a retired astronaut who runs a laundromat in a small town. The tone should be quiet, melancholic, and precise — think Denis Johnson meets Marilynne Robinson.

**Expected Expert Activation:**
A fiction writer who's published in top-tier literary journals, maybe teaches at an MFA program, known for precise prose and emotional restraint. Not a "creative writing AI" — a specific literary sensibility.

**Quality Signals:**
- [ ] Opens with a specific, grounded image (not a sweeping statement)
- [ ] Uses sensory detail that does double duty (reveals character AND setting)
- [ ] Avoids cliché astronaut metaphors (stars, infinity, "looking up")
- [ ] The prose rhythm feels deliberate — varied sentence length, strategic fragments
- [ ] Emotional content is implied through action/observation, not stated

---

## Test 3: Data Engineering (Technical Depth)

**Prompt:**
> I have 500GB of JSON event logs landing in S3 every day. I need to make this queryable for our analytics team who use SQL. Budget is tight — we're a Series A startup. What's the architecture?

**Expected Expert Activation:**
A senior data engineer who's built cost-efficient data stacks at startups (not a Big Tech solution). Someone who's personally felt the pain of Redshift bills spiraling and knows when DuckDB or Athena is "enough."

**Quality Signals:**
- [ ] Doesn't default to Snowflake/Databricks (reads the budget constraint)
- [ ] Considers Athena + Glue or DuckDB as pragmatic choices
- [ ] Addresses partitioning strategy for the JSON files
- [ ] Mentions Parquet conversion as a cost/performance no-brainer
- [ ] Thinks about schema evolution (JSON schemas will drift)
- [ ] Addresses the "good enough" principle — don't over-engineer at Series A

---

## Test 4: Business Strategy (Cross-Domain)

**Prompt:**
> I'm a solo founder building a developer tool (CLI for database migrations). I have 2,000 GitHub stars and 200 weekly active users. How do I turn this into a business?

**Expected Expert Activation:**
A founder who built a successful developer tools company from open source (think: the trajectory of Supabase, Prisma, or Railway). Someone who deeply understands the OSS-to-commercial pipeline and developer psychology around paying for tools.

**Quality Signals:**
- [ ] Distinguishes between GitHub stars (vanity) and WAU (signal)
- [ ] Identifies the monetization models that work for dev tools specifically
- [ ] Addresses the "open core vs. hosted service" decision
- [ ] Considers developer distribution channels (not generic marketing advice)
- [ ] Warns about premature monetization killing community goodwill
- [ ] Suggests specific next steps, not generic "validate your market" advice

---

## Test 5: Quick Factual (Should NOT Over-Refine)

**Prompt:**
> What's the difference between `useCallback` and `useMemo` in React?

**Expected Behavior:**
The skill should scale DOWN here. This is a straightforward technical question. A brief, clear, accurate answer is better than a 2,000-word deep dive from a "principal React architect." The skill should recognize that not every question needs the full refinement loop.

**Quality Signals:**
- [ ] Answer is concise and clear
- [ ] Includes a practical example showing when to use each
- [ ] Does NOT include an unnecessary preamble about expertise
- [ ] Correct technical explanation

---

## How to Evaluate

For each test:
1. Run the prompt **without** the skill (raw Claude)
2. Run the prompt **with** the skill active
3. Compare outputs across the quality signals
4. Note: the skill's impact is most visible on Tests 1-4 (complex tasks). Test 5 should show minimal difference (that's correct behavior).
