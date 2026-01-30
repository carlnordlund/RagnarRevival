# Isometric Scrolling: Technical Details

## Tile Size Considerations

### Option 1: 16×16 Pixels (Recommended)

**Dimensions:**
- Width: 16 pixels = 2 bytes per line
- Height: 16 pixels
- Memory: 32 bytes per tile

**Isometric diamond shape:**
```
    ▓▓▓▓
  ▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓
    ▓▓▓▓
```

**Pros:**
- Fast drawing (only 32 bytes)
- 64 unique tiles fit in 2KB
- Proven in Knight Lore, Head Over Heels
- Good screen coverage

**Cons:**
- Less detailed graphics
- Chunkier appearance

### Option 2: 16×24 Pixels (Good Compromise)

**Dimensions:**
- Width: 16 pixels = 2 bytes per line
- Height: 24 pixels
- Memory: 48 bytes per tile

**Taller isometric diamond:**
```
      ▓▓
    ▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓▓▓
    ▓▓▓▓▓▓
      ▓▓
```

**Pros:**
- Better depth perception
- More vertical detail
- Still reasonably fast
- 42 unique tiles in 2KB

**Cons:**
- 50% more memory than 16×16
- Slower to draw

### Option 3: 32×24 Pixels (Detailed)

**Dimensions:**
- Width: 32 pixels = 4 bytes per line
- Height: 24 pixels
- Memory: 96 bytes per tile

**Large isometric diamond:**
```
        ▓▓▓▓
      ▓▓▓▓▓▓▓▓
    ▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    ▓▓▓▓▓▓▓▓▓▓▓▓
      ▓▓▓▓▓▓▓▓
        ▓▓▓▓
```

**Pros:**
- Highly detailed graphics
- Very impressive visually
- Smooth diagonals

**Cons:**
- 3x memory vs 16×16
- Only 21 unique tiles in 2KB
- Much slower to draw
- Fewer tiles visible on screen

### Screen Coverage Comparison

**ZX Spectrum screen: 256×192 pixels**

**With 16×16 tiles:**
- Horizontal: 256/16 = 16 tiles wide
- Vertical: 192/16 = 12 tiles tall
- Visible: ~8×8 isometric grid

**With 16×24 tiles:**
- Horizontal: 256/16 = 16 tiles wide
- Vertical: 192/24 = 8 tiles tall
- Visible: ~7×7 isometric grid

**With 32×24 tiles:**
- Horizontal: 256/32 = 8 tiles wide
- Vertical: 192/24 = 8 tiles tall
- Visible: ~4×4 isometric grid (too small!)

**Recommendation: 16×16 or 16×24**

## Isometric Scrolling Math

### World Space to Screen Space

Standard isometric transformation:
```
Screen_X = (World_X - World_Y) × Tile_Width / 2
Screen_Y = (World_X + World_Y) × Tile_Height / 4
```

For 16×16 tiles:
```
Screen_X = (World_X - World_Y) × 8
Screen_Y = (World_X + World_Y) × 4
```

### Movement Vectors

**World movement → Screen delta:**

```asm
; North (Y decreases in world)
; Screen moves: +X, -Y
Move_North:
    Screen_DX = +8 pixels   ; Right
    Screen_DY = -4 pixels   ; Up
    Ratio: 2:1

; East (X increases in world)
; Screen moves: +X, +Y
Move_East:
    Screen_DX = +8 pixels   ; Right
    Screen_DY = +4 pixels   ; Down
    Ratio: 2:1

; South (Y increases in world)
; Screen moves: -X, +Y
Move_South:
    Screen_DX = -8 pixels   ; Left
    Screen_DY = +4 pixels   ; Down
    Ratio: 2:1

; West (X decreases in world)
; Screen moves: -X, -Y
Move_West:
    Screen_DX = -8 pixels   ; Left
    Screen_DY = -4 pixels   ; Up
    Ratio: 2:1
```

### Visual Diagram

```
Screen space (isometric view):

        N (↗)
       /
      /  +8X, -4Y
     /
    /
   W   Player   E
(↖)  ← · ·  → (↘)
 \      @      /
  \           /
   \         / +8X, +4Y
    \       /
     \     /
      \   /
       \ /
        S (↙)
     -8X, +4Y

All movements have 2:1 ratio (horizontal:vertical)
```

### Smooth Scrolling Increments

