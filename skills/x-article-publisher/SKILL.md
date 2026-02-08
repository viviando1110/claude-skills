---
name: x-article
description: >
  Manage Markdown articles for X Articles. Three modes:
  export (publish .md as draft), sync (auto-push .md changes to X editor),
  proofread (expert review + diff against local source).
argument-hint: "<export|sync|proofread> [path-to-markdown]"
---

# X Article — Export, Sync & Proofread

Manage Markdown articles for X Articles with three modes:
- **export** — Publish a .md file as a draft to X Articles (rich text, images, code blocks)
- **sync** — Watch a .md file for changes and re-push to X editor on each turn
- **proofread** — Expert editorial review + diff between X editor and local source

## Requirements

- **Playwright MCP**: Browser automation (must be configured)
- **X Premium**: Required for Articles feature (available to all Premium tiers since Jan 2026)
- **Python 3.9+**: With platform-specific dependencies
- **Logged-in X session**: In the Playwright browser

### Python Dependencies (install once)

```bash
# macOS
pip install Pillow pyobjc-framework-Cocoa Pygments

# Windows
pip install Pillow pywin32 clip-util Pygments

# Linux
pip install Pillow Pygments
# Linux clipboard: requires xclip or xsel installed
```

---

## Mode Routing

Check `$0` (the first argument after the skill name) to determine which mode to run:

- `$0 = export` → Run **Export Mode** (Steps 0–9 below)
- `$0 = sync` → Run **Sync Mode**
- `$0 = proofread` → Run **Proofread Mode**

If `$0` is empty or unrecognized, ask the user which mode they want.

The markdown file path is `$1` (the second argument). If not provided, ask the user for it.

---

## Export Mode

Publish a Markdown file as a rich-text draft to X Articles. This is the full export pipeline.

### Step 0: Parse the Markdown

```bash
python3 SKILL_DIR/parse_markdown.py "$1"
```

This outputs JSON:
```json
{
  "title": "Article Title (from H1)",
  "cover_image": "./images/cover.jpg",
  "content_images": [
    {"path": "./images/demo.png", "block_index": 4}
  ],
  "code_blocks": [
    {"language": "python", "code": "print('hello')", "block_index": 3}
  ],
  "dividers": [5],
  "total_blocks": 8,
  "html": "<h2>Section</h2><p>Content...</p>"
}
```

**IMPORTANT**: All image paths are resolved relative to the Markdown file's directory.

### Step 1: Generate Code Block Images

If `code_blocks` is non-empty, generate images for each:

```bash
python3 SKILL_DIR/code_to_image.py \
  --code "print('hello world')" \
  --language python \
  --output /tmp/code_block_1.png \
  --theme monokai \
  --font-size 14
```

Each generated image gets added to `content_images` with its `block_index`.

### Step 2: Open X Articles Editor

Using Playwright MCP:

1. Navigate to `https://x.com/compose/articles`
2. Wait for the editor to fully load
3. Look for the title input field

**Wait condition**: The article title input field is visible.

### Step 3: Upload Cover Image (if present)

If `cover_image` exists:

1. Find the cover image upload area (the large banner area at top)
2. Click the cover image area or find the file input
3. Upload the cover image file
4. Wait for upload to complete

**Wait condition**: The image preview appears in the cover area.

### Step 4: Fill Title

1. Click the title input field
2. Type the `title` value (extracted from H1)
3. Press Tab or click into the body area

**CRITICAL**: The H1 is used ONLY for the title field. It is NOT included in the body HTML.

### Step 5: Paste Article Content

Use clipboard to paste rich text:

```bash
python3 SKILL_DIR/copy_to_clipboard.py --html "<h2>My Section</h2><p>Content here...</p>"
```

Then in Playwright:
1. Click the article body area
2. Execute Ctrl+V (Cmd+V on macOS) to paste
3. All formatting (H2, bold, italic, links, lists, blockquotes) will be preserved

**CRITICAL**: Paste via clipboard preserves rich text formatting. Direct text input would lose all formatting.

### Step 6: Insert Content Images (Reverse Order)

Images MUST be inserted in **reverse block_index order** (highest first) to prevent index shifts.

