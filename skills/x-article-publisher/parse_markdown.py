#!/usr/bin/env python3
"""
Parse Markdown article into structured data for X Articles publishing.

Extracts:
- Title (from H1)
- Cover image (first image)
- Content images with block_index positions
- Code blocks with language and block_index
- Divider positions
- HTML body (without H1, images, code blocks, dividers)

Usage:
    python3 parse_markdown.py /path/to/article.md [--output json]
"""

import json
import os
import re
import sys
from pathlib import Path


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from start of file."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


def parse_markdown(filepath: str) -> dict:
    """Parse a Markdown file into structured data for X Articles."""
    filepath = os.path.expanduser(filepath)
    md_dir = os.path.dirname(os.path.abspath(filepath))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = strip_frontmatter(content)
    lines = content.split("\n")

    title = ""
    cover_image = None
    content_images = []
    code_blocks = []
    dividers = []
    body_lines = []

    # Track state
    in_code_block = False
    code_lang = ""
    code_content = []
    first_image_seen = False
    block_index = 0  # Counts block-level elements in the output HTML

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Code block detection ---
        if line.strip().startswith("```"):
            if not in_code_block:
                # Opening fence
                in_code_block = True
                code_lang = line.strip().lstrip("`").strip()
                code_content = []
                i += 1
                continue
            else:
                # Closing fence
                in_code_block = False
                code_text = "\n".join(code_content)
                if code_text.strip():
                    code_blocks.append({
                        "language": code_lang or "text",
                        "code": code_text,
                        "block_index": block_index,
                    })
                    # Code block becomes an image — placeholder in body
                    block_index += 1
                code_lang = ""
                code_content = []
                i += 1
                continue

        if in_code_block:
            code_content.append(line)
            i += 1
            continue

        # --- H1 title extraction ---
        h1_match = re.match(r"^# (.+)$", line)
        if h1_match and not title:
            title = h1_match.group(1).strip()
            i += 1
            continue

        # --- Image detection ---
        img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if img_match:
            img_path = img_match.group(2).strip()
            # Resolve relative paths
            if not os.path.isabs(img_path) and not img_path.startswith("http"):
                img_path = os.path.normpath(os.path.join(md_dir, img_path))

            if not first_image_seen:
                cover_image = img_path
                first_image_seen = True
            else:
                content_images.append({
                    "path": img_path,
                    "block_index": block_index,
                })
            # Images don't increment block_index here —
            # they're placed AFTER the block at block_index
            i += 1
            continue

        # --- Divider detection ---
        if re.match(r"^---+\s*$", line.strip()) or re.match(r"^\*\*\*+\s*$", line.strip()):
            dividers.append(block_index)
            i += 1
            continue

        # --- Regular content → HTML ---
        stripped = line.strip()

        # Skip blank lines between blocks (but they don't create blocks)
        if not stripped:
            i += 1
            continue

        # Headers (H2-H6)
        h_match = re.match(r"^(#{2,6}) (.+)$", line)
        if h_match:
            level = len(h_match.group(1))
            text = inline_format(h_match.group(2).strip())
            body_lines.append(f"<h{level}>{text}</h{level}>")
            block_index += 1
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            text = inline_format(" ".join(quote_lines))
            body_lines.append(f"<blockquote>{text}</blockquote>")
            block_index += 1
            continue

        # Unordered list
        if re.match(r"^[-*+] ", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*+] ", lines[i]):
                item_text = re.sub(r"^\s*[-*+] ", "", lines[i]).strip()
                items.append(f"<li>{inline_format(item_text)}</li>")
                i += 1
            body_lines.append("<ul>" + "".join(items) + "</ul>")
            block_index += 1
            continue

        # Ordered list
        if re.match(r"^\d+\. ", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\. ", lines[i]):
                item_text = re.sub(r"^\s*\d+\. ", "", lines[i]).strip()
                items.append(f"<li>{inline_format(item_text)}</li>")
                i += 1
            body_lines.append("<ol>" + "".join(items) + "</ol>")
            block_index += 1
            continue

        # Table detection (| col1 | col2 |)
        if re.match(r"^\|.+\|", stripped):
            table_lines = []
            while i < len(lines) and re.match(r"^\s*\|.+\|", lines[i]):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                # Store table as markdown text for table_to_image.py
                table_md = "\n".join(table_lines)
                code_blocks.append({
                    "language": "__table__",
                    "code": table_md,
                    "block_index": block_index,
                })
                block_index += 1
            continue

        # Regular paragraph — collect consecutive non-empty lines
        para_lines = []
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        if para_lines:
            text = inline_format(" ".join(para_lines))
            body_lines.append(f"<p>{text}</p>")
            block_index += 1
            continue

        i += 1

    html = "\n".join(body_lines)

    return {
        "title": title,
        "cover_image": cover_image,
        "content_images": content_images,
        "code_blocks": code_blocks,
        "dividers": dividers,
        "total_blocks": block_index,
        "html": html,
    }


def _is_block_start(line: str) -> bool:
    """Check if a line starts a new block element."""
    s = line.strip()
    if not s:
        return True
    if re.match(r"^#{1,6} ", s):
        return True
    if s.startswith("> "):
        return True
    if re.match(r"^[-*+] ", s):
        return True
    if re.match(r"^\d+\. ", s):
        return True
    if s.startswith("```"):
        return True
    if re.match(r"^---+\s*$", s) or re.match(r"^\*\*\*+\s*$", s):
        return True
    if re.match(r"^!\[", s):
        return True
    if re.match(r"^\|.+\|", s):
        return True
    return False


def inline_format(text: str) -> str:
    """Convert inline Markdown formatting to HTML."""
    # Bold + Italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    # Inline code → bold monospace (X doesn't support <code>)
    text = re.sub(r"`([^`]+)`", r"<strong>\1</strong>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_markdown.py /path/to/article.md", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(os.path.expanduser(filepath)):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    result = parse_markdown(filepath)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
