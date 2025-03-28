#!/usr/bin/env python3
"""ASCII Character and Width Analyzer - Enhanced Edition

An interactive CLI tool that provides comprehensive character analysis with dynamic
borders that properly adjust to content and terminal dimensions.
"""

import os
import re
import shutil
import sys
import unicodedata

# Initialize pyperclip
CLIPBOARD_AVAILABLE = False
pyperclip = None
try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    pass


# Get terminal dimensions
def get_terminal_size():
    """Get current terminal size."""
    return shutil.get_terminal_size()


# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
}


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_display_width(text):
    """Calculate the monospace display width of a string.
    Accounts for wide characters like CJK and emoji.
    """
    width = 0
    for char in text:
        # Handle zero-width characters
        if unicodedata.category(char) in ["Mn", "Me", "Cf"]:
            continue
        # Handle wide characters (CJK, emoji, etc.)
        if unicodedata.east_asian_width(char) in ["F", "W"]:
            width += 2
        # Standard width characters
        else:
            width += 1
    return width


def truncate_text(text, max_width):
    """Truncate text to fit within max_width, accounting for display width."""
    if get_display_width(text) <= max_width:
        return text

    result = ""
    current_width = 0

    for char in text:
        char_width = 2 if unicodedata.east_asian_width(char) in ["F", "W"] else 1
        if current_width + char_width + 3 <= max_width:  # +3 for "..."
            result += char
            current_width += char_width
        else:
            break

    return result + "..."


def create_dynamic_box(
    content: list[str],
    title: str | None = None,
    padding: int = 2,
    min_width: int | None = None,
    max_width: int | None = None,
    center: bool = True,
) -> list[str]:
    """Create a truly dynamic ASCII box that correctly adjusts to content and terminal width.

    Args:
        content (list): List of strings to display in the box
        title (str): Optional title for the box
        padding (int): Horizontal padding inside box
        min_width (int): Minimum box width
        max_width (int): Maximum box width (defaults to terminal width - 4)
        center (bool): Whether to center content in the box

    Returns:
        list: Lines of the box as strings
    """
    # Terminal constraints
    term_width = get_terminal_size().columns

    # Default max_width if not specified
    if max_width is None:
        max_width = term_width - 4  # Leave some margin
    else:
        max_width = min(max_width, term_width - 4)

    # Calculate actual display width of each line (accounting for ANSI color codes)
    content_display_widths = []
    for line in content:
        # Remove ANSI color codes for width calculation
        clean_line = re.sub(r"\033\[[0-9;]*m", "", line)
        content_display_widths.append(get_display_width(clean_line))

    # Calculate box width (content + padding + borders)
    base_width = 0
    if content_display_widths:
        max_display_width = max(content_display_widths)
        # Ensure we're working with an integer
        base_width = int(str(max_display_width))
    box_width = base_width + (padding * 2) + 2

    # Adjust for title if needed
    if title:
        # Remove ANSI color codes for width calculation but keep for display
        clean_title = re.sub(r"\033\[[0-9;]*m", "", title)
        title_width = get_display_width(clean_title)
        box_width = max(box_width, title_width + 4)

    # Apply constraints
    if min_width is not None and box_width < min_width:
        box_width = min_width
    if max_width is not None and box_width > max_width:
        box_width = max_width

    # Box drawing characters
    h_line = "─"
    v_line = "│"
    tl = "╭"
    tr = "╮"
    bl = "╰"
    br = "╯"

    # Build box
    box_lines = []

    # Top border with optional title
    if title:
        # Remove ANSI color codes for width calculation but keep for display
        clean_title = re.sub(r"\033\[[0-9;]*m", "", title)
        title_width = get_display_width(clean_title)

        # Ensure box_width is not None before arithmetic operations
        remaining = box_width - 4 - title_width  # 4 for the spaces and box chars
        left = remaining // 2
        right = remaining - left

        box_lines.append(f"{tl}{h_line * left} {title} {h_line * right}{tr}")
    else:
        box_lines.append(f"{tl}{h_line * (box_width - 2)}{tr}")

    # Content processing with proper type checking
    for line in content:
        # Remove ANSI color codes for width calculation but keep for display
        clean_line = re.sub(r"\033\[[0-9;]*m", "", line)
        display_width = get_display_width(clean_line)

        # Handle truncation if needed
        content_space = box_width - (padding * 2) - 2
        if display_width > content_space:
            max_content_width = content_space
            truncated = ""
            current_width = 0

            line_without_ansi = re.sub(r"\033\[[0-9;]*m", "", line)

            i = 0
            while (
                i < len(line_without_ansi) and current_width < max_content_width - 3
            ):  # -3 for "..."
                char = line_without_ansi[i]
                char_width = (
                    2 if unicodedata.east_asian_width(char) in ["F", "W"] else 1
                )

                if current_width + char_width <= max_content_width - 3:
                    truncated += char
                    current_width += char_width
                else:
                    break
                i += 1

            # Transfer color codes from original to truncated text
            colored_truncated = ""
            original_idx = 0
            for char in truncated:
                while original_idx < len(line) and line[original_idx] != char:
                    if line[original_idx] == "\033":
                        # Copy the ANSI sequence
                        match = re.search(r"m", line[original_idx:])
                        if match:
                            ansi_end = match.end()
                            ansi_seq = line[original_idx : original_idx + ansi_end]
                            colored_truncated += ansi_seq
                            original_idx += len(ansi_seq)
                        else:
                            original_idx += 1
                    else:
                        original_idx += 1

                if original_idx < len(line):
                    colored_truncated += line[original_idx]
                    original_idx += 1

            line = colored_truncated + "..." + COLORS["reset"]
            # Recalculate display width for the truncated line
            clean_line = re.sub(r"\033\[[0-9;]*m", "", colored_truncated + "...")
            display_width = get_display_width(clean_line)

        # Calculate padding based on centering preference
        if center:
            available_space = box_width - 2 - display_width
            left_pad = available_space // 2
            right_pad = available_space - left_pad
        else:
            left_pad = padding
            right_pad = box_width - 2 - display_width - left_pad

        box_lines.append(f"{v_line}{' ' * left_pad}{line}{' ' * right_pad}{v_line}")

    # Bottom border
    box_lines.append(f"{bl}{h_line * (box_width - 2)}{br}")

    return box_lines


