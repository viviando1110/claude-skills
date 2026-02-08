# X Article Skill

> Fork of [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill) with enhancements for code blocks, tables, cross-platform support, and a 3-mode workflow.

Manage Markdown articles for X (Twitter) Articles with three modes: export, sync, and proofread.

**v3.0.0** — 3-mode workflow (export / sync / proofread), expert editorial review, source diff

## Three Modes

| Mode | Command | What It Does |
|------|---------|--------------|
| **Export** | `/x-article export article.md` | Full publish: parse .md → rich text + images → X Articles draft |
| **Sync** | `/x-article sync article.md` | Watch .md for changes, re-push to X editor on each turn |
| **Proofread** | `/x-article proofread article.md` | Expert editorial review + diff between X editor and local source |

### Export

The original workflow. Converts your markdown to rich text, generates code block and table images, and saves everything as a draft in X Articles.

```
/x-article export ~/Documents/my-article.md
```

### Sync

Iterative editing mode. Starts a file watcher, does an initial export, then on each subsequent message re-pushes any changes from your .md file to the X editor.

```
/x-article sync ~/Documents/my-article.md
```

Edit your .md file, send any message, and changes get pushed. Stop with:

```
/x-article sync stop
```

**Note**: Claude Code is turn-based, so changes sync when you send a message — not in real-time.

### Proofread

Expert editorial review before publishing. Scrapes the current X editor content, runs an 8-point editorial review at the 0.1% quality bar, and diffs against your local .md source.

```
/x-article proofread ~/Documents/my-article.md
```

The review covers: structural flow, clarity, concision, rhythm, hooks, technical accuracy, voice consistency, and X Articles formatting.

## What's New vs Previous Versions

| Feature | v1.2 (wshuyi) | v2.0 (fork) | v3.0 (this) |
|---------|---------------|-------------|-------------|
| Code blocks | Not handled | Styled PNG images | Styled PNG images |
| Tables | table_to_image.py | Improved + auto-detected | Improved + auto-detected |
| X Premium tier | Premium+ only | All Premium tiers | All Premium tiers |
| Platform support | macOS/Windows | macOS/Windows/Linux | macOS/Windows/Linux |
| Sync mode | N/A | N/A | File watcher + re-push |
| Proofread mode | N/A | N/A | Expert review + diff |
| Invocation | Natural language | Natural language | `/x-article <mode>` |

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

## Architecture

```
Markdown File (.md)
     | parse_markdown.py
     v
Structured Data (title, images, code_blocks, tables, HTML)
     | code_to_image.py / table_to_image.py
     v
Code/Table -> Styled PNG images
     | copy_to_clipboard.py
     v
Rich text HTML -> System clipboard
     | Playwright MCP
     v
X Articles Editor (browser automation)
     |
     v
Draft Saved (NEVER auto-publishes)
```

**Sync mode** adds `sync_watcher.py` — a background file poller that detects .md changes between turns.

**Proofread mode** adds `diff_content.py` — normalizes X editor HTML and local .md to plain text for comparison.

## Scripts

### `parse_markdown.py`
Parses Markdown into structured JSON with block-index positions.

```bash
python3 parse_markdown.py article.md
```

### `code_to_image.py`
Renders code as styled PNG with syntax highlighting.

```bash
python3 code_to_image.py --code "print('hi')" --language python --output code.png --theme dracula
```

### `table_to_image.py`
Renders Markdown tables as styled PNG.

```bash
python3 table_to_image.py --table "| A | B |\n|---|---|\n| 1 | 2 |" --output table.png
```

### `copy_to_clipboard.py`
Copies HTML to system clipboard as rich text (cross-platform).

```bash
python3 copy_to_clipboard.py --html "<h2>Title</h2><p>Content</p>"
python3 copy_to_clipboard.py --image code.png
```

### `sync_watcher.py`
Background file poller for sync mode. Zero external dependencies.

```bash
# Start watching
python3 sync_watcher.py article.md &

# Stop watching
python3 sync_watcher.py --stop
```

### `diff_content.py`
Compares X editor HTML with local markdown source. Zero external dependencies.

```bash
python3 diff_content.py --html "<scraped HTML>" --markdown article.md
```

## Code Image Themes

Four built-in themes for code block rendering:

- **monokai** (default) — Classic dark theme
- **github-dark** — GitHub's dark mode
- **dracula** — Popular purple-tinted dark theme
- **one-dark** — Atom's One Dark theme

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
| ```` ```lang ```` | **Code blocks -> PNG images** |
| `---` | Dividers |
| `\| table \|` | **Tables -> PNG images** |
| YAML frontmatter | Auto-skipped |

## Credits

- Original skill: [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill) by Shuyi Wang (MIT License)
- v1.2.0 divider/table/Windows features inspired by [sugarforever/01coder-agent-skills](https://github.com/sugarforever/01coder-agent-skills)

## License

MIT — See [LICENSE](../../LICENSE)
