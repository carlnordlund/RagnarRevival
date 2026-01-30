# 3D Isometric Engine Design

This document explores design ideas for the Ragnar Revival 3D isometric engine, building on the original 2-layer demo.

## Original Demo Architecture

The current demo (`Ragnar (demo).z80`) implements:
- **Grid:** 8x8 blocks
- **Layers:** 2 layers of blocks
- **Rendering:** Isometric perspective
- **Platform:** ZX Spectrum 48K

## Enhanced 8-Layer Engine Concept

### Design Goals

1. **8 layers** instead of 2 for true 3D depth
2. **Efficient rendering** on 3.5MHz Z80
3. **Smooth scrolling** (if possible)
4. **Dynamic block updates**
5. **Collision detection**

### Memory Considerations

ZX Spectrum 48K memory layout:
```
$0000-$3FFF: ROM (16KB)
$4000-$57FF: Screen pixels (6144 bytes)
$5800-$5AFF: Screen attributes (768 bytes)
$5B00-$5CCB: System variables
$5CCB-$FFFF: Free RAM (~42KB)
```

Available for program: ~42KB for code, data, and runtime variables.

### Data Structure Options

#### Option 1: Simple Array (8x8x8)
```
Total blocks: 8 * 8 * 8 = 512 blocks
Storage: 1 byte per block type = 512 bytes
```

Pros:
- Simple indexing
- Fast lookups
- Easy to understand

Cons:
- Sparse data wastes memory (empty air blocks)
- Large for bigger worlds

#### Option 2: Sparse Storage
```
Only store non-empty blocks
Each entry: X, Y, Z, Type = 4 bytes
Max blocks: ~1000 with 4KB allocation
```

Pros:
- Efficient for sparse worlds
- Can store more world data

Cons:
- Slower lookups
- More complex code

#### Option 3: Column-Based (Recommended)
```
For each X,Y position: store column of blocks
8x8 = 64 columns
Each column: up to 8 blocks
```

Pros:
- Natural for isometric rendering
- Good balance of speed/memory
- Easy to check "what's above/below"

Cons:
- Fixed column height

### Isometric Rendering Math

#### Coordinate Transformation

Convert 3D world coordinates (X, Y, Z) to 2D screen coordinates:

```
Screen_X = (X - Y) * TILE_WIDTH / 2
Screen_Y = (X + Y) * TILE_HEIGHT / 4 - Z * TILE_HEIGHT / 2
```

For ZX Spectrum with 16x16 pixel tiles:
```
Screen_X = (X - Y) * 8
Screen_Y = (X + Y) * 4 - Z * 8
```

#### Rendering Order (Painter's Algorithm)

To ensure proper visibility, render from back to front:

```
For Z = 0 to 7:
    For Y = 7 to 0:
        For X = 0 to 7:
            If block exists at (X, Y, Z):
                Draw block
```

This ensures closer blocks overdraw farther ones.

### Optimization Techniques

#### 1. Lookup Tables

Pre-calculate screen positions:
```asm
; Table of screen X positions
ScreenXTable:
    ; For each (X-Y) value from -7 to +7
    DEFB 0, 8, 16, 24, 32, 40, 48, 56, ...

; Table of screen Y positions
ScreenYTable:
    ; Pre-calculated Y positions
    DEFW $4000, $4001, $4002, ...
```

#### 2. Block Visibility Culling

Don't draw blocks that are completely hidden:
- Check if block above is solid
- Check if surrounded by solid blocks
- Use dirty rectangles for updates

#### 3. Sprite Pre-shifting

Pre-shift sprite data for all 8 pixel alignments:
- Spectrum screen is byte-aligned
- Pre-calculate all 8 bit-shift variants
- Trade 8x memory for speed

#### 4. Partial Updates

Only redraw changed blocks:
- Keep track of modified blocks
- Mark screen regions as dirty
- Selective redraw

### Example Block Types

```asm
BLOCK_EMPTY     EQU 0   ; Air/nothing
BLOCK_WALL      EQU 1   ; Solid wall
BLOCK_FLOOR     EQU 2   ; Floor tile
BLOCK_DOOR      EQU 3   ; Door
BLOCK_STAIRS_UP EQU 4   ; Stairs going up
BLOCK_STAIRS_DN EQU 5   ; Stairs going down
BLOCK_WATER     EQU 6   ; Water
BLOCK_TREASURE  EQU 7   ; Treasure chest
```

### Collision Detection

Simple bounding box approach:

```asm
CheckCollision:
    ; Input: player position (PX, PY, PZ)
    ; Output: Z flag set if collision

    ; Calculate grid position
    LD A, (PlayerX)
    SRL A
    SRL A               ; Divide by 4 to get grid X
    LD B, A

    LD A, (PlayerY)
    SRL A
    SRL A               ; Divide by 4 to get grid Y
    LD C, A

    LD A, (PlayerZ)
    LD D, A             ; Grid Z

    ; Look up block at (B, C, D)
    CALL GetBlock

    ; Check if solid
    CP BLOCK_EMPTY
    RET Z               ; Empty = no collision

    ; Non-empty = collision
    XOR A
    DEC A               ; Clear Z flag
    RET
```