def analyze_string(text):
    """Perform comprehensive analysis of a string.

    Returns a dictionary with analysis results.
    """
    results = {}

    # Basic metrics
    results["char_count"] = len(text)
    results["display_width"] = get_display_width(text)
    results["bytes"] = len(text.encode("utf-8"))

    # Character type analysis
    char_types = {}
    width_types = {}
    categories = {}

    for char in text:
        # Unicode category
        cat = unicodedata.category(char)
        categories[cat] = categories.get(cat, 0) + 1

        # Display width type
        width = unicodedata.east_asian_width(char)
        width_types[width] = width_types.get(width, 0) + 1

        # Character classification
        if unicodedata.category(char) in ["Mn", "Me", "Cf"]:
            char_type = "zero_width"
        elif unicodedata.east_asian_width(char) in ["F", "W"]:
            char_type = "wide"
        elif char in "─│┌┐└┘├┤┬┴┼╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿":
            char_type = "box_drawing"
        elif ord(char) < 32 or (ord(char) >= 127 and ord(char) < 160):
            char_type = "control"
        else:
            char_type = "standard"

        char_types[char_type] = char_types.get(char_type, 0) + 1

    results["char_types"] = char_types
    results["width_types"] = width_types
    results["categories"] = categories

    # Detect patterns
    results["has_box_drawing"] = any(
        c in "─│┌┐└┘├┤┬┴┼╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿" for c in text
    )
    results["has_wide_chars"] = any(
        unicodedata.east_asian_width(c) in ["F", "W"] for c in text
    )
    results["has_zero_width"] = any(
        unicodedata.category(c) in ["Mn", "Me", "Cf"] for c in text
    )

    return results


