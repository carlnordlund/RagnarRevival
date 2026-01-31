# Pre-Computed Edge Templates for Ultra-Smooth Scrolling

## The Brilliant Insight

Instead of calculating edge graphics at runtime, **pre-render all possible edge combinations** at different scroll positions:

1. **Limited tile types**: Wall, Fog, Ground = only 3 types
2. **Limited combinations**: Wall-Fog, Wall-Ground, Fog-Ground = 3 pairs
3. **Pre-render edges**: Store all variations for each scroll position
4. **Fast blitting**: Just copy pre-rendered edge strip → screen

**Result: 2-pixel or even 1-pixel smooth scrolling becomes feasible!**

## Edge Combination Matrix

### Tile Type Combinations

With only 3 block types, there are only **6 edge types**:

```
1. Wall → Fog (wall on left, fog on right)
2. Fog → Wall (fog on left, wall on right)
3. Wall → Ground (wall on left, ground on right)
4. Ground → Wall (ground on left, wall on right)
5. Fog → Ground (fog on left, ground on right)
6. Ground → Fog (ground on left, fog on right)
```

### Scroll Directions

Isometric has 4 diagonal scroll directions:
```
1. North-West (NW): -X, -Y
2. North-East (NE): +X, -Y
3. South-East (SE): +X, +Y
4. South-West (SW): -X, +Y
```

## Pre-Rendered Edge Templates

### For 4-Pixel Scrolling (Recommended)

**32-pixel tile width / 4 pixels per step = 8 scroll positions**

For each edge type, pre-render 8 variations:

```
Edge: Wall → Ground

Position 0 (no scroll):
████████████████|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    Wall        |      Ground

Position 1 (+4 pixels scrolled):
    ████████████████|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
        Wall        |      Ground

Position 2 (+8 pixels scrolled):
        ████████████████|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
            Wall        |      Ground

... (8 positions total)
```

### Memory Requirements

**Per edge type:**
- 8 scroll positions × 64 bytes per tile = 512 bytes

**Total for all 6 edge types:**
- 6 edge types × 512 bytes = **3,072 bytes (~3KB)**

**Very affordable!**

### For 2-Pixel Scrolling (Ultra-Smooth)

**32-pixel tile width / 2 pixels per step = 16 scroll positions**

**Per edge type:**
- 16 scroll positions × 64 bytes = 1,024 bytes

**Total for all 6 edge types:**
- 6 edge types × 1,024 bytes = **6,144 bytes (~6KB)**

**Still manageable if you want maximum smoothness!**

## Data Structure

### Edge Template Storage

```asm
; Edge templates organized by type and scroll position

; Wall → Fog edges (8 positions for 4-pixel scroll)
EDGE_WALL_FOG:
EDGE_WALL_FOG_POS0:     DEFS 64    ; No scroll
EDGE_WALL_FOG_POS1:     DEFS 64    ; +4 pixels
EDGE_WALL_FOG_POS2:     DEFS 64    ; +8 pixels
EDGE_WALL_FOG_POS3:     DEFS 64    ; +12 pixels
EDGE_WALL_FOG_POS4:     DEFS 64    ; +16 pixels
EDGE_WALL_FOG_POS5:     DEFS 64    ; +20 pixels
EDGE_WALL_FOG_POS6:     DEFS 64    ; +24 pixels
EDGE_WALL_FOG_POS7:     DEFS 64    ; +28 pixels

; Wall → Ground edges
EDGE_WALL_GROUND:
EDGE_WALL_GROUND_POS0:  DEFS 64
EDGE_WALL_GROUND_POS1:  DEFS 64
; ... etc

; Fog → Ground edges
EDGE_FOG_GROUND:
EDGE_FOG_GROUND_POS0:   DEFS 64
; ... etc

; Total: 6 edge types × 8 positions × 64 bytes = 3KB
```

### Edge Lookup Table

