# Graphics Workflow for ZX Spectrum Development

## Overview

Modern ZX Spectrum development lets you create graphics in modern tools (PNG files) and automatically convert them to Z80 assembly data at build time.

## The Graphics Pipeline

```
Create Graphics          Convert to ZX        Include in Code
(Modern Tools)      →    (Build Time)    →    (Assembly)

player.png          →    player_sprite.asm  →  INCLUDE "player_sprite.asm"
tiles.png           →    tiles.asm          →  LD HL, TILE_DATA
```

## ZX Spectrum Graphics Format

### Screen Layout

**Resolution**: 256 x 192 pixels

**Memory Structure**:
- **Pixels**: $4000-$57FF (6144 bytes)
  - 1 bit per pixel (monochrome per 8x8 cell)
  - Organized in thirds (not linear!)
- **Attributes**: $5800-$5AFF (768 bytes)
  - 1 byte per 8x8 character cell
  - Defines INK (foreground) and PAPER (background) colors

### Attribute Byte Format

```
Bit:  7     6     5  4  3     2  1  0
      FLASH BRIGHT PAPER    INK

FLASH: 0=steady, 1=flashing
BRIGHT: 0=dim, 1=bright
PAPER: Background color (0-7)
INK: Foreground color (0-7)
```

### Colors

```
0 = Black
1 = Blue
2 = Red
3 = Magenta
4 = Green
5 = Cyan
6 = Yellow
7 = White
```

With BRIGHT bit: 8 colors × 2 intensities = 16 total colors

## Recommended Graphics Tools

### Native ZX Spectrum Tools

1. **ZX Paintbrush**
   - Website: https://zxart.ee/eng/software/tool/graphics-editor/zx-paintbrush/
   - Authentic Spectrum graphics editor
   - Exports .scr files
   - Handles attributes correctly

2. **SevenuP** (Sprite Editor)
   - Website: http://www.seasip.info/Unix/SevenuP/
   - Cross-platform
   - Sprite and tile editor
   - Exports binary, C, or ASM

3. **McCanvas**
   - Modern web-based editor
   - Export to various formats
   - Good for quick sprites

### Modern Tools

1. **Aseprite** ($20 or compile free)
   - Excellent for pixel art
   - Export to PNG
   - Animation support

2. **GIMP** (Free)
   - Use indexed color mode
   - Limit to 16 colors
   - Export to PNG

3. **GraphicsGale** (Free)
   - Windows pixel art tool
   - Export to PNG

## Graphics Conversion Tools

### Option 1: png2scr (Python)

Simple tool to convert PNG to Spectrum screen format:

```bash
# Install
pip install png2scr

# Convert
png2scr input.png output.scr

# Convert to binary data
png2scr input.png output.bin --binary
```

### Option 2: Image2ZXSpec (Java)

More advanced conversion with dithering:

```bash
java -jar Image2ZXSpec.jar input.png output.scr
```

### Option 3: Custom Python Converter (Recommended)

We'll create a custom tool specifically for your workflow that:
- Converts PNG to ASM format
- Handles sprites of any size
- Generates proper DEFB statements
- Includes attribute data
- Adds labels automatically

## Workflow Example

### Step 1: Create Graphics

Use Aseprite or GIMP to create `player.png`:
- 16x16 pixels
- 2 colors (black and white, or your INK/PAPER)
- Save as PNG

### Step 2: Add to Project

```
project/
├── assets/
│   └── graphics/
│       └── sprites/
│           └── player.png
```

### Step 3: Build Converts Automatically

Your build script runs:

```bash
# Convert graphics
python tools/png2asm.py \
    assets/graphics/sprites/player.png \
    src/data/player_sprite.asm \
    --label PLAYER_SPRITE \
    --width 16 \
    --height 16
```

Generates `src/data/player_sprite.asm`:

