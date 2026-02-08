#!/usr/bin/env python3
"""
Convert Markdown tables to styled PNG images for X Articles.

X Articles doesn't support tables, so we render them as images.

Usage:
    python3 table_to_image.py --table "| Col1 | Col2 |\n|------|------|\n| A | B |" --output /tmp/table.png
    python3 table_to_image.py --file table.md --output /tmp/table.png
"""

import argparse
import os
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def parse_table(markdown_table: str) -> tuple:
    """Parse Markdown table into headers and rows."""
    lines = [l.strip() for l in markdown_table.strip().split("\n") if l.strip()]

    if len(lines) < 2:
        return [], []

    def parse_row(line):
        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last from leading/trailing pipes
        if cells and not cells[0]:
            cells = cells[1:]
        if cells and not cells[-1]:
            cells = cells[:-1]
        return cells

    headers = parse_row(lines[0])

    # Skip separator line (|---|---|)
    rows = []
    for line in lines[2:]:
        if re.match(r"^[\s|:-]+$", line):
            continue
        rows.append(parse_row(line))

    return headers, rows


def get_font(size: int):
    """Get a suitable font."""
    font_paths = [
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()


def render_table_image(
    headers: list,
    rows: list,
    font_size: int = 14,
    padding: int = 12,
    header_bg: tuple = (42, 45, 54),
    header_fg: tuple = (255, 255, 255),
    row_bg_even: tuple = (248, 249, 250),
    row_bg_odd: tuple = (255, 255, 255),
    row_fg: tuple = (33, 37, 41),
    border_color: tuple = (222, 226, 230),
    max_col_width: int = 300,
) -> Image.Image:
    """Render a table as a styled PNG image."""
    font = get_font(font_size)
    bold_font = get_font(font_size)  # Use same font, we'll just use it for headers

    tmp = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(tmp)

    num_cols = max(len(headers), max((len(r) for r in rows), default=0))

    # Normalize rows to same column count
    headers = headers + [""] * (num_cols - len(headers))
    rows = [r + [""] * (num_cols - len(r)) for r in rows]

    # Calculate column widths
    col_widths = []
    for col_idx in range(num_cols):
        max_w = 0
        # Header
        bbox = draw.textbbox((0, 0), headers[col_idx], font=font)
        max_w = max(max_w, bbox[2] - bbox[0])
        # Rows
        for row in rows:
            if col_idx < len(row):
                bbox = draw.textbbox((0, 0), row[col_idx], font=font)
                max_w = max(max_w, bbox[2] - bbox[0])
        col_widths.append(min(max_w + padding * 2, max_col_width))

    row_height = font_size + padding * 2
    table_width = sum(col_widths) + (num_cols + 1)  # +1 for borders
    table_height = row_height * (1 + len(rows)) + (len(rows) + 2)  # borders

    # Add outer padding
    outer_pad = 8
    img_width = table_width + outer_pad * 2
    img_height = table_height + outer_pad * 2

    img = Image.new("RGB", (img_width, img_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    y = outer_pad

    # Draw header row
    x = outer_pad
    draw.rectangle([(x, y), (x + table_width - 1, y + row_height)], fill=header_bg)
    for col_idx in range(num_cols):
        # Cell border
        draw.rectangle(
            [(x, y), (x + col_widths[col_idx], y + row_height)],
            outline=border_color
        )
        # Text
        text = headers[col_idx]
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tx = x + (col_widths[col_idx] - tw) // 2
        ty = y + (row_height - font_size) // 2
        draw.text((tx, ty), text, fill=header_fg, font=font)
        x += col_widths[col_idx]

    y += row_height

    # Draw data rows
    for row_idx, row in enumerate(rows):
        bg = row_bg_even if row_idx % 2 == 0 else row_bg_odd
        x = outer_pad

        draw.rectangle([(x, y), (x + table_width - 1, y + row_height)], fill=bg)

        for col_idx in range(num_cols):
            draw.rectangle(
                [(x, y), (x + col_widths[col_idx], y + row_height)],
                outline=border_color
            )
            text = row[col_idx] if col_idx < len(row) else ""
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            tx = x + padding
            ty = y + (row_height - font_size) // 2
            draw.text((tx, ty), text, fill=row_fg, font=font)
            x += col_widths[col_idx]

        y += row_height

    return img


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown table to PNG")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--table", type=str, help="Markdown table string")
    group.add_argument("--file", type=str, help="File containing Markdown table")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--font-size", type=int, default=14, help="Font size")

    args = parser.parse_args()

    if args.table:
        table_md = args.table
    else:
        with open(os.path.expanduser(args.file), "r") as f:
            table_md = f.read()

    headers, rows = parse_table(table_md)
    if not headers:
        print("Error: Could not parse table", file=sys.stderr)
        sys.exit(1)

    img = render_table_image(headers, rows, font_size=args.font_size)
    output_path = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Saved: {output_path} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
