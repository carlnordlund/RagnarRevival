# Getting Started with Ragnar Revival Development

This quick guide will get you from zero to coding in about 30 minutes.

## Prerequisites

- Windows, Linux, or macOS
- Internet connection for downloads
- Basic familiarity with GitHub (you already have this!)

## Step-by-Step Setup

### 1. Install Visual Studio Code (5 minutes)

1. Go to https://code.visualstudio.com/
2. Download for your platform
3. Install with default options
4. Launch VS Code

### 2. Install Required Extensions (5 minutes)

In VS Code:
1. Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
2. Search for "Z80 Assembly" by Imanolea
3. Click Install
4. Search for "DeZog" by maziac
5. Click Install

### 3. Install sjasmplus Assembler (10 minutes)

**Windows:**
```batch
# Download from https://github.com/z00m128/sjasmplus/releases
# Extract to C:\sjasmplus
# Add C:\sjasmplus to your PATH:
#   Windows 11/10: Settings → System → About → Advanced System Settings → Environment Variables
#   Add C:\sjasmplus to the PATH variable
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install sjasmplus
```

**macOS:**
```bash
# If you don't have Homebrew, install it first from https://brew.sh
brew install sjasmplus
```

Verify installation:
```bash
sjasmplus --version
```

### 4. Install ZEsarUX Emulator (5 minutes)

1. Download from: https://github.com/chernandezba/zesarux/releases
2. Choose your platform:
   - Windows: `ZEsarUX-Windows-XX.zip`
   - Linux: `ZEsarUX-Linux-XX.tar.gz`
   - macOS: `ZEsarUX-MacOS-XX.dmg`
3. Extract/install to a location you'll remember
4. Run it once to make sure it works

### 5. Open This Repository in VS Code (2 minutes)

1. In VS Code, select File → Open Folder
2. Navigate to this repository folder
3. Click Select Folder

### 6. Create Your First Source File (3 minutes)

Create a folder structure:
```bash
mkdir -p src build
```

Create `src/test.asm`:
```asm
; Simple test program
    DEVICE ZXSPECTRUM48
    ORG $8000

Start:
    LD A, 2
    CALL $1601
    LD HL, Message
PrintLoop:
    LD A, (HL)
    OR A
    RET Z
    RST $10
    INC HL
    JR PrintLoop

Message:
    DEFB "RAGNAR LIVES!", 0

    SAVETAP "build/test.tap", CODE, Start, $ - Start
```

### 7. Build and Run (5 minutes)

Build the program:
```bash
sjasmplus src/test.asm
```

You should see `build/test.tap` created.

Load in ZEsarUX:
1. Launch ZEsarUX
2. Machine → Spectrum 48K (if not already selected)
3. Storage → Tape → Insert tape
4. Select `build/test.tap`
5. In the emulator, type: `LOAD ""`
6. Press Enter
7. The program should load and display "RAGNAR LIVES!"

## What Next?

### Extract Original Code

Your original demo is in `Ragnar (demo).z80`. You'll want to:

1. **Disassemble it**: Use a tool like SkoolKit or manually step through it in ZEsarUX
2. **Document it**: Add comments to understand what each section does
3. **Refactor it**: Split into logical modules (graphics, game logic, etc.)

### Project Ideas

Start with one of these:

1. **Enhance the Original Demo**
   - Add keyboard controls to move around
   - Add more block types
   - Implement collision detection

2. **Build the 8-Layer Engine**
   - Design the data structure
   - Write the rendering routine
   - Test with simple blocks

3. **Sword of Fargoal in Machine Code**
   - Start with the map generation algorithm
   - Create the character movement routines
   - Add the basic game loop

### Learning Resources

If you're rusty on Z80 assembly:

1. **Quick Reference**: Keep http://www.z80.info/z80oplist.txt bookmarked
2. **ROM Routines**: https://skoolkid.github.io/rom/ - the Spectrum ROM has useful routines
3. **Tutorial**: http://www.z80.info/z80code.htm

### Development Rhythm

A good workflow:
1. Code for 20-30 minutes
2. Build and test
3. Commit to Git if it works
4. Repeat

Don't try to write too much before testing!

## Tips from the 1980s vs 2026

**Then:**
- Typed directly into the assembler
- Assembled and waited
- If it crashed, start over
- No source control

**Now:**
- Multiple monitors/windows
- Instant assembly
- Step through with debugger
- Git tracks every change
- Can test on real hardware OR emulator

## Common Issues

**"sjasmplus: command not found"**
- The assembler isn't installed or not in PATH
- On Windows, make sure you added it to PATH and restarted your terminal

**"Error: unknown device"**
- Add `DEVICE ZXSPECTRUM48` at the start of your .asm file

**Can't load TAP file in emulator**
- Make sure SAVETAP directive is correct
- Check that the TAP file was actually created
- Try a different emulator (sometimes format quirks exist)

**Emulator crashes**
- Your code might be jumping to invalid addresses
- Use the debugger to step through and find where it goes wrong

## Next Steps

Read the full [DEVELOPMENT.md](DEVELOPMENT.md) guide for:
- Advanced debugging with DeZog
- VS Code task automation
- Memory management tips
- File format details

## Get Coding!

The ZX Spectrum is waiting for you. Time to revive Ragnar!

Remember: In 1985, you had 48KB and no tools. In 2026, you have unlimited storage, instant assembly, full debugging, and Git. You've got this!
