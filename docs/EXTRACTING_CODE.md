# Extracting Code from .z80 Snapshot Files

Your original Ragnar demo is stored in `Ragnar (demo).z80`, which is a snapshot file containing the complete memory state of the ZX Spectrum at a specific moment. To continue development, you'll want to extract and disassemble the code.

## Understanding .z80 Snapshot Format

A .z80 file contains:
- CPU register states (A, BC, DE, HL, IX, IY, SP, PC, etc.)
- All 48KB (or 128KB) of memory
- Hardware state (border color, interrupt mode, etc.)

The actual program code and data are embedded in this memory dump.

## Method 1: Using SkoolKit (Recommended)

SkoolKit is a collection of tools for reverse-engineering ZX Spectrum software.

### Installation

**Linux/macOS:**
```bash
pip3 install skoolkit
```

**Windows:**
```batch
pip install skoolkit
```

### Extract and Disassemble

```bash
# Convert .z80 to binary files
z80sna.py "Ragnar (demo).z80" ragnar.sna

# Create a basic disassembly
sna2ctl.py ragnar.sna > ragnar.ctl
sna2skool.py -c ragnar.ctl ragnar.sna > ragnar.skool

# Generate assembly source
skool2asm.py ragnar.skool > ragnar.asm
```

This will create a basic disassembly, but it won't know which parts are code vs data.

### Improved Disassembly

For better results, you'll need to help SkoolKit identify code vs data:

1. Load the .z80 file in ZEsarUX debugger
2. Find the entry point (PC register)
3. Identify major routines and data blocks
4. Create a control file to guide the disassembly

## Method 2: Manual Disassembly with ZEsarUX

This gives you more control but is more time-consuming.

### Steps:

1. **Load the snapshot in ZEsarUX**
   - Launch ZEsarUX
   - File → Load Snapshot → Select `Ragnar (demo).z80`

2. **Open the debugger**
   - F5 or Debug → Open debugger

3. **Find the entry point**
   - Look at the PC (Program Counter) register
   - This is where your code starts
   - Common locations: $8000, $6000, $5B00

4. **Identify code sections**
   - Step through code (F7 for step-over, F8 for step-into)
   - Look for patterns:
     - Game loop
     - Interrupt handlers
     - Graphics routines
     - Data tables

5. **Export memory blocks**
   - Debug → Memory dump
   - Save relevant sections
   - Common ranges:
     - $4000-$5AFF: Screen data
     - $5B00+: Program code often starts here
     - $8000+: Safe user area, commonly used

6. **Manually disassemble**
   - Use a Z80 disassembler or do it by hand
   - Add meaningful labels and comments
   - Separate code from data

## Method 3: Interactive Exploration

Sometimes the best approach is to explore the code interactively:

### Using ZEsarUX Debugger:

1. **Set breakpoints**
   - Find loops and routines
   - Set breakpoints to understand flow

2. **Watch memory**
   - View screen memory ($4000)
   - Watch variables change
   - Identify data structures

3. **Trace execution**
   - Use trace mode to record execution
   - Analyze the trace log
   - Identify major sections

4. **Document findings**
   - Create a memory map
   - Label important routines
   - Note register usage

## Memory Map Template

Create `docs/memory_map.md` to document your findings:

```markdown
# Ragnar Revival Memory Map

## Screen Memory
- $4000-$57FF: Screen pixel data (6144 bytes)
- $5800-$5AFF: Screen attributes (768 bytes)

## Program Code
- $????-$????: Main program entry point
- $????-$????: Graphics routines
- $????-$????: 3D engine
- $????-$????: Game logic

## Data
- $????-$????: Sprite data
- $????-$????: Tile data
- $????-$????: Level data

## Variables
- $????: Player X position
- $????: Player Y position
- $????: Game state

## Stack
- $????: Stack pointer initial value
```

## Tips for Understanding Your Old Code

### Common Patterns to Look For:

1. **Initialization**
   - Setting up screen mode
   - Clearing memory
   - Setting up interrupt handlers

2. **Main Loop**
   - Usually a JP or JR instruction that loops back
   - Look for HALT instructions (wait for frame)

3. **Keyboard Reading**
   - IN A, (PORT) instructions
   - Port $FE for keyboard
   - BIT tests on the result

4. **Screen Drawing**
   - Writes to $4000-$5AFF range
   - LD (HL), A or similar instructions
   - Often uses LDIR for block copies

5. **3D Isometric Routines**
   - Coordinate transformation math
   - Lookup tables for screen positions
   - Sprite plotting routines

### Z80 Patterns from the 1980s:

You probably used these techniques:

- **Unrolled loops** for speed
- **Self-modifying code** (LD instructions with calculated addresses)
- **Lookup tables** instead of multiplication
- **Bit shifting** for fast division/multiplication by 2
- **Register optimization** (using alternate registers with EXX)

## Reconstructing the Source

Once you understand the code:

1. **Start with a skeleton**
   ```asm
   ; Main program
   ORG $8000  ; or wherever your code started

   Start:
       ; Initialization
       ; ...

   MainLoop:
       ; Game loop
       ; ...
       JR MainLoop
   ```

2. **Add routines one at a time**
   - Copy from disassembly
   - Add meaningful labels
   - Comment extensively

3. **Identify and extract data**
   - Sprite definitions
   - Level data
   - Lookup tables

4. **Modularize**
   - Split into logical files
   - Create include files for data
   - Use macros for repeated patterns

## Example Workflow

```bash
# 1. Load snapshot in ZEsarUX
# 2. Explore and document in docs/memory_map.md
# 3. Export key memory regions

# 4. Create initial source structure
mkdir -p src/{main,graphics,engine,data}

# 5. Start with main program
# Copy entry point code to src/main/start.asm

# 6. Extract graphics routines
# Copy to src/graphics/render.asm

# 7. Extract 3D engine
# Copy to src/engine/iso3d.asm

# 8. Extract data
# Copy to src/data/sprites.asm

# 9. Create main assembly file
# src/ragnar.asm that includes all modules
```

## Automated Tools

Some tools that might help:

- **z80dasm**: Command-line Z80 disassembler
- **IDA Pro Free**: Professional disassembler (has Z80 support)
- **Ghidra**: Free disassembler from NSA (with Z80 processor module)
- **ZXDoc**: Documentation and analysis tool

## Next Steps

1. Load `Ragnar (demo).z80` in ZEsarUX
2. Explore the code using the debugger
3. Document what you find in `docs/memory_map.md`
4. Start extracting and commenting code sections
5. Build up your source files incrementally
6. Test frequently by reassembling and comparing behavior

Remember: You wrote this code 40 years ago. Your style, your logic, your cleverness is in there. Trust your past self and enjoy rediscovering your own work!
