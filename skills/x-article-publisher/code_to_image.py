#!/usr/bin/env python3
"""
Convert code snippets to styled PNG images for X Articles.

Since X Articles doesn't support code blocks or syntax highlighting,
this script renders code as beautiful images (similar to carbon.now.sh).

Uses Pygments for syntax highlighting and Pillow for image rendering.

Usage:
    python3 code_to_image.py --code "print('hello')" --language python --output /tmp/code.png
    python3 code_to_image.py --file snippet.py --output /tmp/code.png
    python3 code_to_image.py --code "..." --language js --theme monokai --font-size 14
"""

import argparse
import math
import os
import sys
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.token import (
        Token, Comment, Keyword, Name, String, Number,
        Operator, Punctuation, Generic, Literal
    )
except ImportError:
    print("Error: Pygments not installed. Run: pip install Pygments", file=sys.stderr)
    sys.exit(1)


# --- Theme definitions ---
THEMES = {
    "monokai": {
        "background": (39, 40, 34),
        "text": (248, 248, 242),
        "comment": (117, 113, 94),
        "keyword": (249, 38, 114),
        "string": (230, 219, 116),
        "number": (174, 129, 255),
        "function": (166, 226, 46),
        "operator": (249, 38, 114),
        "class": (102, 217, 239),
        "variable": (248, 248, 242),
        "title_bar": (30, 31, 26),
        "dots": [(255, 95, 86), (255, 189, 46), (39, 201, 63)],
    },
    "github-dark": {
        "background": (13, 17, 23),
        "text": (201, 209, 217),
        "comment": (125, 133, 144),
        "keyword": (255, 123, 114),
        "string": (165, 214, 255),
        "number": (121, 192, 255),
        "function": (210, 168, 255),
        "operator": (255, 123, 114),
        "class": (121, 192, 255),
        "variable": (201, 209, 217),
        "title_bar": (22, 27, 34),
        "dots": [(255, 95, 86), (255, 189, 46), (39, 201, 63)],
    },
    "dracula": {
        "background": (40, 42, 54),
        "text": (248, 248, 242),
        "comment": (98, 114, 164),
        "keyword": (255, 121, 198),
        "string": (241, 250, 140),
        "number": (189, 147, 249),
        "function": (80, 250, 123),
        "operator": (255, 121, 198),
        "class": (139, 233, 253),
        "variable": (248, 248, 242),
        "title_bar": (33, 34, 44),
        "dots": [(255, 85, 85), (241, 250, 140), (80, 250, 123)],
    },
    "one-dark": {
        "background": (40, 44, 52),
        "text": (171, 178, 191),
        "comment": (92, 99, 112),
        "keyword": (198, 120, 221),
        "string": (152, 195, 121),
        "number": (209, 154, 102),
        "function": (97, 175, 239),
        "operator": (86, 182, 194),
        "class": (229, 192, 123),
        "variable": (224, 108, 117),
        "title_bar": (33, 37, 43),
        "dots": [(255, 95, 86), (255, 189, 46), (39, 201, 63)],
    },
}


def token_to_color(token_type, theme: dict) -> tuple:
    """Map Pygments token type to theme color."""
    if token_type in Token.Comment or token_type in Comment:
        return theme["comment"]
    if token_type in Token.Keyword or token_type in Keyword:
        return theme["keyword"]
    if token_type in Token.Literal.String or token_type in String:
        return theme["string"]
    if token_type in Token.Literal.Number or token_type in Number:
        return theme["number"]
    if token_type in Token.Name.Function or token_type in Name.Function:
        return theme["function"]
    if token_type in Token.Name.Class or token_type in Name.Class:
        return theme["class"]
    if token_type in Token.Name.Decorator:
        return theme["function"]
    if token_type in Token.Operator or token_type in Operator:
        return theme["operator"]
    if token_type in Token.Name.Builtin:
        return theme["function"]
    return theme["text"]


