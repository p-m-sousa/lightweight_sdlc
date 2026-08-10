#!/usr/bin/env python3
"""Calculate WCAG contrast for two hexadecimal sRGB colors."""

from __future__ import annotations

import argparse
import re


HEX_COLOR = re.compile(r"^#?(?P<value>[0-9a-fA-F]{6})$")


def parse_color(value: str) -> tuple[int, int, int]:
    """Parse a six-digit hexadecimal color into RGB channels."""
    match = HEX_COLOR.fullmatch(value)
    if match is None:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not a six-digit hexadecimal color"
        )
    color = match.group("value")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def linearize(channel: int) -> float:
    """Convert an 8-bit sRGB channel to linear light."""
    normalized = channel / 255
    if normalized <= 0.04045:
        return normalized / 12.92
    return ((normalized + 0.055) / 1.055) ** 2.4


def relative_luminance(color: tuple[int, int, int]) -> float:
    """Return WCAG relative luminance for an RGB color."""
    red, green, blue = (linearize(channel) for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(
    foreground: tuple[int, int, int], background: tuple[int, int, int]
) -> float:
    """Return the WCAG contrast ratio for a color pair."""
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def result(ratio: float, threshold: float) -> str:
    """Return a readable pass/fail result for a WCAG threshold."""
    return "PASS" if ratio >= threshold else "FAIL"


def main() -> None:
    """Parse arguments and print contrast classifications."""
    parser = argparse.ArgumentParser(
        description="Calculate WCAG contrast for two hexadecimal sRGB colors."
    )
    parser.add_argument("foreground", type=parse_color)
    parser.add_argument("background", type=parse_color)
    args = parser.parse_args()

    ratio = contrast_ratio(args.foreground, args.background)
    print(f"Contrast ratio: {ratio:.2f}:1")
    print(f"WCAG AA body text (4.5:1): {result(ratio, 4.5)}")
    print(f"WCAG AA large text (3:1): {result(ratio, 3.0)}")
    print(f"WCAG AA meaningful non-text (3:1): {result(ratio, 3.0)}")


if __name__ == "__main__":
    main()
