# Tile-Based Movement with Smooth Visual Scrolling

## The Best of Both Worlds

**Game Logic:** Discrete, tile-based (simple)
**Visual Rendering:** Smooth interpolation (beautiful)

This separation makes the game much easier to implement while still looking smooth!

## How It Works

### Player Movement (Discrete)

Player position is stored in **tile coordinates** (integers):

```asm
PlayerTileX:    DEFB 3      ; Player at tile (3, 3)
PlayerTileY:    DEFB 3      ; Center of 7×7 view

; Player moves north
MovePlayerNorth:
    ; Check destination tile
    LD A, (PlayerTileY)
    DEC A                   ; Y-1 = north
    LD B, A
    LD A, (PlayerTileX)
    LD C, A

    ; Get tile type at destination
    CALL GetTileAt          ; A = tile type

    ; Is it walkable?
    CP TILE_WALL
    RET Z                   ; Can't walk into wall

    CP TILE_FOG
    RET Z                   ; Can't walk into unexplored

    ; Movement is valid
    LD A, (PlayerTileY)
    DEC A
    LD (PlayerTileY), A

    ; Mark new tile as explored
    CALL MarkExplored

    ; Start smooth scroll animation
    LD A, 8                 ; 8 frames
    LD (ScrollFramesLeft), A
    LD A, DIR_NORTH
    LD (ScrollDirection), A

    ; Update world data (load new stripe if needed)
    CALL UpdateWorldStripe

    RET
```

**Game state changes INSTANTLY** - player is immediately at new tile in game logic!

### Visual Scrolling (Smooth)

Camera position interpolates over **8 frames**:

```asm
; Camera offset (for smooth scrolling)
CameraOffsetX:      DEFW 0      ; -32 to +32 pixels
CameraOffsetY:      DEFW 0      ; -16 to +16 pixels
ScrollFramesLeft:   DEFB 0      ; Frames remaining
ScrollDirection:    DEFB 0      ; Direction scrolling

; Called every frame
UpdateCamera:
    LD A, (ScrollFramesLeft)
    OR A
    RET Z                       ; Not scrolling

    DEC A
    LD (ScrollFramesLeft), A

    ; Get scroll direction
    LD A, (ScrollDirection)
    CP DIR_NORTH
    JP Z, .ScrollNorth
    CP DIR_EAST
    JP Z, .ScrollEast
    ; ... etc

.ScrollNorth:
    ; North = +4 pixels X, -2 pixels Y per frame
    LD HL, (CameraOffsetX)
    LD DE, 4
    ADD HL, DE
    LD (CameraOffsetX), HL

    LD HL, (CameraOffsetY)
    LD DE, 2
    OR A
    SBC HL, DE
    LD (CameraOffsetY), HL

    ; Redraw edges at new offset
    CALL RedrawScrollEdges

    RET
```

### After 8 Frames

```asm
; When scroll completes
; (ScrollFramesLeft reaches 0)

OnScrollComplete:
    ; Reset camera offsets
    LD HL, 0
    LD (CameraOffsetX), HL
    LD (CameraOffsetY), HL

    ; World tiles have shifted in memory
    ; Screen now shows new view centered on player

    RET
```

**Visual scroll complete, game continues!**

## Advantages for Corner Handling

### Problem: Partial Corners During Scroll

With sub-tile movement, corners would be partially visible:

```
Frame 1: Corner starting to appear (4 pixels)
  ░░
  ──│
  ▓▓│

Frame 2: More corner visible (8 pixels)
  ░░░░
  ────│
  ▓▓▓▓│

... complex to render!
```

### Solution: Tile-Based Movement

Corners appear/disappear as **complete units**:

```
Frame 0: Old view (corner off-screen)
  ░░░░
  ░░░░
  ────
  ▓▓▓▓

Frame 8: New view (corner fully on-screen)
    ░░░░│
    ────┼
    ▓▓▓▓│███
        │███

No partial corners!
Just smooth camera slide from position A to B
```

**Between frames:** Camera slides smoothly, but **tiles don't change** - we just draw them at different pixel offsets!

## Implementation Details

### Drawing with Camera Offset

```asm
; Draw world with camera offset applied
DrawWorld:
    LD IX, (CameraOffsetX)      ; IX = X offset
    LD IY, (CameraOffsetY)      ; IY = Y offset

    LD B, 7                     ; 7 rows
.RowLoop:
    LD C, 7                     ; 7 columns
.ColLoop:
    PUSH BC

    ; Calculate screen position with offset
    CALL CalculateScreenPos     ; Uses IX, IY

    ; Get tile type
    CALL GetTileType

    ; Draw tile (or edge template if at boundary)
    CALL DrawTileAtOffset

    POP BC
    DEC C
    JR NZ, .ColLoop
    DEC B
    JR NZ, .RowLoop

    ; Draw player sprite (always centered)
    CALL DrawPlayer

    RET
```

### Edge Selection Based on Offset

```asm
; Select correct edge template based on scroll offset
; Input: A = tile type, B = adjacent type
;        IX = camera X offset (0-31)
; Output: HL = edge template address

SelectEdgeTemplate:
    ; Calculate scroll position (0-7 for 4-pixel scroll)
    PUSH IX
    POP HL
    SRL H
    RR L
    SRL H
    RR L                        ; Divide by 4
    LD C, L                     ; C = scroll position (0-7)

    ; Get edge template
    CALL GetEdgeTemplate        ; A, B, C → HL

    RET
```

## Corner Handling with OR Logic

### Draw Order Matters

When using OR logic for overlapping edges:

