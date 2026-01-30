# Edge-Based Scrolling: Practical Examples

## Example 1: Simple Corridor Scroll

### Initial View (8×8 tiles visible)

```
Player view (isometric):

     ███████████████████
    ███████████████████
   ███████████████████
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓▓▓▓▓▓▓▓@▓▓▓▓▓▓▓▓▓▓   @ = Player (centered)
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ███████████████████
  ███████████████████

Tiles marked for edges:
     ███████████████████
    █**************█   ← Top wall edge
   █              █
  ▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓ ▓    ← Wall-to-floor edges (left/right)
 ▓ ▓▓▓▓▓▓@▓▓▓▓▓▓▓ ▓
▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ▓
 █              █      ← Floor-to-wall edges
  █**************█     ← Bottom wall edge

** = Edge tiles that might change when scrolling
```

### Player Moves Right (camera scrolls right)

```
New view:
     ████████████████████
    ████████████████████
   ████████████████████
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓▓▓▓▓▓▓▓▓@▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ████████████████████
  ████████████████████

What was redrawn:
    NEW
     ↓
     █████████████████████  ← Right edge extended
    █████████████████████
   █████████████████████
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ← Right floor edge
 ▓▓▓▓▓▓▓▓▓▓@▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 █████████████████████
  █████████████████████

Only 2 vertical strips redrawn!
- Right wall edge (3 tiles)
- Right floor edge (3 tiles)
- Right wall edge bottom (3 tiles)
Total: ~9 tiles instead of 64
```

## Example 2: Emerging from Fog of War

### Before: At Edge of Explored Area

```
     ███████████░░░░░░░
    ███████████░░░░░░░░
   ███████████░░░░░░░░░
  ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░
 ▓▓▓▓▓@▓▓▓▓▓▓░░░░░░░░░  @ = Player
▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░
 ███████████░░░░░░░░░░
  ███████████░░░░░░░░░
           ↑
    Fog of war boundary
```

### After: Player Moves Right (exploring new area)

```
     ███████████████░░░░
    ███████████████░░░░
   ███████████████░░░░
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░
 ▓▓▓▓▓▓@▓▓▓▓▓▓▓▓░░░░░
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░
 ███████████████░░░░░
  ███████████████░░░░
               ↑
    New fog boundary

Redrawn:
- Right edge: Fog cleared, new wall/floor revealed
- Previous fog edge: Cleared
- New fog edge: Drawn
- Newly explored tiles: Drawn once, then remembered

Tiles redrawn: ~12-15
- New right column (8 tiles)
- Updated fog boundary (4-7 tiles)
```

## Example 3: Room with Multiple Ground Types

### Initial View: Stone Floor Room

```
Isometric view:
     ███████████████████
    ███████████████████
   ███████████████████
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    Stone floor (gray)
 ▓▓▓▓▓@▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒      Wood floor (brown)
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒

Edge types detected:
- Wall-to-stone-floor (top)
- Stone-to-wood transition (middle) ← Important edge!
- Wood-to-boundary (bottom)
```

### Scroll Down: Wood Floor Comes into View

```
New view:
     ███████████████████
    ███████████████████
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓@▓▓▓▓▓▓▓▓▓▓
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▒▒▒▒▒▒▒▒▒▒▒▒      New wood floor rows

Redrawn:
- Top rows: Walls scrolling out (disappeared)
- Bottom rows: New wood floor (appeared)
- Stone-to-wood edge: Repositioned
- Wall-to-stone edge: Repositioned

Efficient because:
- Stone floor middle: UNCHANGED (no redraw)
- Wood floor middle: UNCHANGED (no redraw)
- Only boundaries moved!
```

## Example 4: Complex Scene with Multiple Wall Segments

### Initial Scene: Dungeon Intersection

```
Top-down logic view:
███░░░███
███░░░███
███▓▓▓███
░░░▓@▓░░░  @ = Player
███▓▓▓███
███░░░███
███░░░███

Isometric render:
     ███  ███
    ███  ███
   ███  ███
  ███▓▓▓███
 ░░░▓@▓░░░
███▓▓▓███
 ███  ███
  ███  ███

Edge tiles (marked with *):
     ███  ███
    ███* *███      ← Wall segment ends
   ███*  *███
  ███*▓▓▓*███      ← Multiple edges
 ░░░*▓@▓*░░░       ← Floor-to-fog edges
███*▓▓▓*███
 ███*  *███
  ███* *███
    ███  ███

Many edges due to complex geometry!
```

### Scroll Right: Revealing East Corridor

```
New view:
     ███  ████████
    ███  ████████
   ███  ████████
  ███▓▓▓████████
 ░░░▓▓@▓▓▓▓▓░░░  New corridor floor
███▓▓▓████████
 ███  ████████
  ███  ████████

Redrawn:
- Right side: New wall segment appeared
- Right side: New floor corridor
- Left side: West corridor disappeared
- Center: Floor extended east

Smart algorithm:
1. Detect right edge: new wall segments
2. Detect right edge: floor extension
3. Left edge: mark disappeared tiles as fog
4. Center floor: NO REDRAW (continuous)

Tiles: ~15-20 instead of 64
```

## Example 5: Smooth Sub-Pixel Scrolling

### Using Pre-Shifted Sprites

```
Frame 1 (pixel offset: 0):
     ███████████████
    ███████████████
   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓@▓▓▓▓▓▓▓▓▓▓

Frame 2 (pixel offset: +2):
     ██ ███████████████
    ██ ███████████████
   ▓▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓ ▓▓@▓▓▓▓▓▓▓▓▓▓▓
   ↑ Only this strip new!

Frame 3 (pixel offset: +4):
     ████ ███████████████
    ████ ███████████████
   ▓▓▓▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓ ▓▓@▓▓▓▓▓▓▓▓▓▓▓
     ↑ More of strip revealed

Frame 4 (pixel offset: +8, tile boundary):
     ████████ ███████████
    ████████ ███████████
   ▓▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓ ▓@▓▓▓▓▓▓▓▓
         ↑ New edge strip complete
```