For each image (sorted by `block_index` descending):

1. Count block elements in the editor (paragraphs, headings, lists, blockquotes)
2. Click on the block element at `block_index`
3. Press Enter to create a new line after it
4. Use the image upload mechanism:
   - Click the "+" or media button
   - Select "Add photo"
   - Upload the image file
5. Wait for upload to complete before moving to next image

**Wait condition**: The image appears in the editor. Return immediately when upload is visually confirmed — do NOT use fixed delays.

### Step 7: Insert Dividers (Reverse Order)

If `dividers` array is non-empty, insert horizontal rules at those positions.

For each divider position (reverse order):

1. Click the block element at the divider's `block_index`
2. Press Enter to create a new line
3. Open the X Articles format menu (click "+" button)
4. Select the divider/horizontal rule option

### Step 8: Save as Draft

1. Look for the "Save draft" or similar button
2. Click to save
3. Confirm the draft was saved

**CRITICAL SAFETY RULE**: NEVER click "Publish". ONLY save as draft. The user must manually review and publish.

### Step 9: Report Results

Print a summary:
```
Article draft saved to X Articles!
  Title: {title}
  Cover image: {yes/no}
  Content images: {count}
  Code block images: {count}
  Dividers: {count}
  Status: DRAFT (review and publish manually at x.com)
```

---

## Sync Mode

Watch a markdown file for changes and re-push content to the X editor between turns.

**Limitation**: Claude Code is turn-based, so changes are detected and pushed when the user sends a message — not in real-time.

### Starting Sync: `/x-article sync <path>`

**Step 1: Start the file watcher**

```bash
python3 SKILL_DIR/sync_watcher.py "$1" --state /tmp/x-article-sync.json &
```

Run this as a background process. It polls the file's mtime every second and writes change events to the state file.

**Step 2: Run initial full export**

Execute the full Export Mode (Steps 0–9 above) to push the initial content to X Articles.

**Step 3: Inform the user**

Tell the user:
```
Sync active. Watching: {filepath}
Edit your .md file, then send any message to push changes to X.
Say "stop" or run `/x-article sync stop` to end the sync session.
```

### On Each Subsequent Turn (while sync is active)

1. Read the state file:
   ```bash
   python3 -c "import json; print(json.dumps(json.load(open('/tmp/x-article-sync.json')), indent=2))"
   ```

2. Check `change_count` — if it increased since last check, changes were detected.

3. If changes detected:
   a. Re-parse the markdown: `python3 SKILL_DIR/parse_markdown.py "$1"`
   b. In the X Articles editor (via Playwright MCP):
      - Select all content in the body (`Cmd+A` / `Ctrl+A`)
      - Delete it
      - Re-paste the updated HTML via clipboard (same as Export Step 5)
      - Re-insert images and dividers if needed (same as Export Steps 6–7)
   c. Report: "Pushed {change_count} change(s) to X editor."

4. If no changes: "No changes detected since last sync."

### Stopping Sync: `/x-article sync stop`

```bash
python3 SKILL_DIR/sync_watcher.py --stop --state /tmp/x-article-sync.json
```

Report: "Sync stopped. The article remains as a draft in X — review and publish manually."

---

## Proofread Mode

Expert editorial review of the article in the X editor, plus a diff against local source.

### Step 0: Scrape the X Editor

Using Playwright MCP, extract the current article content from the X Articles editor:

