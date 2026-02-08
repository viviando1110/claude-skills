#!/usr/bin/env python3
"""
Copy HTML content to clipboard as rich text for pasting into X Articles editor.

Cross-platform support:
- macOS: Uses pyobjc NSPasteboard (preserves rich text)
- Windows: Uses pywin32 + clip-util (preserves rich text)
- Linux: Uses xclip with text/html target

Usage:
    python3 copy_to_clipboard.py --html "<h2>Title</h2><p>Content</p>"
    python3 copy_to_clipboard.py --file article.html
"""

import argparse
import os
import platform
import subprocess
import sys
import tempfile


def copy_html_macos(html: str) -> bool:
    """Copy HTML to macOS clipboard using NSPasteboard."""
    try:
        from AppKit import NSPasteboard, NSData, NSString
        from AppKit import NSPasteboardTypeHTML, NSPasteboardTypeString

        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()

        # Set HTML content
        html_data = NSData.dataWithBytes_length_(
            html.encode("utf-8"), len(html.encode("utf-8"))
        )
        pb.setData_forType_(html_data, NSPasteboardTypeHTML)

        # Also set plain text fallback
        import re
        plain = re.sub(r"<[^>]+>", "", html)
        plain = plain.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        pb.setString_forType_(plain, NSPasteboardTypeString)

        return True
    except ImportError:
        print("Warning: pyobjc not available, trying pbcopy fallback", file=sys.stderr)
        return copy_html_macos_fallback(html)


def copy_html_macos_fallback(html: str) -> bool:
    """Fallback: write HTML to temp file and use osascript."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            tmp_path = f.name

        # Use osascript to set clipboard
        script = f'''
        set theFile to POSIX file "{tmp_path}"
        set theHTML to read theFile as «class utf8»
        set the clipboard to theHTML
        '''
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        os.unlink(tmp_path)
        return True
    except Exception as e:
        print(f"macOS fallback failed: {e}", file=sys.stderr)
        return False


def copy_html_windows(html: str) -> bool:
    """Copy HTML to Windows clipboard using pywin32."""
    try:
        import win32clipboard
        import win32con

        # Windows HTML clipboard format requires specific header
        header = (
            "Version:0.9\r\n"
            "StartHTML:{start_html:010d}\r\n"
            "EndHTML:{end_html:010d}\r\n"
            "StartFragment:{start_frag:010d}\r\n"
            "EndFragment:{end_frag:010d}\r\n"
        )
        prefix = "<!DOCTYPE html><html><body><!--StartFragment-->"
        suffix = "<!--EndFragment--></body></html>"

        # Calculate positions
        dummy_header = header.format(
            start_html=0, end_html=0, start_frag=0, end_frag=0
        )
        start_html = len(dummy_header)
        start_frag = start_html + len(prefix)
        end_frag = start_frag + len(html.encode("utf-8"))
        end_html = end_frag + len(suffix)

        full_header = header.format(
            start_html=start_html,
            end_html=end_html,
            start_frag=start_frag,
            end_frag=end_frag,
        )
        clipboard_data = full_header + prefix + html + suffix

        CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(CF_HTML, clipboard_data.encode("utf-8"))

        # Also set plain text
        import re
        plain = re.sub(r"<[^>]+>", "", html)
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, plain)

        win32clipboard.CloseClipboard()
        return True
    except ImportError:
        print("Warning: pywin32 not available, trying clip-util fallback", file=sys.stderr)
        return copy_html_windows_fallback(html)


def copy_html_windows_fallback(html: str) -> bool:
    """Fallback using clip-util on Windows."""
    try:
        import cliputil
        cliputil.set_html(html)
        return True
    except ImportError:
        print("Error: Neither pywin32 nor clip-util available on Windows", file=sys.stderr)
        return False


def copy_html_linux(html: str) -> bool:
    """Copy HTML to Linux clipboard using xclip."""
    try:
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard", "-t", "text/html"],
            stdin=subprocess.PIPE,
        )
        process.communicate(html.encode("utf-8"))
        if process.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Try xsel
    try:
        process = subprocess.Popen(
            ["xsel", "--clipboard", "--input"],
            stdin=subprocess.PIPE,
        )
        process.communicate(html.encode("utf-8"))
        if process.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Try wl-copy (Wayland)
    try:
        process = subprocess.Popen(
            ["wl-copy", "--type", "text/html"],
            stdin=subprocess.PIPE,
        )
        process.communicate(html.encode("utf-8"))
        if process.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    print("Error: No clipboard tool found. Install xclip, xsel, or wl-clipboard", file=sys.stderr)
    return False


def copy_image_to_clipboard(image_path: str) -> bool:
    """Copy an image file to clipboard (for pasting images into editor)."""
    system = platform.system()

    if system == "Darwin":
        try:
            from AppKit import NSPasteboard, NSImage, NSPasteboardTypePNG

            pb = NSPasteboard.generalPasteboard()
            pb.clearContents()
            image = NSImage.alloc().initWithContentsOfFile_(image_path)
            if image:
                pb.writeObjects_([image])
                return True
        except ImportError:
            # osascript fallback
            script = f'''
            set theImage to (read (POSIX file "{image_path}") as TIFF picture)
            set the clipboard to theImage
            '''
            try:
                subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
                return True
            except Exception:
                pass

    elif system == "Windows":
        try:
            from PIL import Image
            import win32clipboard
            import io

            img = Image.open(image_path)
            output = io.BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # Remove BMP header

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except ImportError:
            pass

    elif system == "Linux":
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", image_path],
                check=True, capture_output=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                subprocess.run(
                    ["wl-copy", "--type", "image/png"],
                    stdin=open(image_path, "rb"),
                    check=True, capture_output=True
                )
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

    print(f"Error: Could not copy image to clipboard on {system}", file=sys.stderr)
    return False


def copy_to_clipboard(html: str) -> bool:
    """Copy HTML to clipboard (auto-detects platform)."""
    system = platform.system()
    if system == "Darwin":
        return copy_html_macos(html)
    elif system == "Windows":
        return copy_html_windows(html)
    elif system == "Linux":
        return copy_html_linux(html)
    else:
        print(f"Unsupported platform: {system}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Copy HTML to clipboard as rich text")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html", type=str, help="HTML string to copy")
    group.add_argument("--file", type=str, help="HTML file to copy")
    group.add_argument("--image", type=str, help="Image file to copy to clipboard")

    args = parser.parse_args()

    if args.image:
        path = os.path.expanduser(args.image)
        if not os.path.exists(path):
            print(f"Error: Image not found: {path}", file=sys.stderr)
            sys.exit(1)
        if copy_image_to_clipboard(path):
            print(f"Image copied to clipboard: {path}")
        else:
            sys.exit(1)
    else:
        if args.html:
            html = args.html
        else:
            with open(os.path.expanduser(args.file), "r", encoding="utf-8") as f:
                html = f.read()

        if copy_to_clipboard(html):
            print(f"HTML copied to clipboard ({len(html)} chars)")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