```asm
; Auto-generated from assets/graphics/sprites/player.png
; Size: 16x16 pixels (2x2 characters)

PLAYER_SPRITE:
    ; Row 0
    DEFB %00011000, %00011000
    DEFB %00111100, %00111100
    DEFB %01111110, %01111110
    DEFB %11111111, %11111111
    DEFB %11111111, %11111111
    DEFB %01111110, %01111110
    DEFB %00111100, %00111100
    DEFB %00011000, %00011000
    ; Row 1
    DEFB %00011000, %00011000
    DEFB %00111100, %00111100
    DEFB %01011010, %01011010
    DEFB %11111111, %11111111
    DEFB %11111111, %11111111
    DEFB %01111110, %01111110
    DEFB %00111100, %00111100
    DEFB %00011000, %00011000

PLAYER_SPRITE_ATTRS:
    DEFB $47, $47       ; INK 7 (white), PAPER 0 (black), BRIGHT
    DEFB $47, $47

PLAYER_SPRITE_WIDTH:  EQU 2  ; In characters
PLAYER_SPRITE_HEIGHT: EQU 2  ; In characters
```

### Step 4: Use in Code

```asm
    INCLUDE "src/data/player_sprite.asm"

DrawPlayer:
    LD HL, PLAYER_SPRITE
    LD DE, (ScreenPos)
    LD B, PLAYER_SPRITE_HEIGHT
    LD C, PLAYER_SPRITE_WIDTH
    CALL DrawSprite
    RET
```

## Sprite Drawing Routine

Basic sprite drawing routine:

```asm
; Draw sprite to screen
; Input:
;   HL = sprite data address
;   DE = screen address
;   B = height in characters
;   C = width in characters

DrawSprite:
    PUSH BC             ; Save height

.RowLoop:
    PUSH DE             ; Save screen position
    PUSH BC             ; Save width

.CharLoop:
    ; Draw 8 lines of current character
    LD B, 8
.LineLoop:
    LD A, (HL)          ; Get sprite byte
    LD (DE), A          ; Draw to screen
    INC HL              ; Next sprite byte

    ; Move to next screen line
    INC D               ; Next pixel row (works for first 8 lines)
    DJNZ .LineLoop

    ; Move to next character
    POP BC
    POP DE
    INC E               ; Next character position
    PUSH DE
    PUSH BC

    DEC C
    JR NZ, .CharLoop

    ; Move to next character row
    POP BC
    POP DE

    ; Calculate next character row (complex on Spectrum!)
    LD A, D
    SUB 8               ; Back to top of character
    AND $F8
    LD D, A

    LD A, E
    ADD A, $20          ; Next character row
    LD E, A
    JR NC, .NoCarry
    LD A, D
    ADD A, $08
    LD D, A
.NoCarry:

    POP BC
    DJNZ .RowLoop
    RET
```

## Pre-Shifted Sprites (Advanced)

For smooth pixel scrolling, pre-shift sprites to all 8 alignments:

```asm
; Generate all 8 shifts of a sprite
; Original: %11110000
; Shift 0:  %11110000
; Shift 1:  %01111000
; Shift 2:  %00111100
; Shift 3:  %00011110
; ...

; This trades memory (8x sprite data) for speed
```

The conversion tool can generate these automatically:

```bash
python tools/png2asm.py \
    player.png \
    player_sprite.asm \
    --preshifted
```

## Tiles vs Sprites

### Tiles
- Background elements
- Aligned to 8x8 character grid
- Don't need pre-shifting
- Examples: walls, floors, blocks

### Sprites
- Moving objects
- Can be positioned at any pixel
- Benefit from pre-shifting
- Examples: player, enemies, bullets

## Complete Build Integration

### tools/convert-graphics.sh

```bash
#!/bin/bash

echo "Converting graphics..."

# Sprites (pre-shifted for smooth movement)
python3 tools/png2asm.py \
    assets/graphics/sprites/player.png \
    src/data/player_sprite.asm \
    --label PLAYER_SPRITE \
    --preshifted

python3 tools/png2asm.py \
    assets/graphics/sprites/enemy.png \
    src/data/enemy_sprite.asm \
    --label ENEMY_SPRITE \
    --preshifted

# Tiles (not pre-shifted, grid-aligned)
python3 tools/png2asm.py \
    assets/graphics/tiles/blocks.png \
    src/data/blocks.asm \
    --label BLOCK_TILES \
    --tileset 16x16

# Screens
python3 tools/png2scr.py \
    assets/graphics/screens/title.png \
    src/data/title_screen.asm \
    --label TITLE_SCREEN

echo "Done!"
```