1. Navigate to `https://x.com/compose/articles` (or confirm it's already open)
2. Extract the title from the title input field
3. Extract the body innerHTML from `[contenteditable="true"]`
   - Fallback selectors: `[data-testid="articleBody"]`, `div[role="textbox"]`, `.public-DraftEditor-content`
4. Save the scraped HTML to `/tmp/x-article-scraped.html`

If the editor is empty or not accessible, tell the user to open the X Articles editor with a draft loaded first.

### Step 1: Expert Editorial Review

Activate an expert proofreader persona to review the article at the highest quality bar.

**Expert persona** (apply internally per expert-role-refiner methodology — do NOT explain the persona to the user, just produce expert-quality output):

Former senior editor at The Atlantic with 12 years editing long-form tech journalism. Previously edited at Wired and Ars Technica. Known for transforming dense technical content into compelling, accessible narratives without dumbing anything down. Particular strengths: structural architecture of arguments, ruthless cutting of filler, rhythm and pacing in technical prose, and ensuring every paragraph earns its place. Has a side specialty in platform-native writing — understands how formatting, length, and structure differ between blog posts, newsletters, and social media long-form (like X Articles). Applies the "would I share this?" test to every piece.

**Review the article against these 8 criteria:**

1. **Structural flow** — Does the piece have a clear arc? Does each section earn its position? Is there a compelling hook and a satisfying conclusion?
2. **Clarity** — Can a smart reader outside the exact niche follow the argument? Are there jargon gaps or assumed knowledge?
3. **Concision** — What can be cut without losing meaning? Flag filler sentences, redundant phrases, and bloated paragraphs.
4. **Rhythm & pacing** — Does sentence length vary? Are there walls of text that need breaking up? Does the piece maintain momentum?
5. **Hooks & transitions** — Does each section opening pull the reader forward? Are transitions smooth or jarring?
6. **Technical accuracy** — Are claims precise? Are there overstatements, hedging, or hand-waving where specifics are needed?
7. **Voice consistency** — Does the tone stay consistent throughout? Are there tonal shifts that feel unintentional?
8. **X Articles formatting** — Is the piece optimized for the platform? Appropriate header usage, paragraph length for screen reading, effective use of bold/emphasis, good break points?

**Apply the 0.1% quality bar**: Would a top editor look at this piece and say "this is ready"? If not, what's missing?

### Step 2: Diff Comparison

Compare the X editor content against the local markdown source:

```bash
python3 SKILL_DIR/diff_content.py --html-file /tmp/x-article-scraped.html --markdown "$1"
```

This produces:
- Match percentage between X editor and local .md
- Unified diff showing any divergence
- Summary of lines added/removed

### Step 3: Combined Report

Present a single report with three sections:

**1. Expert Editorial Review**
- Overall assessment (1-2 sentences)
- Issue-by-issue breakdown, prioritized by impact
- For each issue: what's wrong, where it is, and a specific suggested fix
- A "quick wins" section for easy improvements

**2. Source Diff**
- The diff summary and any notable divergences
- If the X editor content diverges from local .md, flag this clearly — the user needs to decide which version is authoritative

**3. Recommended Actions**
- Prioritized list: fix these first (high-impact), then these (medium), then nice-to-have
- If the article is ready to publish, say so explicitly

---

## Error Handling

- If Playwright MCP is not available → Tell user to configure it
- If not logged into X → Tell user to log in via the Playwright browser first
- If Articles editor doesn't load → X Premium may not be active
- If image upload fails → Check file path, format (jpg/png/gif/webp), and network
- If clipboard paste loses formatting → Ensure copy_to_clipboard.py ran successfully
- If sync state file is missing → Watcher may have crashed; restart with `/x-article sync <path>`

## Supported Markdown

| Syntax | Result | Notes |
|--------|--------|-------|
| `# H1` | Article title | Extracted, NOT in body |
| `## H2` - `###### H6` | Section headers | Rendered as headings |
| `**bold**` | **Bold text** | |
| `*italic*` | *Italic text* | |
| `~~strike~~` | ~~Strikethrough~~ | |
| `[text](url)` | Hyperlinks | |
| `> quote` | Blockquotes | |
| `- item` | Unordered lists | |
| `1. item` | Ordered lists | |
| `![](img.jpg)` | Images | First = cover, rest = content |
| `` `code` `` | Inline code | Rendered as bold monospace in HTML |
| ```` ```lang ```` | Code blocks | Converted to styled PNG images |
| `---` | Dividers | Inserted via X Articles menu |
| `\| table \|` | Tables | Converted to PNG images |
| YAML frontmatter | Skipped | `---` at start of file |

## File Paths

- `SKILL_DIR` = the directory containing this SKILL.md file
- Scripts are at `SKILL_DIR/` (same directory as this file)
- All image paths from parse output are absolute (resolved from the .md file location)