```asm
; Quick lookup: (LeftType, RightType, ScrollPos) → Edge Address

; Input: A = left tile type, B = right tile type, C = scroll position (0-7)
; Output: HL = address of pre-rendered edge

GetEdgeTemplate:
    ; Calculate edge type index
    ; Wall=0, Fog=1, Ground=2

    LD H, A             ; Left type
    ADD A, A
    ADD A, A            ; × 4
    ADD A, B            ; + right type
    ; Now A = edge type index (0-5)

    ; Multiply by 512 (8 positions × 64 bytes)
    LD H, A
    LD L, 0
    SLA H               ; × 2
    ; Now HL = edge type × 512

    ; Add scroll position offset
    LD A, C             ; Scroll position (0-7)
    LD D, 0
    LD E, A
    SLA E               ; × 2
    SLA E               ; × 4
    SLA E               ; × 8
    SLA E               ; × 16
    SLA E               ; × 32
    SLA E               ; × 64
    ADD HL, DE

    ; Add base address
    LD DE, EDGE_TEMPLATES_BASE
    ADD HL, DE

    RET
```

## Stripe-Based World Storage

### Traditional Storage (Tile Matrix)

```
7×7 tiles stored as 2D array:
[0,0] [1,0] [2,0] ... [6,0]
[0,1] [1,1] [2,1] ... [6,1]
...
[0,6] [1,6] [2,6] ... [6,6]

Access: Tile[Y][X]
```

### Stripe-Based Storage (Optimized for Scrolling)

```
Store as vertical stripes (columns):

Stripe 0: [0,0] [0,1] [0,2] ... [0,6]
Stripe 1: [1,0] [1,1] [1,2] ... [1,6]
Stripe 2: [2,0] [2,1] [2,2] ... [2,6]
...
Stripe 6: [6,0] [6,1] [6,2] ... [6,6]

When scrolling horizontally:
- Discard leftmost/rightmost stripe
- Add new stripe on other side
- Entire stripe operation!
```

**Or horizontal stripes (rows):**

```
Stripe 0: [0,0] [1,0] [2,0] ... [6,0]
Stripe 1: [0,1] [1,1] [2,1] ... [6,1]
...
Stripe 6: [0,6] [1,6] [2,6] ... [6,6]

When scrolling vertically:
- Discard top/bottom stripe
- Add new stripe on other side
```

### Memory Layout

```asm
; Store world as stripes for fast scrolling

; Vertical stripes (for E/W scrolling)
WorldStripes_Vertical:
    ; Stripe 0 (leftmost column)
    DEFB TILE_WALL, TILE_WALL, TILE_GROUND, ...  ; 7 bytes
    ; Stripe 1
    DEFB TILE_WALL, TILE_GROUND, TILE_GROUND, ...
    ; ... (7 stripes total)

; Horizontal stripes (for N/S scrolling)
WorldStripes_Horizontal:
    ; Stripe 0 (top row)
    DEFB TILE_FOG, TILE_FOG, TILE_FOG, ...  ; 7 bytes
    ; Stripe 1
    DEFB TILE_FOG, TILE_WALL, TILE_WALL, ...
    ; ... (7 stripes total)

; Total: 7 × 7 × 2 = 98 bytes (negligible!)
```

## Scrolling Implementation

### Determine Which Edges to Draw

```asm
; When scrolling East (NE or SE)
; Need to draw right edge of screen

ScrollEast:
    LD A, (ScrollPhase)     ; 0-7 for 4-pixel scroll
    LD C, A                 ; Save scroll position

    ; Get rightmost stripe
    LD HL, WorldStripes_Vertical + (6 * 7)
    LD B, 7                 ; 7 tiles in stripe

.DrawEdges:
    ; Get current tile type
    LD A, (HL)
    INC HL
    LD D, A                 ; Save current type

    ; Get next tile type (or fog if at edge)
    LD A, (HL)
    OR A
    JR NZ, .HasNext
    LD A, TILE_FOG          ; Edge of world = fog

.HasNext:
    LD E, A                 ; Next type

    ; Get edge template
    PUSH HL
    PUSH BC
    LD A, D                 ; Left type
    LD B, E                 ; Right type
    ; C already has scroll position
    CALL GetEdgeTemplate    ; Returns HL = template address

    ; Draw edge template to screen
    CALL BlitEdgeToScreen

    POP BC
    POP HL

    DJNZ .DrawEdges

    RET
```

### Fast Edge Blitting