### Sample Memory Layout

```
$5CCB-$6CCB: World data (4KB)
  - Column descriptors: 64 * 8 bytes = 512 bytes
  - Block data: ~3.5KB

$6CCB-$7CCB: Sprite data (4KB)
  - 16 block types * 256 bytes = 4KB

$7CCB-$8CCB: Screen position tables (4KB)
  - X position lookup: 256 bytes
  - Y position lookup: 2KB
  - Attribute lookup: 768 bytes
  - Misc: ~1KB

$8CCB-$FFFF: Program code (~29KB)
```

### Performance Targets

ZX Spectrum runs at 50Hz (PAL) or 60Hz (NTSC).
- Frame time: 20ms (50Hz) or 16.67ms (60Hz)
- CPU cycles per frame: 69,888 (50Hz)

Goals:
- Full screen redraw: < 2 frames (40ms)
- Partial update: < 1 frame (20ms)
- Allow time for game logic and input

### Advanced Features

#### Level Scrolling
- Shift entire view by half-tile increments
- Use screen scrolling for smooth motion
- More complex but much smoother

#### Dynamic Lighting
- Attribute changes for light/shadow
- Could use bright/dim attributes
- Torches, day/night cycle

#### Destructible Blocks
- Allow removing/adding blocks
- Procedural generation
- Dungeon building/digging

#### Multiple Viewpoints
- Top-down mode
- First-person mode (like Doom)
- Split-screen multiplayer?

## Implementation Phases

### Phase 1: Basic 8-Layer Display
- Implement column-based storage
- Render static 8x8x8 world
- No movement, just display
- **Goal:** Prove the concept works

### Phase 2: Camera Movement
- Scroll the view
- Change viewing angle
- Zoom in/out
- **Goal:** Navigate the world

### Phase 3: Player Character
- Add player sprite
- Keyboard control
- Basic collision
- **Goal:** Walk around

### Phase 4: Game Mechanics
- Doors, keys, items
- Enemies (?)
- Score, lives
- **Goal:** Make it a game

### Phase 5: Polish
- Sound effects
- Music
- Title screen
- **Goal:** Complete experience

## Performance Testing

Create benchmark programs:
```asm
; Test full screen render time
BenchmarkRender:
    LD B, 50            ; 50 frames
    LD HL, 0            ; Frame counter
.Loop:
    HALT                ; Wait for frame
    INC HL
    CALL RenderWorld    ; Your render routine
    DJNZ .Loop

    ; HL now contains time in 1/50th seconds
    RET
```

## Code Organization

Suggested file structure:
```
src/
├── main.asm            # Entry point, main loop
├── engine/
│   ├── world.asm       # World data management
│   ├── render.asm      # Rendering engine
│   ├── camera.asm      # Camera/viewport
│   └── collision.asm   # Collision detection
├── game/
│   ├── player.asm      # Player control
│   ├── entities.asm    # Game entities
│   └── logic.asm       # Game rules
├── graphics/
│   ├── blocks.asm      # Block sprite data
│   ├── sprites.asm     # Character sprites
│   └── charset.asm     # Font data
└── data/
    ├── level1.asm      # Level data
    └── tables.asm      # Lookup tables
```

## References and Inspiration

### Classic Isometric Games

- **Knight Lore** (1984) - Ultimate Play The Game
  - First major 3D isometric Spectrum game
  - Filmation engine

- **Head Over Heels** (1987) - Ocean Software
  - Two characters with different abilities
  - Excellent isometric engine

- **Batman** (1986) - Ocean Software
  - Isometric rooms
  - Good reference for rendering

### Modern Tools

- **AGD (Arcade Game Designer)** - Study its isometric mode
- **3D Construction Kit** - See how they handled it

### Technical Resources

- **ZX Spectrum Assembly Programming** tutorials
- **Isometric game development** articles
- **Z80 optimization** guides

## Questions to Explore

1. Can we do smooth sub-tile scrolling?
2. What's the maximum reasonable world size?
3. Can we do colored sprites (attribute tricks)?
4. Is parallax scrolling possible?
5. Can we compress level data further?

## Experiment Ideas

1. **Render speed test:** How fast can we draw all 512 blocks?
2. **Memory test:** How much can we fit in 48KB?
3. **Culling test:** How much does visibility culling help?
4. **Lookup test:** Pre-calc vs runtime calculation?

Start with Phase 1 and build from there. Don't try to implement everything at once!

Good luck building the next generation of Ragnar Revival!