def get_monospace_font(size: int):
    """Try to find a monospace font, fall back to default."""
    font_paths = [
        # macOS
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/Library/Fonts/SF-Mono-Regular.otf",
        # Linux
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    # Fall back to Pillow default
    try:
        return ImageFont.truetype("DejaVuSansMono.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


def render_code_image(
    code: str,
    language: str = "text",
    theme_name: str = "monokai",
    font_size: int = 14,
    padding: int = 20,
    line_height_factor: float = 1.5,
    max_width: int = 800,
    show_title_bar: bool = True,
    title: str = "",
    show_line_numbers: bool = True,
) -> Image.Image:
    """Render code as a styled image."""
    theme = THEMES.get(theme_name, THEMES["monokai"])
    font = get_monospace_font(font_size)
    line_height = int(font_size * line_height_factor)

    # Tokenize with Pygments
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        try:
            lexer = guess_lexer(code)
        except Exception:
            lexer = get_lexer_by_name("text")

    tokens = list(lexer.get_tokens(code))

    # Split into lines with color info
    lines = [[]]
    for tok_type, tok_value in tokens:
        color = token_to_color(tok_type, theme)
        parts = tok_value.split("\n")
        for idx, part in enumerate(parts):
            if idx > 0:
                lines.append([])
            if part:
                lines[-1].append((part, color))

    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()

    # Calculate dimensions
    # Use a temp image to measure text
    tmp_img = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp_img)

    # Measure max line width
    line_num_width = 0
    if show_line_numbers:
        num_digits = len(str(len(lines)))
        line_num_text = "9" * num_digits + "  "
        bbox = tmp_draw.textbbox((0, 0), line_num_text, font=font)
        line_num_width = bbox[2] - bbox[0]

    max_text_width = 0
    for line in lines:
        line_text = "".join(text for text, _ in line)
        if line_text:
            bbox = tmp_draw.textbbox((0, 0), line_text, font=font)
            w = bbox[2] - bbox[0]
            max_text_width = max(max_text_width, w)

    content_width = line_num_width + max_text_width + padding * 2
    content_width = max(content_width, 300)  # minimum width
    content_width = min(content_width, max_width)

    title_bar_height = 36 if show_title_bar else 0
    content_height = len(lines) * line_height + padding * 2

    img_width = content_width + padding * 2
    img_height = title_bar_height + content_height

    # Create image with rounded corners effect
    img = Image.new("RGB", (img_width, img_height), theme["background"])
    draw = ImageDraw.Draw(img)

    # Draw title bar
    if show_title_bar:
        draw.rectangle(
            [(0, 0), (img_width, title_bar_height)],
            fill=theme["title_bar"]
        )
        # Traffic light dots
        dot_y = title_bar_height // 2
        dot_radius = 6
        dot_spacing = 20
        dot_start_x = 16
        for idx, color in enumerate(theme["dots"]):
            cx = dot_start_x + idx * dot_spacing
            draw.ellipse(
                [(cx - dot_radius, dot_y - dot_radius),
                 (cx + dot_radius, dot_y + dot_radius)],
                fill=color
            )
        # Title text (language or filename)
        if title or language:
            display_title = title or language
            title_font = get_monospace_font(font_size - 2)
            title_bbox = draw.textbbox((0, 0), display_title, font=title_font)
            title_w = title_bbox[2] - title_bbox[0]
            draw.text(
                ((img_width - title_w) // 2, (title_bar_height - font_size) // 2),
                display_title,
                fill=theme["comment"],
                font=title_font
            )

    # Draw code lines
    y = title_bar_height + padding
    for line_idx, line in enumerate(lines):
        x = padding

        # Line numbers
        if show_line_numbers:
            num_text = str(line_idx + 1).rjust(len(str(len(lines))))
            draw.text((x, y), num_text, fill=theme["comment"], font=font)
            x += line_num_width

        # Code tokens
        for text, color in line:
            draw.text((x, y), text, fill=color, font=font)
            bbox = draw.textbbox((x, y), text, font=font)
            x = bbox[2]

        y += line_height

    # Add subtle border/shadow
    draw.rectangle(
        [(0, 0), (img_width - 1, img_height - 1)],
        outline=(60, 60, 60),
        width=1
    )

    return img


def main():
    parser = argparse.ArgumentParser(description="Convert code to styled PNG image")
    parser.add_argument("--code", type=str, help="Code string to render")
    parser.add_argument("--file", type=str, help="Code file to render")
    parser.add_argument("--language", type=str, default="text", help="Programming language")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--theme", type=str, default="monokai",
                        choices=list(THEMES.keys()), help="Color theme")
    parser.add_argument("--font-size", type=int, default=14, help="Font size")
    parser.add_argument("--max-width", type=int, default=800, help="Max image width")
    parser.add_argument("--no-title-bar", action="store_true", help="Hide title bar")
    parser.add_argument("--no-line-numbers", action="store_true", help="Hide line numbers")
    parser.add_argument("--title", type=str, default="", help="Title bar text")

    args = parser.parse_args()

    if args.code:
        code = args.code
    elif args.file:
        with open(os.path.expanduser(args.file), "r") as f:
            code = f.read()
        if not args.language or args.language == "text":
            ext = os.path.splitext(args.file)[1].lstrip(".")
            ext_map = {
                "py": "python", "js": "javascript", "ts": "typescript",
                "rb": "ruby", "rs": "rust", "go": "go", "java": "java",
                "c": "c", "cpp": "cpp", "cs": "csharp", "php": "php",
                "sh": "bash", "bash": "bash", "zsh": "bash",
                "sql": "sql", "html": "html", "css": "css",
                "json": "json", "yaml": "yaml", "yml": "yaml",
                "xml": "xml", "md": "markdown", "swift": "swift",
                "kt": "kotlin", "r": "r", "m": "matlab",
            }
            args.language = ext_map.get(ext, "text")
    else:
        print("Error: Provide --code or --file", file=sys.stderr)
        sys.exit(1)

    img = render_code_image(
        code=code,
        language=args.language,
        theme_name=args.theme,
        font_size=args.font_size,
        max_width=args.max_width,
        show_title_bar=not args.no_title_bar,
        show_line_numbers=not args.no_line_numbers,
        title=args.title,
    )

    output_path = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Saved: {output_path} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
