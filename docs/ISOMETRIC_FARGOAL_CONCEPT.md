# 3D Isometric Sword of Fargoal - Concept Document

## Vision

Create a 3D isometric version of Sword of Fargoal with:
- **Procedurally generated infinite dungeons**
- **Multiple levels** with increasing difficulty
- **Smooth scrolling** with player-centered viewport
- **Efficient rendering** using partial screen updates
- **Classic Fargoal gameplay** in isometric 3D

## Original Sword of Fargoal Mechanics

### Core Gameplay
- **Goal**: Descend through dungeon levels to find the Sword of Fargoal, then return to surface
- **Roguelike elements**: Permadeath, procedural generation, random encounters
- **Combat**: Real-time combat with monsters
- **Items**: Gold, potions, weapons, armor, magic items
- **Stairs**: Up and down between levels
- **Fog of war**: Unexplored areas are hidden
- **Time pressure**: Health decreases over time

### Key Features to Preserve
- Random dungeon layout each game
- Increasing difficulty with depth
- Item management
- Strategic combat
- Tension between exploration and survival

## Technical Challenges on ZX Spectrum

### 1. Infinite Map Generation with Limited Memory

**Problem**: 48KB RAM can't store infinite maps

**Solution**: **Chunk-based procedural generation**

#### Concept: Generate on Demand

Only generate and keep in memory what's visible plus a small buffer:

```
Memory contains:
- Current 8x8x8 visible chunk
- Adjacent chunks (for smooth scrolling)
- Random seed for entire level
```

When player moves to new area:
1. Discard chunks far from player
2. Generate new chunks based on position + seed
3. Seed ensures same position = same map layout

#### Data Structure

```asm
; Current world position (not screen position!)
WorldX:     DEFW 0      ; Player's X in world space (-32768 to +32767)
WorldY:     DEFW 0      ; Player's Y in world space
WorldZ:     DEFB 0      ; Current dungeon level (0-255)

; Random seed for this level
LevelSeed:  DEFW 0      ; Seed for procedural generation

; Loaded chunks (3x3 grid around player)
ChunkGrid:
    ; 9 chunks * 64 blocks per chunk = 576 blocks max in memory
    DEFS 576            ; Block type data
```

### 2. Procedural Generation Algorithm

Use a **deterministic pseudo-random** approach:

```asm
; Generate block at world position (X, Y, Z)
; Input: BC = X, DE = Y, A = Z
; Output: A = block type

GenerateBlock:
    ; Combine position with level seed
    LD HL, (LevelSeed)
    ADD HL, BC          ; Add X
    ADD HL, DE          ; Add Y
    ADD A, H            ; Mix with Z

    ; Simple hash function
    XOR L
    ADD A, A
    XOR H

    ; Use hash to determine block type
    AND $0F             ; 16 possible outcomes

    ; Probability distribution
    CP 12               ; 75% chance (0-11)
    JR C, .Floor        ; Floor/empty

    CP 15               ; 18.75% chance (12-14)
    JR C, .Wall         ; Wall

    ; 6.25% chance (15)
    ; Special block (door, stairs, etc.)
    JR .Special

.Floor:
    LD A, BLOCK_FLOOR
    RET

.Wall:
    LD A, BLOCK_WALL
    RET

.Special:
    ; More complex logic for special tiles
    ; Use secondary random generation
    ; ...
    RET
```

### 3. Room-Based Generation (Better Approach)

Instead of pure noise, generate **rooms and corridors** like classic roguelikes:

```
Generation steps:
1. Divide chunk into potential rooms
2. Randomly place rooms (using position+seed)
3. Connect rooms with corridors
4. Place special features (stairs, treasures)
5. Fill remaining space with walls
```

This creates recognizable dungeon architecture while still being procedural.

### 4. Smooth Scrolling Implementation

#### Concept: Player-Centered View

**Traditional approach**: Redraw entire screen when player moves

**Optimized approach**:
- Keep player sprite in screen center
- Scroll the world around them
- Only redraw edges that come into view

#### Scrolling Mechanics

```
Screen shows: 7x7 tiles (visible area)
Memory contains: 9x9 tiles (with 1-tile border)

When player moves RIGHT:
1. Shift camera position right
2. Left column scrolls off screen
3. New right column scrolls into view
4. Only redraw new right column!

Savings: 7 tiles instead of 49 tiles redrawn
```

#### Implementation Challenge: Isometric Complexity

In isometric view, scrolling is more complex than top-down:

**Top-down scrolling**: Simple pixel shifts

**Isometric scrolling**:
- Diagonal scrolling (X and Y affect both screen axes)
- Overlapping tiles
- Z-order must be maintained

#### Practical Isometric Scrolling Approach

