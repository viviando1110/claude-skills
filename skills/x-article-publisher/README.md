# X Article Publisher Skill

> Fork of [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill) with enhancements for code blocks, tables, and cross-platform support.

Publish Markdown articles to X (Twitter) Articles with one command. Say goodbye to tedious rich text editing.

**v2.0.0** — Code-to-image, table-to-image, cross-platform clipboard, updated for Premium (not just Premium+)

## What's New vs Original

| Feature | wshuyi v1.2 | This Fork v2.0 |
|---------|-------------|-----------------|
| Code blocks | ❌ Not handled | ✅ Rendered as styled PNG images (4 themes) |
| Tables | ✅ table_to_image.py | ✅ Improved + auto-detected in parser |
| X Premium tier | Premium+ only | ✅ All Premium tiers (Articles expanded Jan 2026) |
| Linux support | ❌ macOS/Windows | ✅ macOS/Windows/Linux |
| Image clipboard | macOS only | ✅ Cross-platform |
| Themes | N/A | Monokai, GitHub Dark, Dracula, One Dark |

## The Problem

Writing in Markdown is great. Publishing to X Articles is painful:

- Copy from editor → paste to X → **all formatting gone**
- Re-add headers, bold, links manually → **15-20 min per article**
- Code blocks? X doesn't support them **at all**
- Tables? Also not supported

**This skill does it all in 2-3 minutes.**

## Architecture

```
Markdown File (.md)
     ↓ parse_markdown.py
Structured Data (title, images, code_blocks, tables, HTML)
     ↓ code_to_image.py / table_to_image.py
Code/Table → Styled PNG images
     ↓ copy_to_clipboard.py
Rich text HTML → System clipboard
     ↓ Playwright MCP
X Articles Editor (browser automation)
     ↓
Draft Saved (NEVER auto-publishes)
```

## Requirements

| Requirement | Details |
|-------------|---------|
| Claude Code | [claude.ai/code](https://claude.ai/code) |
| Playwright MCP | Browser automation server |
| X Premium | Any tier (Basic/Premium/Premium+) |
| Python 3.9+ | With dependencies below |
| OS | macOS, Windows, or Linux |

```bash
# macOS
pip install Pillow pyobjc-framework-Cocoa Pygments

# Windows
pip install Pillow pywin32 clip-util Pygments

# Linux
pip install Pillow Pygments
sudo apt-get install xclip  # or xsel, or wl-clipboard
```

## Installation

```bash
git clone https://github.com/USERNAME/claude-skills.git
cp -r claude-skills/skills/x-article-publisher ~/.claude/skills/
```

## Usage

```
Publish ~/Documents/my-article.md to X
```

```
Help me post this article to X Articles: /path/to/article.md
```

## Supported Markdown

| Syntax | Rendering |
|--------|-----------|
| `# H1` | Article title (not in body) |
| `## H2` - `###### H6` | Section headers |
| `**bold**` | Bold text |
| `*italic*` | Italic text |
| `~~strike~~` | Strikethrough |
| `[text](url)` | Hyperlinks |
| `> quote` | Blockquotes |
| `- item` / `1. item` | Lists |
| `![](img.jpg)` | Images (first = cover) |
| `` `code` `` | Inline code (bold) |
| ```` ```lang ```` | **Code blocks → PNG images** |
| `---` | Dividers |
| `\| table \|` | **Tables → PNG images** |
| YAML frontmatter | Auto-skipped |

## Code Image Themes

Four built-in themes for code block rendering:

- **monokai** (default) — Classic dark theme
- **github-dark** — GitHub's dark mode
- **dracula** — Popular purple-tinted dark theme  
- **one-dark** — Atom's One Dark theme

## Scripts

### `parse_markdown.py`
Parses Markdown into structured JSON with block-index positions.

```bash
python3 scripts/parse_markdown.py article.md
```

### `code_to_image.py`
Renders code as styled PNG with syntax highlighting.

```bash
python3 scripts/code_to_image.py --code "print('hi')" --language python --output code.png --theme dracula
```

### `table_to_image.py`
Renders Markdown tables as styled PNG.

```bash
python3 scripts/table_to_image.py --table "| A | B |\n|---|---|\n| 1 | 2 |" --output table.png
```

### `copy_to_clipboard.py`
Copies HTML to system clipboard as rich text (cross-platform).

```bash
python3 scripts/copy_to_clipboard.py --html "<h2>Title</h2><p>Content</p>"
python3 scripts/copy_to_clipboard.py --image code.png
```

## Credits

- Original skill: [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill) by Shuyi Wang (MIT License)
- v1.2.0 divider/table/Windows features inspired by [sugarforever/01coder-agent-skills](https://github.com/sugarforever/01coder-agent-skills)

## License

MIT — See [LICENSE](../../LICENSE)