```asm
; Blit pre-rendered edge template to screen
; Input: HL = edge template address
;        DE = screen destination

BlitEdgeToScreen:
    LD B, 16                ; 16 lines (diamond height)

.LineLoop:
    ; Copy 4 bytes (32 pixels wide)
    LDI
    LDI
    LDI
    LDI

    ; Move to next screen line
    PUSH HL
    EX DE, HL
    CALL NextScreenLine     ; DE = next line
    EX DE, HL
    POP HL

    DJNZ .LineLoop
    RET

; This is MUCH faster than calculating edges at runtime!
; Just a block copy of pre-rendered data
```

## Scroll Position Tracking

```asm
; Current scroll state
ScrollPhase:        DEFB 0      ; 0-7 (for 4-pixel scroll)
                                ; 0-15 (for 2-pixel scroll)

ScrollDirection:    DEFB 0      ; 0=NE, 1=SE, 2=SW, 3=NW

PixelOffsetX:       DEFW 0      ; Current X offset (0-31)
PixelOffsetY:       DEFW 0      ; Current Y offset (0-15)

; Smooth scroll one step
ScrollStep:
    LD A, (ScrollPhase)
    INC A
    CP 8                        ; 8 steps for 4-pixel scroll
    JR NZ, .NotComplete

    ; Completed full tile
    XOR A
    CALL ShiftWorldStripe       ; Shift world data

.NotComplete:
    LD (ScrollPhase), A

    ; Update pixel offsets
    LD HL, (PixelOffsetX)
    LD DE, 4                    ; +4 pixels per step
    ADD HL, DE
    LD (PixelOffsetX), HL

    ; Draw edges with current scroll phase
    CALL DrawScrollEdges

    RET
```

## Building Edge Templates (One-Time Setup)

### Generate Templates at Build Time

Use your `png2asm.py` tool to generate all edge combinations!

```bash
# Create edge graphics in Aseprite
# For each edge type, create 8 frames (4-pixel offsets)

# Wall-to-fog edge animation (8 frames)
python tools/png2asm.py \
    assets/edges/wall_fog.png \
    src/data/edge_wall_fog.asm \
    --label EDGE_WALL_FOG \
    --frames 8

# Wall-to-ground edge
python tools/png2asm.py \
    assets/edges/wall_ground.png \
    src/data/edge_wall_ground.asm \
    --label EDGE_WALL_GROUND \
    --frames 8

# Fog-to-ground edge
python tools/png2asm.py \
    assets/edges/fog_ground.png \
    src/data/edge_fog_ground.asm \
    --label EDGE_FOG_GROUND \
    --frames 8

# All edges generated automatically!
```

### Or Generate Programmatically

```asm
; Generate edge templates from base tiles at startup
; (Only needed once, can be pre-built)

GenerateEdgeTemplates:
    ; For each edge type
    LD B, 6                 ; 6 edge types
    LD HL, EdgeTypeTable

.EdgeTypeLoop:
    PUSH BC

    ; Get left and right tile types
    LD A, (HL)
    INC HL
    LD C, A                 ; Left type
    LD A, (HL)
    INC HL
    LD D, A                 ; Right type

    ; Generate 8 scroll positions
    LD E, 8
.ScrollPosLoop:
    PUSH HL
    PUSH DE

    ; Render edge at this scroll position
    CALL RenderEdge         ; C=left, D=right, E=scroll

    POP DE
    POP HL

    DEC E
    JR NZ, .ScrollPosLoop

    POP BC
    DJNZ .EdgeTypeLoop

    RET

EdgeTypeTable:
    DEFB TILE_WALL, TILE_FOG
    DEFB TILE_FOG, TILE_WALL
    DEFB TILE_WALL, TILE_GROUND
    DEFB TILE_GROUND, TILE_WALL
    DEFB TILE_FOG, TILE_GROUND
    DEFB TILE_GROUND, TILE_FOG
```

## Performance Analysis

### Traditional Edge Calculation (Runtime)

```
Per edge tile:
1. Determine tile types (left/right): 50 cycles
2. Calculate edge pixels: 200 cycles
3. Draw to screen: 500 cycles
Total: ~750 cycles per edge

For 14 edges (typical scroll):
14 × 750 = 10,500 cycles
```