```asm
; Smooth scrolling in isometric view
; Keep player at screen center (pixel position fixed)
; Adjust camera offset, redraw affected tiles

CameraX:    DEFW 0      ; Camera position in world (pixels)
CameraY:    DEFW 0

PlayerX:    DEFW 0      ; Player position in world (pixels)
PlayerY:    DEFW 0

; Screen constants
SCREEN_CENTER_X EQU 128
SCREEN_CENTER_Y EQU 96

MovePlayerRight:
    ; Update player world position
    LD HL, (PlayerX)
    INC HL
    INC HL              ; Move 2 pixels
    LD (PlayerX), HL

    ; Update camera to follow
    LD HL, (CameraX)
    INC HL
    INC HL
    LD (CameraX), HL

    ; Determine which tiles need redrawing
    CALL CalculateVisibleTiles
    CALL RedrawAffectedTiles

    RET
```

### 5. Efficient Partial Redraw

#### Dirty Rectangle System

Track which screen regions need updating:

```asm
; Dirty tile flags (8x8 grid)
DirtyTiles:
    DEFS 64             ; 1 byte per tile, 0=clean, 1=dirty

MarkTileDirty:
    ; Input: B = tile X, C = tile Y
    LD A, C
    ADD A, A
    ADD A, A
    ADD A, A            ; Y * 8
    ADD A, B            ; + X
    LD HL, DirtyTiles
    LD D, 0
    LD E, A
    ADD HL, DE
    LD (HL), 1          ; Mark dirty
    RET

RedrawDirtyTiles:
    LD HL, DirtyTiles
    LD B, 8             ; Y counter
.RowLoop:
    LD C, 8             ; X counter
.ColLoop:
    LD A, (HL)
    OR A
    JR Z, .Skip         ; Skip if clean

    ; Redraw this tile
    PUSH BC
    PUSH HL
    CALL DrawTile
    POP HL
    POP BC

    ; Clear dirty flag
    LD (HL), 0

.Skip:
    INC HL
    DEC C
    JR NZ, .ColLoop

    DEC B
    JR NZ, .RowLoop
    RET
```

#### Smart Isometric Redraw

In isometric, when one tile changes, overlapping tiles may also need updating:

```
When tile at (X,Y,Z) changes:
- Redraw tile at (X,Y,Z)
- If transparent, redraw tile behind at (X,Y,Z-1)
- Redraw tiles that overlap this position
```

### 6. Scrolling Strategy: Sub-Tile vs Tile-Based

**Option A: Tile-based scrolling** (Easier)
- Player moves one full tile at a time
- Redraw column/row of tiles
- Still looks smooth with good animation
- Simpler to implement

**Option B: Pixel-based scrolling** (Harder but smoother)
- Player moves pixel-by-pixel
- Partial tile visibility at edges
- Requires more complex clipping
- Much more work

**Recommendation**: Start with **tile-based**, upgrade to pixel if needed

### 7. Memory Budget

```
ZX Spectrum 48K allocation:

$4000-$5AFF: Screen (6912 bytes)
$5B00-$5CFF: System variables
$5D00-$6CFF: Chunk data (4KB)
  - 9 chunks * 64 blocks * 7 bytes/block = 4032 bytes
  - Block data: X, Y, Z, Type, Flags, Item, Enemy
$6D00-$7CFF: Sprite data (4KB)
  - 32 different tiles * 128 bytes = 4KB
$7D00-$8CFF: Screen position tables (4KB)
$8D00-$9CFF: Game state (4KB)
  - Player stats, inventory, level data
  - Entity list (monsters, items)
$9D00-$FFFF: Program code (~25KB)
```

### 8. Procedural Content Placement

#### Stairs (Exits)

Place stairs consistently based on level seed:

```asm
; Determine if stairs down exist at chunk position
; Input: BC = chunk X, DE = chunk Y
; Output: Z flag set if stairs present, HL = position

FindStairsInChunk:
    ; Hash chunk position with level seed
    LD HL, (LevelSeed)
    ADD HL, BC
    ADD HL, DE

    ; Only specific chunks have stairs
    LD A, H
    XOR L
    AND $1F             ; 1 in 32 chunks
    CP $00
    RET NZ              ; No stairs in this chunk

    ; Calculate stairs position within chunk
    LD A, H
    XOR L
    AND $07             ; 0-7
    LD B, A             ; X within chunk

    LD A, H
    XOR C
    AND $07
    LD C, A             ; Y within chunk

    ; Return position
    XOR A               ; Set Z flag (stairs found)
    RET
```

#### Gold and Items

Scatter randomly but consistently:

