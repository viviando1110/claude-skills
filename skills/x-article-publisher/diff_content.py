#!/usr/bin/env python3
"""
Compare X Articles editor HTML with local markdown source.

Normalizes both to plain text, then produces a unified diff + summary.
Used by the proofread mode to highlight divergence between what's published
in the X editor and the local source of truth.

Zero external dependencies — uses only stdlib.

Usage:
    python3 diff_content.py --html "<scraped HTML>" --markdown /path/to/article.md
    python3 diff_content.py --html-file /tmp/scraped.html --markdown /path/to/article.md
"""

import argparse
import difflib
import html
import os
import re
import sys


def html_to_text(html_content: str) -> list[str]:
    """Convert HTML to normalized plain text lines.

    Strips tags, decodes entities, normalizes whitespace.
    Preserves block-level structure (one line per block element).
    """
    text = html_content

    # Replace block-level tags with newlines
    block_tags = r"</?(?:p|div|h[1-6]|li|tr|br|blockquote|hr|pre|ul|ol|table)\b[^>]*>"
    text = re.sub(block_tags, "\n", text, flags=re.IGNORECASE)

    # Strip all remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize whitespace within lines, strip blank lines
    lines = []
    for line in text.split("\n"):
        cleaned = " ".join(line.split()).strip()
        if cleaned:
            lines.append(cleaned)

    return lines


def markdown_to_text(filepath: str) -> list[str]:
    """Convert markdown file to normalized plain text lines.

    Strips markdown syntax and normalizes to match html_to_text output.
    """
    filepath = os.path.expanduser(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip YAML frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:]

    lines = []
    in_code_block = False

    for line in content.split("\n"):
        stripped = line.strip()

        # Toggle code blocks
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
            else:
                in_code_block = False
            continue

        # Include code block content as-is (trimmed)
        if in_code_block:
            if stripped:
                lines.append(stripped)
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Skip H1 lines — H1 maps to X Articles title field, not the body
        if re.match(r"^#\s+", stripped):
            continue

        # Strip H2-H6 markers
        stripped = re.sub(r"^#{2,6}\s+", "", stripped)

        # Skip standalone images
        if re.match(r"^!\[.*\]\(.*\)$", stripped):
            continue

        # Skip dividers
        if re.match(r"^[-*_]{3,}\s*$", stripped):
            continue

        # Skip table separator rows
        if re.match(r"^[\s|:-]+$", stripped):
            continue

        # Strip table pipes but keep content
        if re.match(r"^\|.+\|$", stripped):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            stripped = " | ".join(cells)

        # Strip list markers
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\d+\.\s+", "", stripped)

        # Strip blockquote markers
        stripped = re.sub(r"^>\s*", "", stripped)

        # Strip inline formatting
        stripped = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", stripped)  # bold+italic
        stripped = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)  # bold
        stripped = re.sub(r"\*(.+?)\*", r"\1", stripped)  # italic
        stripped = re.sub(r"~~(.+?)~~", r"\1", stripped)  # strikethrough
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)  # inline code
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)  # links

        # Normalize whitespace
        cleaned = " ".join(stripped.split()).strip()
        if cleaned:
            lines.append(cleaned)

    return lines


def generate_diff(html_lines: list[str], md_lines: list[str]) -> str:
    """Generate unified diff + summary between HTML-derived and markdown-derived text."""
    diff_lines = list(difflib.unified_diff(
        md_lines,
        html_lines,
        fromfile="local .md (source of truth)",
        tofile="X editor (published)",
        lineterm="",
    ))

    # Compute summary stats
    matcher = difflib.SequenceMatcher(None, md_lines, html_lines)
    ratio = matcher.ratio()

    added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    summary_parts = [
        f"Match: {ratio:.1%}",
        f"Lines in local .md: {len(md_lines)}",
        f"Lines in X editor: {len(html_lines)}",
    ]

    if added == 0 and removed == 0:
        summary_parts.append("Status: IDENTICAL (no differences)")
    else:
        summary_parts.append(f"Lines only in X editor (+): {added}")
        summary_parts.append(f"Lines only in local .md (-): {removed}")

    output = "=== DIFF SUMMARY ===\n"
    output += "\n".join(summary_parts)
    output += "\n\n"

    if diff_lines:
        output += "=== UNIFIED DIFF ===\n"
        output += "\n".join(diff_lines)
    else:
        output += "No differences found."

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Compare X editor HTML with local markdown source"
    )
    html_group = parser.add_mutually_exclusive_group(required=True)
    html_group.add_argument("--html", type=str, help="Scraped HTML string")
    html_group.add_argument("--html-file", type=str, help="File containing scraped HTML")
    parser.add_argument("--markdown", type=str, required=True, help="Path to local .md file")

    args = parser.parse_args()

    if args.html:
        html_content = args.html
    else:
        with open(os.path.expanduser(args.html_file), "r", encoding="utf-8") as f:
            html_content = f.read()

    html_lines = html_to_text(html_content)
    md_lines = markdown_to_text(args.markdown)
    result = generate_diff(html_lines, md_lines)
    print(result)


if __name__ == "__main__":
    main()