Each sub-pixel scroll:
- Uses pre-shifted sprite data
- Only draws 1-2 pixel columns
- Creates incredibly smooth motion
- Still only updating edges!

## Example 6: Water/Special Floor Transition

### Approaching Water

```
Initial:
     ███████████████
    ███████████████
   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   Stone floor
  ▓▓▓▓@▓▓▓▓▓▓▓▓▓▓▓
 ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈   Water (special tile)
  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

Edge at stone-to-water:
Special transition tile with blend:
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓≈▓≈▓≈▓≈▓≈▓≈▓≈▓   ← Transition
  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
```

When scrolling across water boundary:
1. Detect floor type change
2. Select appropriate transition tile
3. Redraw edge with blended tile
4. Water tiles can be animated independently!

## Example 7: Diagonal Scrolling

### Isometric View Natural Diagonal

Moving northeast in world = moving up-right on screen:

```
Frame 1:
     ███████████
    ███████████
   ▓▓▓▓▓▓▓▓▓▓▓
  ▓▓▓▓@▓▓▓▓▓▓▓
 ▓▓▓▓▓▓▓▓▓▓▓▓

Frame 2 (moved NE):
      ████████████
     ████████████
    ▓▓▓▓▓▓▓▓▓▓▓▓
   ▓▓▓▓▓@▓▓▓▓▓▓▓
  ▓▓▓▓▓▓▓▓▓▓▓▓▓

Redrawn:
- Top-right: New tiles appearing
- Bottom-left: Old tiles disappearing
- Diagonal edge strip

Tiles: ~12-16 (still efficient!)
```

## Performance Calculation Examples

### Example 1: Simple Corridor

**Full redraw:**
- 64 tiles × 32 bytes = 2048 bytes
- ~200,000 cycles
- ~57ms at 3.5MHz

**Edge-based:**
- 9 tiles × 32 bytes = 288 bytes
- ~28,000 cycles
- ~8ms at 3.5MHz

**Speedup: 7x faster!**

### Example 2: Complex Intersection

**Full redraw:**
- 64 tiles = ~200,000 cycles = 57ms

**Edge-based:**
- 20 tiles × 32 bytes = 640 bytes
- ~64,000 cycles
- ~18ms at 3.5MHz

**Speedup: 3x faster**

### Example 3: Sub-Pixel Scroll (2-pixel increment)

**Traditional:**
- Would need full redraw every 2 pixels
- Impractical!

**Edge-based with pre-shift:**
- 2 pixel columns = ~8-16 bytes
- ~2,000 cycles
- ~0.5ms

**Enables smooth scrolling that was impossible before!**

## Memory Requirements by Example

### Simple Corridor

```
Edge map: 8 bytes (64 tiles / 8 bits)
Dirty list: 20 bytes (10 edges × 2 coords)
Total: ~28 bytes
```

### Complex Intersection

```
Edge map: 8 bytes
Dirty list: 40 bytes (20 edges × 2 coords)
Pre-calc cache: 128 bytes (common patterns)
Total: ~176 bytes
```

### Full Implementation

```
Edge system: 300 bytes
Fog of war map: 64 bytes (1 bit per tile × 64 tiles / 8)
Transition tiles: 512 bytes (16 transitions × 32 bytes)
Pre-shift cache: 1024 bytes (if using sub-pixel)
Total: ~1900 bytes (<2KB)

For the capability enabled, this is excellent!
```

## Practical Tips

### Tip 1: Design Tiles for Seamless Tiling

Make sure adjacent wall tiles blend together:

```
Bad (visible seams):
████│████│████
────┼────┼────  ← Seams visible
▓▓▓▓│▓▓▓▓│▓▓▓▓

Good (seamless):
████████████████
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← Can't see individual tiles
```

### Tip 2: Use Transition Tiles

Create special tiles for common transitions:

```
Wall-to-floor transition:
████████████████
███████▓▓▓▓▓▓▓▓  ← Smooth gradation
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

Better than hard edge:
████████████████
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← Abrupt
```

### Tip 3: Update Fog of War Efficiently

```
Mark explored when player enters tile:
- Set bit in exploration bitmap
- Don't re-draw fog tiles that are already drawn
- Only draw fog edges as they're revealed
```

### Tip 4: Cache Edge Patterns

```
Pre-render common edge patterns:
- Vertical wall edge
- Horizontal wall edge
- Corner pieces
- Transitions

Look up and blit instead of calculating!
```

## Implementation Checklist

- [ ] Design seamless wall tiles
- [ ] Design seamless floor tiles (multiple types)
- [ ] Create transition tiles for each floor type combination
- [ ] Implement basic edge detection
- [ ] Test with static scene
- [ ] Implement tile-based scrolling with edge updates
- [ ] Add fog of war integration
- [ ] Optimize with lookup tables
- [ ] (Optional) Add sub-pixel scrolling with pre-shift
- [ ] Test with complex scenes
- [ ] Profile performance
- [ ] Polish visual transitions

## Next Steps

1. **Create test scene** with simple corridor
2. **Implement edge detector** (start basic)
3. **Test scrolling** one tile at a time
4. **Measure performance** (count cycles)
5. **Add complexity** gradually (fog, ground types)
6. **Optimize** with profiling data
7. **Add smoothness** (sub-pixel if cycles permit)

This edge-based approach makes your vision of smooth-scrolling infinite dungeons genuinely achievable on the ZX Spectrum! 🎮
