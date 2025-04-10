#!/usr/bin/env python3
"""ASCII Character and Width Analyzer

A reliable tool for measuring character count and display width
with perfectly aligned borders.
"""

import os
import shutil
import unicodedata
from typing import Any

try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    pyperclip = None


# Set up terminal colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_terminal_width() -> int:
    """Get current terminal width."""
    return shutil.get_terminal_size().columns


def get_display_width(text: str) -> int:
    """Calculate the display width of a string in a monospace terminal."""
    return sum(
        2 if unicodedata.east_asian_width(char) in ["F", "W"] else 1
        for char in text
        if unicodedata.category(char) not in ["Mn", "Me", "Cf"]
    )


def draw_box(
    lines: list[str],
    title: str | None = None,
    width: int | None = None,
    padding: int = 1,
) -> list[str]:
    """Draw a perfectly aligned box around the given lines.

    Args:
        lines: List of strings to display in the box
        title: Optional title for the box
        width: Fixed width for the box (None for auto-sizing)
        padding: Horizontal padding inside the box

    Returns:
        List of strings representing the box
    """
    # Terminal width constraint
    terminal_width = get_terminal_width()

    # Calculate content width
    content_width = max((get_display_width(line) for line in lines), default=0)

    # Calculate box width
    if width is None:
        # Auto-size with constraints
        inner_width = content_width + (padding * 2)
        box_width = min(inner_width + 2, terminal_width - 2)
    else:
        # Fixed width with constraints
        box_width = min(width, terminal_width - 2)

    # Calculate usable width for content
    usable_width = box_width - 2 - (padding * 2)

    # Border characters
    tl_corner = "╭"
    tr_corner = "╮"
    bl_corner = "╰"
    br_corner = "╯"
    h_line = "─"
    v_line = "│"

    # Result box
    result = []

    # Top border (with optional title)
    if title:
        title_display_width = get_display_width(title)
        if title_display_width > box_width - 4:
            # Truncate title if too long
            truncated = ""
            current_width = 0
            for char in title:
                char_width = get_display_width(char)
                if current_width + char_width > box_width - 7:
                    break
                truncated += char
                current_width += char_width
            title = f"{truncated}..."
            title_display_width = get_display_width(title)

        remaining = (
            box_width - 2 - title_display_width - 2
        )  # -2 for spaces around title
        left_padding = remaining // 2
        right_padding = remaining - left_padding

        result.append(
            f"{tl_corner}{h_line * left_padding} {title} "
            f"{h_line * right_padding}{tr_corner}"
        )
    else:
        result.append(f"{tl_corner}{h_line * (box_width - 2)}{tr_corner}")

    # Content lines
    for line in lines:
        line_width = get_display_width(line)
        if line_width <= usable_width:
            # Line fits, add padding
            left_space = padding
            right_space = box_width - 2 - line_width - left_space
            result.append(
                f"{v_line}{' ' * left_space}{line}{' ' * right_space}{v_line}"
            )
        else:
            # Line too long, truncate
            truncated = ""
            current_width = 0
            for char in line:
                char_width = get_display_width(char)
                if current_width + char_width > usable_width - 3:
                    break

                truncated += char
                current_width += char_width
            truncated_line = f"{truncated}..."
            truncated_width = get_display_width(truncated_line)
            right_space = box_width - 2 - truncated_width - padding

            result.append(
                f"{v_line}{' ' * padding}{truncated_line}{' ' * right_space}{v_line}"
            )

    # Bottom border
    result.append(f"{bl_corner}{h_line * (box_width - 2)}{br_corner}")

    return result


def analyze_string(text: str) -> dict[str, Any]:
    """Analyze a string for character count and display width."""
    char_count = len(text)
    display_width = get_display_width(text)
    byte_count = len(text.encode("utf-8"))

    # Detect special character types
    has_wide = any(unicodedata.east_asian_width(c) in ["F", "W"] for c in text)
    has_zero_width = any(unicodedata.category(c) in ["Mn", "Me", "Cf"] for c in text)
    box_chars = (
        "─│┌┐└┘├┤┬┴┼╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬"
        "/"  # Using standard forward slash
        "X"  # Using standard X
        "╴╵╶╷╸╹╺╻╼╽╾╿"
    )
    has_box_drawing = any(c in box_chars for c in text)

    return {
        "char_count": char_count,
        "display_width": display_width,
        "byte_count": byte_count,
        "has_wide": has_wide,
        "has_zero_width": has_zero_width,
        "has_box_drawing": has_box_drawing,
    }


