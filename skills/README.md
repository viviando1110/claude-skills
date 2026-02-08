# 🧠 Claude Skills

A curated collection of high-performance [Claude Skills](https://docs.anthropic.com/en/docs/build-with-claude/projects) — reusable prompt-engineering modules that dramatically improve Claude's output quality for specific tasks.

## What Are Claude Skills?

Claude Skills are structured instruction sets that Claude reads before executing a task. Think of them as "expert mode activators" — instead of getting generic, averaged-out responses, skills prime Claude with domain-specific knowledge, workflows, and quality standards.

Each skill lives in its own folder with a `SKILL.md` file and optional supporting resources.

## 📦 Available Skills

| Skill | Description | Use Case |
|-------|-------------|----------|
| [Expert Role Refiner](skills/expert-role-refiner/) | Activates hyper-specific expert personas through an iterative refinement loop | Any task where quality matters — coding, writing, analysis, strategy |

## 🚀 Quick Start

### Using with Claude Projects

1. Create a new [Claude Project](https://claude.ai)
2. Copy the `SKILL.md` file from any skill into your project's knowledge base
3. Claude will automatically use the skill when relevant tasks come up

### Using with Claude Code

1. Clone this repo into your project
2. Reference the skill in your system prompt or let Claude discover it

```bash
git clone https://github.com/YOUR_USERNAME/claude-skills.git
```

### Manual Usage

Copy-paste the contents of any `SKILL.md` directly into your conversation with Claude. It works immediately.

## 📁 Repo Structure

```
claude-skills/
├── README.md                          # You are here
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # How to add skills
├── skills/
│   └── expert-role-refiner/
│       ├── SKILL.md                   # The skill definition
│       └── README.md                  # Usage docs & examples
├── examples/
│   ├── role-refiner-examples.md       # Test prompts & sample outputs
│   └── before-after-comparisons.md    # Side-by-side quality comparisons
└── docs/
    └── how-role-refinement-works.md   # Deep-dive article / tutorial
```

## 🧪 Testing a Skill

Every skill includes example prompts you can test with. See the [examples/](examples/) directory for ready-to-use test cases.

Quick test for the Expert Role Refiner:

> **Prompt:** "Help me optimize a PostgreSQL query that's scanning 50M rows and timing out after 30 seconds"
>
> Without the skill: You get a generic DBA response with standard indexing advice.
> With the skill: You get a response from a "staff database engineer who spent 6 years at Timescale optimizing time-series queries at petabyte scale" — fundamentally different advice.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new skills.

The short version:
1. Create a folder in `skills/` with a descriptive name
2. Write a `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add a `README.md` with usage examples
4. Submit a PR

## 📄 License

MIT — use these skills however you want.

---

*Built with Claude. Improved by humans. Repeat.*