**Tile-based (jump full tile):**
```
North: Camera += (+16X, -8Y)
East:  Camera += (+16X, +8Y)
South: Camera += (-16X, +8Y)
West:  Camera += (-16X, -8Y)
```

**Smooth scrolling (2-pixel increments):**
```
North: Camera += (+2X, -1Y) × 8 frames = full tile
East:  Camera += (+2X, +1Y) × 8 frames = full tile
South: Camera += (-2X, +1Y) × 8 frames = full tile
West:  Camera += (-2X, -1Y) × 8 frames = full tile
```

**Why 2-pixel minimum?**
- Isometric 2:1 ratio requires even horizontal movement
- 1 pixel vertical = 2 pixels horizontal
- Can't do half-pixels on ZX Spectrum!

### Sub-Pixel Scrolling

For buttery-smooth motion:
```
Frame 1: Offset (+0, +0)
Frame 2: Offset (+2, +1)   ; 2 pixels right, 1 down
Frame 3: Offset (+4, +2)   ; 4 pixels right, 2 down
Frame 4: Offset (+6, +3)   ; 6 pixels right, 3 down
Frame 5: Offset (+8, +4)   ; 8 pixels right, 4 down (half tile)
...
Frame 8: Offset (+16, +8)  ; Full tile, reset offset
```

## Edge-Based Optimization Reality Check

### When It Helps Most

**1. Uniform corridors:**
```
████████████████
████████████████  ← 16 tiles, all same wall
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← 16 tiles, all same floor
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

Scrolling right:
- Redraw: Left edge (1 col) + right edge (1 col) = 4 tiles
- Skip: Middle 14 columns (56 tiles)
- Speedup: 60/4 = 15x !
```

**2. Large rooms:**
```
████████████████████
█                  █
█  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  █  ← All same floor
█  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  █
█  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  █
█                  █
████████████████████

Scrolling: Only wall edges + floor boundaries
Speedup: 4-5x
```

### When It Helps Less

**Varied floor tiles:**
```
▓▓▒▒░░≈≈▓▓▒▒░░≈≈  ← Every tile different pattern
```

If each stone tile has unique cracks/pattern:
- Can't skip drawing
- Must redraw each tile's unique graphic
- Only speedup: screen edge culling (1.5-2x)

### Practical Approach

**Design uniform tileable patterns:**

```
Stone floor - all tiles identical:
▓░▓░▓░▓░▓░▓░▓░▓░
░▓░▓░▓░▓░▓░▓░▓░▓
▓░▓░▓░▓░▓░▓░▓░▓░  ← Pattern repeats seamlessly

When scrolling:
- Pixel data at any position is same
- Just shifted in screen buffer
- Can use fast block copy for middle
- Only edges need "real" drawing
```

**Different floor TYPES, not unique tiles:**

```
Area 1: All stone (same pattern)
Area 2: All wood (same pattern)
Boundary: Stone-to-wood edge (redraw)

Not: Every stone tile has unique pattern
```

### Realistic Performance

**Best case (long uniform corridors):**
- 64 tiles visible
- Scroll right: 8 edge tiles redrawn
- Speedup: 8x

**Average case (mixed dungeon):**
- Some uniform areas
- Some varied areas
- Typical: 20 tiles redrawn
- Speedup: 3x

**Worst case (no optimization):**
- Full screen redraw
- 64 tiles
- Speedup: 1x (but can still use dirty rectangles)

**Even 3x is huge** for ZX Spectrum!

## Implementation Strategy

### Phase 1: Simple Tile-Based (Start Here)

```asm
; Move player north (in world)
MovePlayerNorth:
    ; Update world position
    LD HL, (PlayerWorldY)
    DEC HL
    LD (PlayerWorldY), HL

    ; Camera follows (tile-based)
    LD HL, (CameraWorldY)
    DEC HL
    LD (CameraWorldY), HL

    ; Calculate screen tiles to redraw
    ; North = bottom row disappears, top row appears
    CALL MarkBottomRowClean
    CALL MarkTopRowDirty

    ; Redraw dirty tiles
    CALL RedrawDirtyTiles

    RET
```

**Pros:**
- Simple to implement
- Immediate results
- Jump full tile at a time

**Cons:**
- Jerky movement
- Not smooth

### Phase 2: Smooth 2-Pixel Scrolling