def format_results(text: str, analysis: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Format analysis results for display."""
    # Input section
    input_lines = ["Input:", text]

    # Analysis section
    analysis_lines = [
        "Analysis Results:",
        f"Character count:       {analysis['char_count']}",
        f"Display width:         {analysis['display_width']}",
        f"UTF-8 bytes:           {analysis['byte_count']}",
    ]

    # Add explanation if counts differ
    if analysis["char_count"] != analysis["display_width"]:
        analysis_lines.append("")
        if analysis["display_width"] > analysis["char_count"]:
            diff = analysis["display_width"] - analysis["char_count"]
            analysis_lines.append(f"Width exceeds count by {diff} columns")
            if analysis["has_wide"]:
                analysis_lines.append("(Contains wide characters like CJK or emoji)")
        else:
            diff = analysis["char_count"] - analysis["display_width"]
            analysis_lines.append(f"Count exceeds width by {diff} characters")
            if analysis["has_zero_width"]:
                analysis_lines.append("(Contains zero-width or combining characters)")

    # Note special characters
    if analysis["has_box_drawing"]:
        if analysis_lines and analysis_lines[-1] != "":
            analysis_lines.append("")
        analysis_lines.append("Contains box-drawing characters")

    return input_lines, analysis_lines


def show_welcome() -> None:
    """Display welcome message."""
    welcome_lines = [
        "ASCII CHARACTER AND WIDTH ANALYZER",
        "",
        "This tool analyzes text for ASCII UI development:",
        "• Counts characters (Unicode code points)",
        "• Measures display width (columns in terminal)",
        "• Detects special characters",
        "",
        "Commands:",
        "• Enter text directly to analyze it",
        "• 'clip' - Analyze clipboard content",
        "• 'clear' - Clear the screen",
        "• 'exit' - Exit the program",
    ]

    box = draw_box(welcome_lines, width=70, padding=2)
    for line in box:
        print(line)
    print()


def get_clipboard_content() -> str | None:
    """Get content from clipboard if available."""
    if not CLIPBOARD_AVAILABLE or pyperclip is None:
        print(
            f"{Colors.RED}Clipboard feature not available. "
            f"Install pyperclip module:{Colors.RESET}"
        )
        print(f"{Colors.YELLOW}pip install pyperclip{Colors.RESET}")
        return None

    try:
        if clipboard_text := pyperclip.paste():
            print(
                f"{Colors.GREEN}Analyzing clipboard content "
                f"({len(clipboard_text)} chars){Colors.RESET}"
            )
            return clipboard_text
        print(f"{Colors.YELLOW}Clipboard appears to be empty{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}Error accessing clipboard: {e!s}{Colors.RESET}")
        return None


def main() -> None:
    """Main function for the interactive CLI."""
    clear_screen()
    show_welcome()

    while True:
        try:
            # Get user input
            print(f"\n{Colors.BOLD}Enter text to analyze (or command):{Colors.RESET}")
            user_input = input(f"{Colors.GREEN}> {Colors.RESET}")

            # Process commands
            if user_input.lower() in ["exit", "quit"]:
                print(
                    f"\n{Colors.CYAN}Thank you for using the ASCII Character "
                    f"Analyzer. Goodbye!{Colors.RESET}"
                )
                break

            elif user_input.lower() == "clear":
                clear_screen()
                show_welcome()
                continue

            elif user_input.lower() in ["clip", "clipboard"]:
                if clipboard_text := get_clipboard_content():
                    user_input = clipboard_text
                else:
                    continue

            elif user_input.lower() in ["help", "?"]:
                show_welcome()
                continue

            # Skip empty input
            if not user_input:
                continue

            # Analyze the input
            analysis = analyze_string(user_input)
            input_lines, analysis_lines = format_results(user_input, analysis)

            # Display results
            print()
            for line in draw_box(input_lines, title="Input", padding=2):
                print(line)
            print()
            for line in draw_box(analysis_lines, title="Analysis", padding=2):
                print(line)
            print()

        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}Program interrupted. Goodbye!{Colors.RESET}")
            break

        except Exception as e:
            print(f"\n{Colors.RED}Error: {e!s}{Colors.RESET}")
            print(f"{Colors.YELLOW}Please try again.{Colors.RESET}")


if __name__ == "__main__":
    main()