### Pre-Computed Edge Blitting

```
Per edge tile:
1. Lookup pre-rendered template: 100 cycles
2. Block copy to screen: 200 cycles
Total: ~300 cycles per edge

For 14 edges:
14 × 300 = 4,200 cycles

Speedup: 2.5x faster!
```

### Total Scroll Performance

**With pre-computed edges (4-pixel scroll):**
```
Edge drawing: 4,200 cycles
Player sprite: 2,000 cycles
Screen management: 1,000 cycles
Total: ~7,200 cycles per frame

At 3.5MHz: 2ms per frame
FPS: 500 FPS (obviously game logic limited)
Practical: 50-60 FPS easily achievable!
```

## Memory Trade-off Summary

### Option 1: 4-Pixel Scrolling (Recommended)

**Memory:**
- Edge templates: 3KB
- Stripe storage: 98 bytes
- Total: ~3.1KB

**Performance:**
- 8 frames per tile
- Smooth motion
- 50-60 FPS achievable
- ✓ Excellent balance

### Option 2: 2-Pixel Scrolling (Ultra-Smooth)

**Memory:**
- Edge templates: 6KB
- Stripe storage: 98 bytes
- Total: ~6.1KB

**Performance:**
- 16 frames per tile
- Buttery smooth
- 50-60 FPS still achievable
- Best visual quality

### Option 3: Runtime Calculation (No Templates)

**Memory:**
- No edge templates: 0KB
- Traditional storage: 49 bytes

**Performance:**
- Slower drawing
- 25-35 FPS
- Still playable but less smooth

## Implementation Steps

### Step 1: Create Edge Graphics

```
In Aseprite:
1. Create wall tile (32×16 diamond)
2. Create fog tile (32×16 diamond)
3. Create ground tile (32×16 diamond)

For each edge type:
1. Create animation with 8 frames
2. Each frame = 4-pixel scroll offset
3. Export as single PNG with frames

Example: wall_fog.png
Frame 0: Wall fully left, fog fully right
Frame 1: Wall scrolled 4px right
Frame 2: Wall scrolled 8px right
...
Frame 7: Wall scrolled 28px right
```

### Step 2: Generate Assembly Data

```bash
# Automated conversion
./tools/generate_all_edges.sh
```

### Step 3: Integrate Into Rendering

```asm
; Replace runtime edge calculation with template lookup
OldWay:
    CALL CalculateEdge      ; Slow!
    CALL DrawEdge

NewWay:
    CALL GetEdgeTemplate    ; Fast lookup!
    CALL BlitEdgeToScreen   ; Fast copy!
```

### Step 4: Test Performance

```asm
; Benchmark
TestScroll:
    LD B, 50                ; 50 frames

.Loop:
    HALT                    ; Wait for frame
    CALL ScrollStep
    DJNZ .Loop

    ; Measure time taken
    ; Should be smooth 50 FPS!
    RET
```

## Advantages of This Approach

✅ **Blazing fast**: Block copy instead of calculation
✅ **Predictable**: No variance in render time
✅ **Smooth**: Can do 2-pixel or even 1-pixel scrolling
✅ **Simple**: Just lookup and blit
✅ **Memory efficient**: Only 3-6KB for all edges
✅ **Scalable**: Easy to add more edge types if needed

## Disadvantages

❌ **Upfront memory**: 3-6KB reserved for templates
❌ **Build complexity**: Need to generate all templates
❌ **Less flexible**: Can't easily change edge appearance at runtime

## Conclusion

Pre-computed edge templates are **absolutely worth it** for smooth scrolling:

- **3KB memory** for 4-pixel scrolling (recommended)
- **6KB memory** for 2-pixel ultra-smooth scrolling
- **2.5x performance improvement** in edge rendering
- **50-60 FPS** easily achievable with game logic

Combined with:
- Stripe-based world storage
- Edge-based rendering (only draw boundaries)
- Limited tile types (wall/fog/ground)

You'll have a **beautifully smooth scrolling isometric roguelike** that would be genuinely impressive on the ZX Spectrum! 🚀✨

This optimization strategy is sophisticated but very practical for your single-layer Sword of Fargoal design!