def format_analysis_results(analysis):
    """Format analysis results for display."""
    lines = []

    # Basic metrics
    lines.append(f"{COLORS['bold']}BASIC METRICS:{COLORS['reset']}")
    lines.append(
        f"• Character count: {COLORS['green']}{analysis['char_count']}{COLORS['reset']}"
    )
    lines.append(
        f"• Display width: {COLORS['green']}{analysis['display_width']}{COLORS['reset']}"
    )
    lines.append(
        f"• UTF-8 bytes: {COLORS['green']}{analysis['bytes']}{COLORS['reset']}"
    )

    # Explain any discrepancy
    if analysis["char_count"] != analysis["display_width"]:
        lines.append("")
        if analysis["display_width"] > analysis["char_count"]:
            diff = analysis["display_width"] - analysis["char_count"]
            lines.append(
                f"{COLORS['yellow']}Width exceeds count by {diff} columns{COLORS['reset']}"
            )
            if analysis["has_wide_chars"]:
                lines.append("  (Contains wide characters that occupy 2 columns each)")
        else:
            diff = analysis["char_count"] - analysis["display_width"]
            lines.append(
                f"{COLORS['yellow']}Count exceeds width by {diff} characters{COLORS['reset']}"
            )
            if analysis["has_zero_width"]:
                lines.append("  (Contains zero-width or combining characters)")

    # Character type breakdown
    if analysis["char_types"]:
        lines.append("")
        lines.append(f"{COLORS['bold']}CHARACTER TYPES:{COLORS['reset']}")
        for char_type, count in sorted(
            analysis["char_types"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / analysis["char_count"]) * 100
            lines.append(f"• {char_type}: {count} ({percentage:.1f}%)")

    # Special notices
    if analysis["has_box_drawing"]:
        lines.append("")
        lines.append(
            f"{COLORS['cyan']}Contains box-drawing characters{COLORS['reset']}"
        )

    return lines


def display_welcome():
    """Display welcome message and instructions."""
    welcome_text = [
        f"{COLORS['bold']}{COLORS['cyan']}ASCII CHARACTER AND WIDTH ANALYZER{COLORS['reset']}",
        "",
        "This tool helps analyze text for ASCII UI design by measuring:",
        "• Character count (actual Unicode characters)",
        "• Display width (columns in monospace terminal)",
        "",
        f"{COLORS['bold']}COMMANDS:{COLORS['reset']}",
        "• Enter text directly to analyze it",
        "• Type 'clip' to analyze clipboard content",
        "• Type 'clear' to clear the screen",
        "• Type 'exit' to quit the program",
    ]

    welcome_box = create_dynamic_box(welcome_text, padding=2, min_width=60)
    print()
    for line in welcome_box:
        print(line)
    print()


def display_results(text, analysis):
    """Display analysis results in nicely formatted boxes."""
    # Input box
    input_text = [text]
    input_box = create_dynamic_box(
        input_text,
        title=f"{COLORS['bold']}INPUT TEXT{COLORS['reset']}",
        padding=2,
        center=False,
    )

    # Results box
    result_text = format_analysis_results(analysis)
    result_box = create_dynamic_box(
        result_text,
        title=f"{COLORS['bold']}ANALYSIS RESULTS{COLORS['reset']}",
        padding=2,
        center=False,
    )

    # Print both boxes
    print()
    for line in input_box:
        print(line)
    print()
    for line in result_box:
        print(line)
    print()


def main():
    """Main function for the interactive CLI."""
    clear_screen()
    display_welcome()

    while True:
        try:
            # Get user input
            print(
                f"\n{COLORS['bold']}Enter text to analyze (or command):{COLORS['reset']}"
            )
            user_input = input(f"{COLORS['green']}> {COLORS['reset']}")

            # Process commands
            if user_input.lower() in ["exit", "quit"]:
                print(
                    f"\n{COLORS['cyan']}Thank you for using the ASCII Character Analyzer. Goodbye!{COLORS['reset']}"
                )
                sys.exit(0)

            elif user_input.lower() == "clear":
                clear_screen()
                display_welcome()
                continue

            elif user_input.lower() in ["clip", "clipboard"]:
                if CLIPBOARD_AVAILABLE and pyperclip is not None:
                    try:
                        clipboard_text = pyperclip.paste()
                        if clipboard_text:
                            user_input = clipboard_text
                            print(
                                f"{COLORS['yellow']}Analyzing clipboard content ({len(clipboard_text)} chars){COLORS['reset']}"
                            )
                        else:
                            print(
                                f"{COLORS['red']}Clipboard appears to be empty{COLORS['reset']}"
                            )
                            continue
                    except Exception as e:
                        print(
                            f"{COLORS['red']}Error accessing clipboard: {e!s}{COLORS['reset']}"
                        )
                        continue
                else:
                    print(
                        f"{COLORS['red']}Clipboard feature not available. Install pyperclip module.{COLORS['reset']}"
                    )
                    print(
                        f"{COLORS['yellow']}Run: pip install pyperclip{COLORS['reset']}"
                    )
                    continue

            elif user_input.lower() in ["help", "?"]:
                display_welcome()
                continue

            # Skip empty input
            if not user_input:
                continue

            # Analyze the input
            analysis = analyze_string(user_input)
            display_results(user_input, analysis)

        except KeyboardInterrupt:
            print(f"\n{COLORS['cyan']}Program interrupted. Goodbye!{COLORS['reset']}")
            sys.exit(0)

        except Exception as e:
            print(f"\n{COLORS['red']}Error: {e!s}{COLORS['reset']}")
            print(f"{COLORS['yellow']}Please try again.{COLORS['reset']}")


if __name__ == "__main__":
    main()
