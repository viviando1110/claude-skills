---
name: x-article-publisher
description: Publish Markdown articles to X (Twitter) Articles via Playwright browser automation. Converts Markdown to rich text, handles images with block-index positioning, generates code block images, and saves as draft.
---

# X Article Publisher

Publish Markdown articles to X Articles with one command. Preserves all formatting including headers, bold, italic, links, lists, blockquotes. Converts code blocks to styled images since X doesn't support code formatting.

## When to Use This Skill

- User wants to publish a Markdown file to X/Twitter Articles
- User says "publish to X", "post to X Articles", "send to Twitter"
- User provides a .md file and wants it on X

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

## Instructions

### Step 0: Parse the Markdown

Run the parse script to extract structured data:

```bash
python3 SKILL_DIR/scripts/parse_markdown.py "/path/to/article.md"
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
python3 SKILL_DIR/scripts/code_to_image.py \
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

This is the key step. Use clipboard to paste rich text:

```bash
python3 SKILL_DIR/scripts/copy_to_clipboard.py --html "<h2>My Section</h2><p>Content here...</p>"
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
✅ Article draft saved to X Articles!
   Title: {title}
   Cover image: {yes/no}
   Content images: {count}
   Code block images: {count}
   Dividers: {count}
   Status: DRAFT (review and publish manually at x.com)
```

## Error Handling

- If Playwright MCP is not available → Tell user to configure it
- If not logged into X → Tell user to log in via the Playwright browser first
- If Articles editor doesn't load → X Premium may not be active
- If image upload fails → Check file path, format (jpg/png/gif/webp), and network
- If clipboard paste loses formatting → Ensure copy_to_clipboard.py ran successfully

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
- Scripts are at `SKILL_DIR/scripts/`
- All image paths from parse output are absolute (resolved from the .md file location)