```asm
; Draw corner by overlaying edges
DrawCorner:
    ; Example: Wall-Fog-Ground corner

    ; 1. Draw base (ground)
    LD HL, TILE_GROUND
    CALL BlitDirect

    ; 2. OR wall edge on top
    LD HL, EDGE_GROUND_WALL
    CALL BlitWithOR

    ; 3. OR fog edge on top
    LD HL, EDGE_WALL_FOG
    CALL BlitWithOR

    ; Result: All three tiles blend at corner!
    RET
```

### Blit Functions

```asm
; Direct blit (overwrites screen)
BlitDirect:
    LD B, 16
.Loop:
    LD A, (HL)
    LD (DE), A
    INC HL
    INC DE
    DJNZ .Loop
    RET

; OR blit (combines with existing pixels)
BlitWithOR:
    LD B, 16
.Loop:
    LD A, (DE)              ; Read existing screen data
    OR (HL)                 ; OR with new data
    LD (DE), A              ; Write back
    INC HL
    INC DE
    DJNZ .Loop
    RET
```

### OR Logic for Corners

```
Ground alone:
  ▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓

OR with wall edge:
  ▓▓▓▓████
  ▓▓▓▓████

OR with fog edge:
  ░░▓▓████
  ░░▓▓████

Final corner! ✓
```

**No special corner templates needed!**

## Example: Full Movement Sequence

### User Presses "North"

**Frame 0:**
```
Game state:
- PlayerTileY = 3
- World tiles updated
- ScrollFramesLeft = 8
- CameraOffsetX = 0, CameraOffsetY = 0

Screen: Old view
```

**Frames 1-7:**
```
Game state:
- PlayerTileY = 2 (already moved!)
- ScrollFramesLeft = 7, 6, 5, 4, 3, 2, 1
- CameraOffsetX += 4, CameraOffsetY -= 2 (each frame)

Screen: Smoothly sliding
- All tiles drawn at offset position
- Edges use templates based on current offset
- Corners handled via OR logic
```

**Frame 8:**
```
Game state:
- PlayerTileY = 2
- ScrollFramesLeft = 0
- CameraOffsetX = 32, CameraOffsetY = -16

Action: Reset offsets to 0, update screen base

Screen: New view (centered on player's new position)
```

**Player can now move again!**

## Input Handling

```asm
; Only allow movement when not scrolling
ReadInput:
    ; Check if already scrolling
    LD A, (ScrollFramesLeft)
    OR A
    RET NZ                      ; Still animating, ignore input

    ; Read keyboard
    CALL ReadKeyboard

    ; Check directions
    BIT KEY_UP, A
    JP NZ, MovePlayerNorth

    BIT KEY_RIGHT, A
    JP NZ, MovePlayerEast

    ; ... etc

    RET
```

**This prevents "buffered" movement and keeps it feeling responsive!**

## Performance Analysis

### Per Frame During Scroll

```
Edge template lookup: 100 cycles × 14 edges = 1,400 cycles
Edge blitting: 200 cycles × 14 edges = 2,800 cycles
Corner OR operations: 50 cycles × ~4 corners = 200 cycles
Player sprite: 2,000 cycles
Frame management: 500 cycles

Total: ~6,900 cycles per frame
At 3.5MHz: ~2ms per frame

FPS during scroll: 50-60 FPS ✓
```

### Per Frame When Static

```
No scrolling - screen doesn't change!
Only need to animate:
- Player idle animation
- Monster animations
- Torch/fire effects

Minimal CPU usage, can be 50 FPS easily
```

## Memory Requirements

```
Graphics data:
- 3 base tiles (wall, fog, ground): 192 bytes
- 6 edge types × 8 positions: 3,072 bytes
- Player sprite: 128 bytes
- Monster sprites: 512 bytes
Total: ~4KB

World data:
- Current view (7×7 tiles): 49 bytes
- Chunk buffer (9×9 tiles): 81 bytes
- Exploration bitmap: 11 bytes
Total: ~150 bytes

State:
- Scroll state: 10 bytes
- Player state: 20 bytes
- Monster list: 100 bytes
Total: ~130 bytes

Grand total: ~4.3KB (very manageable!)
```

## Advantages Summary

✅ **Simple game logic**: Integer tile coordinates
✅ **Simple collision**: Tile-based checks
✅ **Simple AI**: Tile-based pathfinding
✅ **Simple corners**: OR logic, no special cases
✅ **Smooth visuals**: 8-frame interpolation
✅ **Responsive input**: Move when animation completes
✅ **Classic feel**: Like 8-bit and 16-bit classics
✅ **Excellent performance**: 50-60 FPS
✅ **Low memory**: Only ~4KB for everything

## Classic Games Using This Approach

- **The Legend of Zelda** (NES): Tile-based movement, smooth scroll
- **Final Fantasy** (NES): Discrete steps, smooth animation
- **Dragon Quest** (NES): Same approach
- **Phantasy Star** (SMS): Tile movement with smooth scroll
- **Knight Lore** (ZX Spectrum): Isometric with discrete movement

**Proven technique, perfect for ZX Spectrum! ✓**

## Implementation Checklist

- [ ] Tile-based world representation (7×7 visible)
- [ ] Player position as tile coordinates
- [ ] Movement validation (collision check)
- [ ] 8-frame scroll animation system
- [ ] Camera offset interpolation (4px X, 2px Y per frame)
- [ ] Edge template selection based on scroll position
- [ ] OR blitting for corner handling
- [ ] Input lock during scroll animation
- [ ] Smooth 50-60 FPS during movement

This approach gives you the **best of both worlds**: simple, robust game logic with beautiful smooth visuals! 🎮✨
