# Sword of Fargoal: Single-Layer Isometric Design

## Core Concept Clarification

**Single-layer dungeon** viewed in isometric projection:
- **7×7 visible floor tiles** (player-centered)
- **Flat dungeon** - no vertical layers
- **Walls** are vertical blocks placed on floor tiles
- **Fog of war** obscures unexplored areas
- **Infinite horizontal world** via procedural generation

This is simpler than multi-layer 3D, making smooth scrolling very achievable!

## Visual Structure

### Tile Types (Single Layer)

```
Floor tiles (32×16 pixel diamonds):
1. Empty floor (walkable)
2. Wall block (impassable)
3. Fog of war (unexplored)
4. Special: stairs, doors, treasure, etc.
```

### Example View (7×7 visible area)

```
Isometric view:
       ░░░░░░░░░░░  ← Fog (unexplored)
     ░░░░░░░░░░░░░
   ░░░█████░░░░░░
  ░░░█████░░░░░░    ← Walls (vertical blocks)
 ░░░░█▓▓▓█░░░░░     ← Floor inside room
░░░░░█▓@▓█░░░░░     @ = Player (centered)
 ░░░░█▓▓▓█░░░░
  ░░░█████░░░░      ← More walls
   ░░░░░░░░░
     ░░░░░░░
       ░░░░

7×7 visible diamonds
Player always at center (3,3)
World scrolls around player
```

## Tile Specifications

### Floor Diamond (32×16 pixels)

```
        ████████████████        ← Top point
      ████████████████████
    ████████████████████████
  ████████████████████████████  ← Widest: 32 pixels
████████████████████████████████
  ████████████████████████████
    ████████████████████████
      ████████████████████
        ████████████████        ← Bottom point

Height: 16 pixels
Memory: 4 bytes × 16 lines = 64 bytes
```

### Wall Block (vertical face on floor)

```
Wall has TOP surface + FRONT face:

Top (diamond):
    ████████
  ████████████
████████████████  ← 32×16 pixels

Front (rectangular):
████████████████
████████████████
████████████████  ← 32 pixels wide
████████████████     16-24 pixels tall
████████████████     (shows wall height)
████████████████

Total: ~96-128 bytes per wall tile
```

## Memory Requirements (Much Lighter!)

### Graphics Data

```
Floor tiles (stone, wood, dirt, etc.):
  8 types × 64 bytes = 512 bytes

Wall tiles (different wall types):
  8 types × 128 bytes = 1,024 bytes

Special tiles (stairs, doors, treasure):
  8 types × 128 bytes = 1,024 bytes

Fog overlay:
  1 type × 64 bytes = 64 bytes

Total graphics: ~2.5KB (very manageable!)
```

### World Data (Chunk System)

```
Visible area: 7×7 = 49 tiles
Buffer area: 9×9 = 81 tiles (1-tile border)

Per tile storage:
- Block type: 1 byte
- Explored flag: 1 bit (packed)
- Item/enemy: 1 byte (if present)

Storage: 81 bytes + 10 bytes flags = ~100 bytes per chunk

With 3×3 chunk buffer: 9 chunks × 100 bytes = 900 bytes
Very affordable!
```

### Total Memory Budget

```
$4000-$5AFF: Screen (6912 bytes)
$5B00-$5CFF: System variables
$5D00-$5FFF: Chunk data (900 bytes)
$6000-$69FF: Sprite data (2.5KB)
$6A00-$7AFF: Screen tables (4KB)
$7B00-$8AFF: Game state (4KB)
  - Player stats, inventory
  - Monster list
  - Item list
  - Level seed
$8B00-$FFFF: Program code (~29KB)

Plenty of room!
```

## Simplified Rendering

### No Z-Sorting Needed!

Since everything is on one layer:

```asm
; Render visible area (7×7 grid)
RenderScene:
    LD B, 7             ; 7 rows
.RowLoop:
    LD C, 7             ; 7 columns
.ColLoop:
    PUSH BC

    ; Calculate world position
    CALL WorldPosFromScreen

    ; Get tile type
    CALL GetTileAt

    ; Check if explored
    CALL IsExplored
    JR Z, .DrawTile

    ; Not explored - draw fog
    LD A, TILE_FOG

.DrawTile:
    ; Draw tile at screen position
    CALL DrawIsometricTile

    POP BC
    DEC C
    JR NZ, .ColLoop

    DEC B
    JR NZ, .RowLoop

    ; Draw player sprite (always on top)
    CALL DrawPlayer
    RET
```