```asm
; Check if gold exists at specific position
; Input: BC = X, DE = Y
; Output: A = gold amount (0 = none)

GetGoldAt:
    ; Hash position
    LD HL, (LevelSeed)
    ADD HL, BC
    ADD HL, DE
    LD A, H
    XOR L

    ; 1 in 16 chance of gold
    AND $0F
    CP $00
    RET NZ              ; No gold

    ; Calculate gold amount (10-250)
    LD A, H
    XOR D
    AND $0F
    ADD A, A
    ADD A, A
    ADD A, A
    ADD A, 10           ; 10 + (0-15)*8
    RET
```

#### Monsters

```asm
; Check if monster exists at position
; Input: BC = X, DE = Y
; Output: A = monster type (0 = none)

GetMonsterAt:
    ; Hash
    LD HL, (LevelSeed)
    ADD HL, BC
    ADD HL, DE
    LD A, H
    XOR L

    ; 1 in 8 chance
    AND $07
    CP $00
    RET NZ

    ; Monster type based on level depth
    LD A, (WorldZ)      ; Current level
    AND $03             ; 4 monster types
    INC A               ; 1-4
    RET
```

### 9. Fog of War / Exploration

Track which areas have been explored:

```asm
; Exploration bitmap (1 bit per tile)
; For current chunk only (64 tiles = 8 bytes)
ExploredMap:
    DEFS 8

MarkExplored:
    ; Input: B = X (0-7), C = Y (0-7)
    LD A, C
    ADD A, A
    ADD A, A
    ADD A, A            ; Y * 8
    ADD A, B            ; + X = bit index

    LD B, A             ; Save index
    SRL A
    SRL A
    SRL A               ; Divide by 8 = byte index

    LD HL, ExploredMap
    LD D, 0
    LD E, A
    ADD HL, DE          ; HL = byte address

    LD A, B
    AND $07             ; Bit position within byte
    LD B, A
    LD A, 1
.ShiftLoop:
    OR A
    JR Z, .Done
    SLA A
    DJNZ .ShiftLoop
.Done:
    OR (HL)             ; Set bit
    LD (HL), A
    RET

IsExplored:
    ; Input: B = X, C = Y
    ; Output: Z flag set if explored
    ; (Similar logic but test bit instead of set)
    ; ...
```

## Game Loop Structure

```asm
MainGameLoop:
    ; 1. Input
    CALL ReadKeyboard
    CALL ProcessInput

    ; 2. Update player position
    CALL MovePlayer
    CALL CheckCollisions

    ; 3. Update camera
    CALL UpdateCamera
    CALL DetermineVisibleChunks
    CALL LoadChunks         ; Generate if needed

    ; 4. Update entities
    CALL UpdateMonsters
    CALL UpdateProjectiles

    ; 5. Check for events
    CALL CheckItemPickup
    CALL CheckStairs
    CALL CheckCombat

    ; 6. Render
    CALL MarkDirtyTiles
    CALL RedrawDirtyTiles
    CALL DrawPlayer
    CALL DrawUI

    ; 7. Wait for frame
    HALT

    ; 8. Loop
    JR MainGameLoop
```

## Technical Implementation Phases

### Phase 1: Basic Procedural Generation
- Implement chunk system
- Seed-based generation
- Simple floor/wall patterns
- **Goal**: Infinite static dungeon

### Phase 2: Isometric Rendering
- Draw 8x8 visible chunk in isometric
- Player sprite in center
- No scrolling yet
- **Goal**: See the isometric dungeon

### Phase 3: Tile-Based Scrolling
- Player movement updates camera
- Redraw affected columns/rows
- Keep player centered
- **Goal**: Smooth tile-based scrolling

### Phase 4: Content Generation
- Rooms and corridors algorithm
- Stairs placement
- Gold and items
- **Goal**: Playable dungeon exploration

### Phase 5: Game Mechanics
- Combat system
- Item pickup
- Inventory
- Health/stats
- **Goal**: Playable game

### Phase 6: Pixel Scrolling (Optional)
- Sub-tile movement
- Pixel-smooth scrolling
- **Goal**: Buttery smooth movement

## Performance Targets

**Target frame rate**: 25 FPS (every other frame at 50Hz)
- Allows 40ms per game loop iteration
- ~140,000 Z80 cycles per iteration

**Optimizations needed**:
- Unroll critical loops
- Lookup tables for screen positions
- Pre-shifted sprite data
- Dirty rectangle system essential

## Scrolling Algorithm Detail

### Determine What to Redraw

