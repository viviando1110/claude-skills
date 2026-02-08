# Contributing to Claude Skills

Thanks for wanting to contribute! Here's how to add a new skill or improve an existing one.

## Adding a New Skill

### 1. Create the Skill Directory

```bash
mkdir -p skills/your-skill-name
```

### 2. Write SKILL.md

Every skill needs a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: your-skill-name
description: >
  A clear description of what the skill does and WHEN to trigger it.
  Be specific about trigger conditions. Err on the side of "pushy" —
  Claude tends to under-trigger skills, so make the description
  clear about when this skill is relevant.
---
```

The body should contain:
- **Why** this approach works (theory/motivation)
- **How** to execute it (step-by-step process)
- **Examples** showing good vs. bad outputs
- **Edge cases** and important notes

### 3. Add a README.md

Include:
- What the skill does (human-readable)
- How to use it
- Example prompts and expected behavior
- Any dependencies or setup

### 4. Add Examples

Add test prompts to `examples/` so others can verify the skill works.

### 5. Submit a PR

- Keep PRs focused on one skill
- Include before/after examples showing the improvement
- Test with at least 3 different prompts

## Skill Design Principles

1. **Invisible to the user.** Skills should improve output quality without the user needing to know the skill exists. No "I'm now activating expert mode" theater.

2. **Explain the WHY.** Don't just list rules — explain why each instruction matters. Claude follows instructions better when it understands the reasoning.

3. **Use examples generously.** Show "BAD" and "GOOD" outputs side by side. Concrete examples beat abstract rules.

4. **Keep SKILL.md under 500 lines.** If you need more, use a `references/` directory with supporting files.

5. **Test with real prompts.** The best skills come from actual workflows that produced measurably better results.

## Improving Existing Skills

- Open an issue describing what's not working
- Include the prompt you used and the output you got
- Suggest specific changes and why they'd help
- PRs with before/after comparisons are especially welcome