**Much simpler than multi-layer!**

## Edge-Based Scrolling (Critical Here!)

With 64-byte floor tiles, edge optimization is essential:

### Performance Without Optimization

```
Full redraw: 49 tiles × 64 bytes = 3,136 bytes
~313,600 cycles = 90ms at 3.5MHz
Max FPS: 11 FPS (too slow!)
```

### Performance With Edge Optimization

```
Typical scroll: 10-15 edge tiles × 64 bytes = 640-960 bytes
~64,000-96,000 cycles = 18-27ms
FPS: 37-55 FPS (excellent!)

Speedup: 3-5x
```

### What Counts as an Edge?

```
1. Wall-to-floor boundary
   ████ ← Wall
   ▓▓▓▓ ← Floor (edge here)

2. Floor-to-fog boundary
   ▓▓▓▓ ← Explored floor
   ░░░░ ← Fog (edge here)

3. Different floor types
   ▓▓▓▓ ← Stone
   ▒▒▒▒ ← Wood (edge here)

4. Screen edge
   New tiles appearing/disappearing
```

## Scrolling Implementation

### Player Movement

```asm
; Player moves north in world
MovePlayerNorth:
    ; Check if tile ahead is walkable
    LD HL, (PlayerWorldY)
    DEC HL              ; Y-1 (north)
    LD DE, (PlayerWorldX)
    CALL GetTileAt

    CP TILE_WALL
    RET Z               ; Can't walk into wall

    ; Move is valid
    LD HL, (PlayerWorldY)
    DEC HL
    LD (PlayerWorldY), HL

    ; Mark tile as explored
    CALL MarkExplored

    ; Camera follows (smooth scroll)
    CALL ScrollCameraNorth

    RET
```

### Smooth Scrolling (4-pixel increments)

```asm
; Scroll camera north smoothly
ScrollCameraNorth:
    LD A, (ScrollPhase)
    CP 8
    JR Z, .NewTile

    ; Sub-tile scroll
    INC A
    LD (ScrollPhase), A

    ; Update pixel offset
    LD HL, (CameraOffsetX)
    LD DE, 4
    ADD HL, DE          ; +4 pixels X
    LD (CameraOffsetX), HL

    LD HL, (CameraOffsetY)
    LD DE, 2
    OR A
    SBC HL, DE          ; -2 pixels Y
    LD (CameraOffsetY), HL

    ; Mark edges dirty
    CALL MarkScrollEdges

    ; Redraw dirty edges
    CALL RedrawDirtyTiles

    RET

.NewTile:
    ; Completed full tile scroll
    XOR A
    LD (ScrollPhase), A

    ; Reset offsets
    ; Update chunk if needed
    CALL UpdateChunks

    ; Mark new tile row dirty
    CALL MarkNewTilesDirty

    RET
```

### Diagonal Movement (Isometric)

```
World direction → Screen scroll:

North: +4 pixels X, -2 pixels Y per frame
East:  +4 pixels X, +2 pixels Y per frame
South: -4 pixels X, +2 pixels Y per frame
West:  -4 pixels X, -2 pixels Y per frame

8 frames = full tile (32×16 pixels)
2:1 ratio maintained
```

## Fog of War (Essential Feature)

### Exploration Tracking

```asm
; Each chunk has exploration bitmap
; 9×9 tiles = 81 bits = 11 bytes

ExploredMap:
    DEFS 11         ; Bitmap for current chunks

MarkExplored:
    ; Input: B = tile X, C = tile Y
    ; Calculate bit index
    LD A, C
    ADD A, A
    ADD A, A
    ADD A, A        ; Y × 8
    ADD A, C        ; Y × 9
    ADD A, B        ; + X = index

    ; Convert to byte + bit
    LD D, A
    SRL A
    SRL A
    SRL A           ; Divide by 8 = byte index

    LD HL, ExploredMap
    LD E, 0
    ADD HL, DE

    ; Get bit position
    LD A, D
    AND $07
    LD B, A
    LD A, 1
.ShiftLoop:
    OR A
    JR Z, .Done
    SLA A
    DJNZ .ShiftLoop
.Done:
    ; Set bit
    OR (HL)
    LD (HL), A
    RET
```