```asm
; Smooth north movement
MovePlayerNorthSmooth:
    LD A, (ScrollPhase)
    CP 8
    JR Z, .NewTile

    ; Sub-tile scrolling
    INC A
    LD (ScrollPhase), A

    ; Adjust pixel offset
    LD HL, (PixelOffsetX)
    INC HL
    INC HL              ; +2 pixels X
    LD (PixelOffsetX), HL

    LD HL, (PixelOffsetY)
    DEC HL              ; -1 pixel Y
    LD (PixelOffsetY), HL

    ; Redraw with offset
    CALL RedrawWithOffset

    RET

.NewTile:
    ; Completed full tile
    XOR A
    LD (ScrollPhase), A

    ; Update world position
    LD HL, (PlayerWorldY)
    DEC HL
    LD (PlayerWorldY), HL

    ; Mark new tiles dirty
    CALL MarkTopRowDirty

    RET
```

**Pros:**
- Smooth motion
- Professional feel
- 2:1 ratio maintained

**Cons:**
- More complex
- Requires pre-shifted sprites
- More CPU time

### Phase 3: Edge-Based Optimization

```asm
; Mark only edge tiles dirty
MarkEdgeTilesDirty:
    ; After north scroll, check top row
    LD B, 8             ; 8 columns
    LD C, 0             ; Top row

.Loop:
    ; Get tile type at this position
    PUSH BC
    CALL GetTileType
    LD D, A             ; Save type

    ; Get tile below
    INC C
    CALL GetTileType

    ; Different type?
    CP D
    JR Z, .Same

    ; Different = edge, mark dirty
    CALL MarkTileDirty

.Same:
    POP BC
    INC B
    LD A, B
    CP 8
    JR NZ, .Loop

    RET
```

**Pros:**
- Fast (only draws what changed)
- Enables smooth scrolling on limited hardware
- Works great with uniform areas

**Cons:**
- Complex edge detection
- Less benefit with varied tiles

## Memory Optimization

### Tile Data Organization

```
For 16×16 tiles with 32 bytes each:

Tile_Wall:
    DEFB %11111111, %11111111
    DEFB %11110000, %00001111
    DEFB %11100000, %00000111
    ; ... 16 lines total
    ; 32 bytes

Tile_Floor_Stone:
    DEFB %10101010, %10101010
    DEFB %01010101, %01010101
    ; ... repeating pattern
    ; 32 bytes

Total for 32 tile types:
32 tiles × 32 bytes = 1024 bytes (1KB)
```

### Screen Position Lookup Tables

Pre-calculate screen addresses:

```asm
; Table of screen line addresses
; 192 lines × 2 bytes = 384 bytes
ScreenLineTable:
    DEFW $4000, $4001, $4002, ...

; Table of attribute addresses
; 192 lines × 2 bytes = 384 bytes
AttrLineTable:
    DEFW $5800, $5820, $5840, ...

Total: 768 bytes
```

### Per-Pixel Shift Tables (For Smooth Scrolling)

If using pre-shifted sprites:

```asm
; 8 shifts of each tile
; 32 tile types × 8 shifts × 32 bytes = 8KB

Tile_Floor_Stone_Shift0:  ; No shift
Tile_Floor_Stone_Shift1:  ; 1 pixel left
Tile_Floor_Stone_Shift2:  ; 2 pixels left
; ...
Tile_Floor_Stone_Shift7:  ; 7 pixels left
```

**Trade-off:** 8KB for instant pre-shifted sprites vs calculating shifts at runtime

## Recommendation

### For Ragnar Revival / Sword of Fargoal:

**Start with:**
- 16×16 pixel tiles (proven, fast)
- Tile-based scrolling (8-pixel jumps)
- Basic edge detection (uniform floor optimization)

**Then add:**
- Smooth 2-pixel scrolling if performance allows
- Pre-shifted sprites if memory allows (probably not worth it)
- Sub-pixel camera offset for smoothness

**Avoid:**
- 32×24 tiles (too expensive)
- Unique graphics per tile instance (kills optimization)
- 1-pixel scrolling (impossible with 2:1 ratio)

### Expected Performance

With 16×16 tiles and edge-based optimization:
- Best case: 60+ FPS (simple corridors)
- Average: 30-35 FPS (mixed areas)
- Worst: 20-25 FPS (complex scenes)

**All very playable on ZX Spectrum!**