### .vscode/tasks.json

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Convert Graphics",
            "type": "shell",
            "command": "bash",
            "args": ["tools/convert-graphics.sh"],
            "problemMatcher": []
        },
        {
            "label": "Build",
            "type": "shell",
            "command": "sjasmplus",
            "args": [
                "${workspaceFolder}/src/main.asm",
                "--lst",
                "--raw=${workspaceFolder}/build/output.bin"
            ],
            "dependsOn": ["Convert Graphics"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```

Now `Ctrl+Shift+B` converts graphics AND builds in one step!

## Tips for Creating Spectrum Graphics

### 1. Respect the Attribute Clash

Remember: colors are per 8x8 character, not per pixel!

**Good**: Design sprites that work within 8x8 color blocks
**Bad**: Expecting per-pixel color

### 2. Use BRIGHT Wisely

BRIGHT doubles your palette from 8 to 16 colors.

### 3. Embrace Limitations

The restrictions create the iconic Spectrum look!

### 4. Test on Real Hardware/Emulator

What looks good in Aseprite might clash on real Spectrum.

### 5. Study Classic Games

Look at **Knightlore**, **Head Over Heels**, **Starquake** for inspiration.

## Example Graphics Project Structure

```
project/
├── assets/
│   └── graphics/
│       ├── sprites/
│       │   ├── player/
│       │   │   ├── walk_01.png
│       │   │   ├── walk_02.png
│       │   │   └── walk_03.png
│       │   ├── enemies/
│       │   │   ├── skeleton.png
│       │   │   └── bat.png
│       │   └── items/
│       │       ├── sword.png
│       │       └── gold.png
│       ├── tiles/
│       │   ├── dungeon_floor.png
│       │   ├── dungeon_wall.png
│       │   └── door.png
│       └── screens/
│           ├── title.png
│           └── gameover.png
├── src/
│   └── data/
│       ├── sprites_player.asm      # Generated
│       ├── sprites_enemies.asm     # Generated
│       ├── tiles.asm               # Generated
│       └── screens.asm             # Generated
└── tools/
    ├── png2asm.py
    ├── png2scr.py
    └── convert-graphics.sh
```

## Animated Sprites

For animations, create multiple frames:

```
player_walk_01.png → PLAYER_WALK_1
player_walk_02.png → PLAYER_WALK_2
player_walk_03.png → PLAYER_WALK_3
player_walk_04.png → PLAYER_WALK_4
```

In code:

```asm
; Animation frame table
PlayerWalkFrames:
    DEFW PLAYER_WALK_1
    DEFW PLAYER_WALK_2
    DEFW PLAYER_WALK_3
    DEFW PLAYER_WALK_4

; Current frame
PlayerFrame: DEFB 0

DrawPlayerAnimated:
    LD A, (PlayerFrame)
    AND $03             ; 0-3
    ADD A, A            ; * 2 for word offset
    LD HL, PlayerWalkFrames
    LD D, 0
    LD E, A
    ADD HL, DE          ; HL = address of frame pointer
    LD E, (HL)
    INC HL
    LD D, (HL)          ; DE = sprite data
    EX DE, HL           ; HL = sprite data

    ; Draw sprite at HL
    CALL DrawSprite

    ; Advance frame
    LD A, (PlayerFrame)
    INC A
    LD (PlayerFrame), A
    RET
```

## Color Planning

Create a color palette document:

```
Game Palette:
- Player: INK 7 (white), PAPER 0 (black), BRIGHT 1
- Walls: INK 6 (yellow), PAPER 0 (black), BRIGHT 0
- Floor: INK 2 (red), PAPER 0 (black), BRIGHT 0
- Enemy 1: INK 2 (red), PAPER 0 (black), BRIGHT 1
- Enemy 2: INK 4 (green), PAPER 0 (black), BRIGHT 1
- Gold: INK 6 (yellow), PAPER 0 (black), BRIGHT 1
- Sword: INK 7 (white), PAPER 4 (green), BRIGHT 1
```

## Next Steps

1. **Install Aseprite or GIMP** for creating graphics
2. **Create test sprite** (16x16 simple character)
3. **Convert to ASM** using the tool we'll create
4. **Include in code** and display it
5. **Iterate** - refine your workflow

I'll create the `png2asm.py` converter tool in the next step. This will make your graphics workflow completely automated and modern while targeting classic hardware!

The combination of modern tools + automated conversion + classic Z80 code is the perfect development setup for 2026 Spectrum development! 🎨