### Fog Rendering

```asm
DrawTile:
    ; Check if explored
    CALL IsExplored
    JR NZ, .DrawFog

    ; Explored - draw actual tile
    CALL DrawFloorTile
    RET

.DrawFog:
    ; Not explored - draw fog
    LD HL, TILE_FOG_DATA
    CALL DrawFloorTile
    RET
```

### Partial Fog (Memory Optimization)

```
Only remember exploration for current chunk:
- When entering new chunk, fog resets
- OR: Track exploration globally with sparse storage
  - List of explored (X,Y) coordinates
  - Max ~1000 tiles = 2KB
```

## Procedural Generation (Rooms & Corridors)

### Room-Based Algorithm

```asm
; Generate chunk at world position
; Input: BC = chunk X, DE = chunk Y
GenerateChunk:
    ; Use position + seed for determinism
    LD HL, (LevelSeed)
    ADD HL, BC
    ADD HL, DE
    LD (RNG_State), HL

    ; Clear chunk to walls
    CALL FillChunkWalls

    ; Generate 1-3 rooms in this chunk
    LD A, (RNG_State)
    AND $03
    INC A               ; 1-4 rooms
    LD B, A

.RoomLoop:
    PUSH BC
    CALL GenerateRoom
    POP BC
    DJNZ .RoomLoop

    ; Connect rooms with corridors
    CALL GenerateCorridors

    ; Place special features
    CALL PlaceStairs
    CALL PlaceGold
    CALL PlaceMonsters

    RET

GenerateRoom:
    ; Random position in chunk
    CALL Random
    AND $07             ; 0-7
    LD B, A             ; Room X

    CALL Random
    AND $07
    LD C, A             ; Room Y

    ; Random size (3-6 tiles)
    CALL Random
    AND $03
    ADD A, 3
    LD D, A             ; Width

    CALL Random
    AND $03
    ADD A, 3
    LD E, A             ; Height

    ; Carve out room (set to floor)
    CALL CarveRoom
    RET
```

### Corridor Generation

```asm
; Connect rooms with L-shaped corridors
ConnectRooms:
    ; Get room1 center
    LD BC, (Room1_Center)
    ; Get room2 center
    LD DE, (Room2_Center)

    ; Draw horizontal corridor
.Horizontal:
    LD A, B
    CP D
    JR Z, .Vertical
    JR C, .GoRight

.GoLeft:
    DEC B
    CALL SetFloor
    JR .Horizontal

.GoRight:
    INC B
    CALL SetFloor
    JR .Horizontal

    ; Draw vertical corridor
.Vertical:
    LD A, C
    CP E
    RET Z
    JR C, .GoDown

.GoUp:
    DEC C
    CALL SetFloor
    JR .Vertical

.GoDown:
    INC C
    CALL SetFloor
    JR .Vertical
```

## Gameplay Elements

### Monster Placement

```asm
; 1-3 monsters per room
PlaceMonsters:
    ; For each room
    LD A, (RoomCount)
    LD B, A

.RoomLoop:
    PUSH BC

    ; Random monster count (1-3)
    CALL Random
    AND $03
    INC A
    LD C, A

.MonsterLoop:
    PUSH BC

    ; Random position in room
    CALL GetRandomRoomPos

    ; Choose monster type (by depth)
    LD A, (DungeonLevel)
    SRL A
    SRL A
    AND $03
    INC A           ; Monster type 1-4

    ; Place monster
    CALL PlaceMonster

    POP BC
    DEC C
    JR NZ, .MonsterLoop

    POP BC
    DJNZ .RoomLoop
    RET
```

### Gold & Treasure

```asm
; More gold in deeper levels
PlaceGold:
    LD A, (DungeonLevel)
    ADD A, A
    ADD A, 5        ; 5-50 gold pieces
    LD B, A

.GoldLoop:
    ; Random floor position
    CALL GetRandomFloorPos

    ; Gold amount
    LD A, (DungeonLevel)
    ADD A, A
    ADD A, 10       ; 10+ × level

    CALL PlaceGoldPile

    DJNZ .GoldLoop
    RET
```