```asm
; Called after camera moves
; Marks tiles that need redrawing

UpdateAfterScroll:
    ; Calculate how many tiles camera shifted
    LD HL, (CameraX)
    LD DE, (OldCameraX)
    OR A
    SBC HL, DE          ; HL = delta X

    LD A, H
    OR A
    JP NZ, .FullRedraw  ; Scrolled too far, full redraw

    LD A, L
    CP 16               ; More than 1 tile?
    JP NC, .FullRedraw

    ; Micro-scroll, mark edge tiles dirty
    LD A, L
    OR A
    JR Z, .CheckY       ; No X movement

    JP P, .ScrolledRight

.ScrolledLeft:
    ; Mark left column dirty
    LD B, 0             ; Left edge
    LD C, 8
.MarkLeftLoop:
    PUSH BC
    CALL MarkTileDirty
    POP BC
    INC B
    DEC C
    JR NZ, .MarkLeftLoop
    JR .CheckY

.ScrolledRight:
    ; Mark right column dirty
    LD B, 7             ; Right edge
    LD C, 8
.MarkRightLoop:
    PUSH BC
    CALL MarkTileDirty
    POP BC
    INC B
    DEC C
    JR NZ, .MarkRightLoop

.CheckY:
    ; Similar logic for Y scrolling
    ; ...

    RET

.FullRedraw:
    ; Mark all tiles dirty
    LD HL, DirtyTiles
    LD DE, DirtyTiles + 1
    LD BC, 63
    LD (HL), 1
    LDIR
    RET
```

## Visual Effects

### Fog of War Rendering

Draw unexplored areas darkened or with pattern:

```asm
DrawTile:
    ; ... normal tile drawing ...

    ; Check if explored
    CALL IsExplored
    RET Z               ; Explored, done

    ; Not explored - apply fog effect
    ; Option 1: Draw darker attributes
    ; Option 2: Draw diagonal pattern over it
    ; Option 3: Don't draw at all

    LD A, $00           ; Black INK
    LD (AttributeAddress), A
    RET
```

### Smooth Movement Animation

Even with tile-based scrolling, animate player sprite:

```
Frame 0: Player at center
Frame 1: Player sprite shifts 2 pixels right
Frame 2: Player sprite shifts 4 pixels right
Frame 3: Player sprite shifts 6 pixels right
Frame 4: Scroll tiles, reset player sprite to center
```

This creates illusion of smooth movement while only updating tiles every 4 frames.

## Challenges and Solutions

### Challenge 1: Isometric Math is Slow

**Solution**: Extensive lookup tables
- Pre-calculate all screen positions
- Table: world position → screen coordinates
- 256 bytes for X, 512 bytes for Y

### Challenge 2: Z80 Can't Handle Truly Infinite Maps

**Solution**: Very large but bounded
- World coordinates: -32768 to +32767 (16-bit signed)
- That's 65536 x 65536 tiles = 4 billion tiles!
- More than sufficient for "infinite feel"

### Challenge 3: Random Generation Must Be Fast

**Solution**: Simple hash functions
- One calculation per tile
- No complex algorithms
- Lookup tables for distributions

### Challenge 4: Scrolling Redraws Too Much

**Solution**: Intelligent dirty tracking
- Only redraw changed tiles
- Pre-render chunks off-screen
- Double-buffering if needed (costly on Spectrum)

## Comparison: BASIC vs Machine Code

**Your BASIC version**:
- Can implement complex algorithms easily
- Procedural generation straightforward
- Too slow for smooth scrolling
- Limited graphics capabilities

**Machine code version**:
- 10-50x faster
- Smooth scrolling possible
- More complex graphics
- Harder to develop (but worth it!)

## Next Steps

1. **Study the original demo** - Understand the isometric rendering
2. **Implement chunk system** - Prove procedural generation works
3. **Build room generator** - Create interesting dungeons
4. **Add scrolling** - Start with tile-based
5. **Add gameplay** - Combat, items, progression
6. **Polish** - Smooth it out

## Inspiration

This would be **unique**: A smoothly scrolling 3D isometric roguelike with infinite procedural dungeons on a 1982 computer with 48KB RAM. Nothing quite like it exists!

## File Structure Suggestion

```
SwordOfFargoal/
├── src/
│   ├── main.asm
│   ├── procgen/
│   │   ├── chunks.asm
│   │   ├── rooms.asm
│   │   └── items.asm
│   ├── engine/
│   │   ├── camera.asm
│   │   ├── scroll.asm
│   │   └── render.asm
│   ├── game/
│   │   ├── player.asm
│   │   ├── combat.asm
│   │   └── items.asm
│   └── data/
│       ├── sprites.asm
│       └── tables.asm
├── assets/
│   └── graphics/
│       ├── player.png
│       ├── monsters.png
│       └── tiles.png
└── docs/
    ├── DESIGN.md
    └── ALGORITHMS.md
```

This is an incredibly ambitious project - but absolutely achievable! The combination of procedural generation, isometric 3D, and smooth scrolling would create something truly special for the ZX Spectrum.

Ready to make gaming history? 🗡️✨
