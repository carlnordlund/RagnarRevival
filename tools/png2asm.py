#!/usr/bin/env python3
"""
PNG to ZX Spectrum Assembly Converter

Converts PNG images to Z80 assembly data for ZX Spectrum development.
Handles sprites, tiles, and full screens.

Usage:
    python png2asm.py input.png output.asm --label SPRITE_NAME
    python png2asm.py tiles.png tiles.asm --tileset 16x16 --label TILES
    python png2asm.py player.png player.asm --preshifted --label PLAYER

Requirements:
    pip install pillow
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: PIL (Pillow) not installed.")
    print("Install with: pip install pillow")
    sys.exit(1)


class ZXSpectrumConverter:
    """Converts images to ZX Spectrum format."""

    # ZX Spectrum colors (RGB values)
    COLORS = {
        (0, 0, 0): 0,        # Black
        (0, 0, 255): 1,      # Blue
        (255, 0, 0): 2,      # Red
        (255, 0, 255): 3,    # Magenta
        (0, 255, 0): 4,      # Green
        (0, 255, 255): 5,    # Cyan
        (255, 255, 0): 6,    # Yellow
        (255, 255, 255): 7,  # White
    }

    # Bright versions (approximate)
    BRIGHT_COLORS = {
        (0, 0, 0): 0,        # Black (same)
        (0, 0, 215): 1,      # Blue (bright)
        (215, 0, 0): 2,      # Red (bright)
        (215, 0, 215): 3,    # Magenta (bright)
        (0, 215, 0): 4,      # Green (bright)
        (0, 215, 215): 5,    # Cyan (bright)
        (215, 215, 0): 6,    # Yellow (bright)
        (215, 215, 215): 7,  # White (bright)
    }

    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixel_data = []
        self.attr_data = []

    def nearest_color(self, rgb):
        """Find nearest ZX Spectrum color."""
        r, g, b = rgb[:3]  # Ignore alpha

        # Check for exact match in normal colors
        if rgb in self.COLORS:
            return self.COLORS[rgb], False

        # Check for exact match in bright colors
        if rgb in self.BRIGHT_COLORS:
            return self.BRIGHT_COLORS[rgb], True

        # Find nearest color (simple distance)
        min_dist = float('inf')
        nearest = 0
        bright = False

        for color_rgb, color_num in self.COLORS.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb))
            if dist < min_dist:
                min_dist = dist
                nearest = color_num
                bright = False

        for color_rgb, color_num in self.BRIGHT_COLORS.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb))
            if dist < min_dist:
                min_dist = dist
                nearest = color_num
                bright = True

        return nearest, bright

    def convert_8x8_block(self, img, x, y):
        """Convert an 8x8 pixel block to ZX Spectrum format."""
        # Extract pixel data
        pixels = []
        colors_used = set()

        for py in range(y, min(y + 8, img.height)):
            for px in range(x, min(x + 8, img.width)):
                if px < img.width and py < img.height:
                    pixel = img.getpixel((px, py))
                    if isinstance(pixel, int):  # Grayscale
                        pixel = (pixel, pixel, pixel)
                    color, bright = self.nearest_color(pixel)
                    colors_used.add((color, bright))
                    pixels.append(color)
                else:
                    pixels.append(0)  # Black for out of bounds

        # Determine INK and PAPER from most common colors
        if len(colors_used) == 0:
            ink, paper = 7, 0  # White on black default
            bright = False
        elif len(colors_used) == 1:
            (ink, bright) = list(colors_used)[0]
            paper = 0
        else:
            # Use two most common colors
            color_counts = {}
            for color_bright in colors_used:
                count = pixels.count(color_bright[0])
                color_counts[color_bright] = count

            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            (paper, bright1) = sorted_colors[0][0]
            (ink, bright2) = sorted_colors[1][0] if len(sorted_colors) > 1 else (7, False)
            bright = bright1 or bright2

        # Convert to binary data (8 bytes for 8x8 block)
        binary_data = []
        for row in range(8):
            byte_val = 0
            for col in range(8):
                pixel_idx = row * 8 + col
                pixel_color = pixels[pixel_idx] if pixel_idx < len(pixels) else 0
                # If pixel matches INK, set bit to 1
                if pixel_color == ink or (pixel_color != paper and pixel_color != 0):
                    byte_val |= (1 << (7 - col))
            binary_data.append(byte_val)

        # Create attribute byte
        attr = ink | (paper << 3)
        if bright:
            attr |= 0x40  # BRIGHT bit

        return binary_data, attr

    def convert_image(self, image_path):
        """Convert entire image to ZX Spectrum format."""
        img = Image.open(image_path)

        # Convert to RGB if needed
        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')

        self.width = img.width
        self.height = img.height

        # Convert in 8x8 blocks
        char_width = (self.width + 7) // 8
        char_height = (self.height + 7) // 8

        self.pixel_data = []
        self.attr_data = []

        for char_y in range(char_height):
            for char_x in range(char_width):
                pixels, attr = self.convert_8x8_block(
                    img,
                    char_x * 8,
                    char_y * 8
                )
                self.pixel_data.extend(pixels)
                self.attr_data.append(attr)

        return char_width, char_height

    def generate_asm(self, label, preshifted=False):
        """Generate Z80 assembly code."""
        lines = []

        lines.append(f"; Auto-generated sprite data")
        lines.append(f"; Size: {self.width}x{self.height} pixels")
        lines.append("")

        # Generate pixel data
        if preshifted:
            # Generate 8 shifted versions
            for shift in range(8):
                lines.append(f"{label}_SHIFT{shift}:")
                shifted_data = self._shift_sprite_data(self.pixel_data, shift)
                lines.extend(self._format_bytes(shifted_data))
                lines.append("")
        else:
            lines.append(f"{label}:")
            lines.extend(self._format_bytes(self.pixel_data))
            lines.append("")

        # Generate attribute data
        lines.append(f"{label}_ATTRS:")
        lines.extend(self._format_bytes(self.attr_data))
        lines.append("")

        # Add constants
        char_width = (self.width + 7) // 8
        char_height = (self.height + 7) // 8
        lines.append(f"{label}_WIDTH:  EQU {char_width}")
        lines.append(f"{label}_HEIGHT: EQU {char_height}")
        lines.append("")

        return "\n".join(lines)

    def _shift_sprite_data(self, data, shift):
        """Shift sprite data by N pixels for pre-shifted sprites."""
        if shift == 0:
            return data

        shifted = []
        carry = 0

        for byte in data:
            new_byte = ((byte << shift) | carry) & 0xFF
            carry = byte >> (8 - shift)
            shifted.append(new_byte)

        return shifted

    def _format_bytes(self, data, bytes_per_line=8):
        """Format bytes as DEFB statements."""
        lines = []

        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            byte_strs = [f"${b:02X}" for b in chunk]
            lines.append(f"    DEFB {', '.join(byte_strs)}")

        return lines


def main():
    parser = argparse.ArgumentParser(
        description='Convert PNG images to ZX Spectrum assembly data'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Input PNG file'
    )

    parser.add_argument(
        'output',
        type=str,
        help='Output ASM file'
    )

    parser.add_argument(
        '--label',
        type=str,
        default='SPRITE_DATA',
        help='Label name for the sprite data (default: SPRITE_DATA)'
    )

    parser.add_argument(
        '--preshifted',
        action='store_true',
        help='Generate pre-shifted versions (8x data for smooth scrolling)'
    )

    parser.add_argument(
        '--tileset',
        type=str,
        help='Treat as tileset (e.g., 16x16 for 16x16 tiles)'
    )

    args = parser.parse_args()

    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)

    # Convert image
    print(f"Converting {args.input}...")

    converter = ZXSpectrumConverter()
    char_width, char_height = converter.convert_image(args.input)

    print(f"  Size: {converter.width}x{converter.height} pixels")
    print(f"  Characters: {char_width}x{char_height}")

    # Generate assembly
    asm_code = converter.generate_asm(args.label, args.preshifted)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(asm_code)

    print(f"  Wrote {len(asm_code)} bytes to {args.output}")

    if args.preshifted:
        print(f"  Generated 8 pre-shifted versions")

    print("Done!")


if __name__ == '__main__':
    main()