### Stairs

```asm
; Always place stairs down in each level
PlaceStairs:
    ; Find random room
    CALL GetRandomRoom

    ; Center of room
    CALL GetRoomCenter

    ; Place stairs
    LD A, TILE_STAIRS_DOWN
    CALL SetTile

    RET
```

## Performance Targets (7×7 Grid, Single Layer)

### With Edge-Based Optimization

```
Simple corridor scroll:
- Redraw: 10 tiles × 64 bytes = 640 bytes
- Cycles: ~64,000
- Time: 18ms at 3.5MHz
- FPS: 55 FPS ✓

Complex room scroll:
- Redraw: 15 tiles × 64 bytes = 960 bytes
- Cycles: ~96,000
- Time: 27ms
- FPS: 37 FPS ✓

With game logic (monsters, items):
- Target: 25-30 FPS (smooth and playable!)
```

## Advantages of Single-Layer Design

### vs Multi-Layer (Ragnar Revival)

**Simplicity:**
- ✓ No Z-sorting
- ✓ Simpler rendering
- ✓ Easier collision detection
- ✓ Less memory for world data

**Performance:**
- ✓ Faster rendering (no depth sorting)
- ✓ Edge optimization more effective
- ✓ More cycles for game logic

**Gameplay:**
- ✓ Clearer dungeon layout
- ✓ Easier for player to navigate
- ✓ Focus on exploration, not 3D puzzles

**Development:**
- ✓ Faster to implement
- ✓ Easier to debug
- ✓ More time for gameplay features

## Implementation Phases

### Phase 1: Static Room (1-2 weeks)
- [x] Define tile format (32×16 diamonds)
- [ ] Create basic floor tile graphics
- [ ] Create wall tile graphics
- [ ] Render static 7×7 room
- [ ] Test on emulator

### Phase 2: Player Movement (1 week)
- [ ] Add player sprite
- [ ] Implement tile-based movement (jump full tiles)
- [ ] Add collision detection (walls)
- [ ] Test control responsiveness

### Phase 3: Smooth Scrolling (2 weeks)
- [ ] Implement 4-pixel scroll increments
- [ ] Add edge detection
- [ ] Optimize dirty rectangle system
- [ ] Achieve 30+ FPS

### Phase 4: Fog of War (1 week)
- [ ] Exploration tracking
- [ ] Fog rendering
- [ ] Smooth fog reveal when exploring

### Phase 5: Procedural Generation (2 weeks)
- [ ] Chunk system
- [ ] Room generation
- [ ] Corridor generation
- [ ] Stairs placement

### Phase 6: Gameplay (2-3 weeks)
- [ ] Monsters (AI, combat)
- [ ] Gold and items
- [ ] Inventory system
- [ ] Health and stats

### Phase 7: Polish (1-2 weeks)
- [ ] Sound effects
- [ ] Title screen
- [ ] Game over screen
- [ ] Score/progress tracking

**Total: ~10-14 weeks to playable game!**

## Comparison: Fargoal vs Ragnar Revival

| Feature | Sword of Fargoal | Ragnar Revival |
|---------|------------------|----------------|
| Grid size | 7×7 visible | 8×8 visible |
| Layers | 1 (flat) | 8 (height) |
| Complexity | Medium | High |
| Rendering | Simple | Complex (Z-sort) |
| Memory | Light (~3KB) | Heavy (~6KB) |
| Performance | 30-55 FPS | 20-35 FPS |
| Development | 10-14 weeks | 16-24 weeks |
| Genre | Roguelike RPG | Puzzle/Action |

## Conclusion

Single-layer isometric design for Sword of Fargoal is **much more practical**:

✅ Simpler to implement
✅ Better performance
✅ Faster development
✅ Still looks great in isometric
✅ Perfect for roguelike dungeon crawling

Combined with:
- Edge-based scrolling optimization
- Procedural generation
- Fog of war
- Smooth 4-pixel scrolling

You'll have something genuinely impressive and unique for the ZX Spectrum! 🗡️✨
