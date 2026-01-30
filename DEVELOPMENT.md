# ZX Spectrum Development Guide

This guide will help you set up a modern development environment for ZX Spectrum Z80 assembly programming using Visual Studio Code and GitHub.

## Quick Start

1. Install Visual Studio Code
2. Install sjasmplus assembler
3. Install a ZX Spectrum emulator
4. Install VS Code extensions for Z80 development
5. Start coding!

## Detailed Setup Instructions

### 1. Install Visual Studio Code

Download and install from: https://code.visualstudio.com/

**Note:** This is different from Visual Studio Community Edition. VS Code is a lightweight, cross-platform code editor perfect for assembly development.

### 2. Install Z80 Assembler

#### Option A: sjasmplus (Recommended)

**Windows:**
- Download from: https://github.com/z00m128/sjasmplus/releases
- Extract to a folder (e.g., `C:\sjasmplus`)
- Add to PATH environment variable

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install sjasmplus

# Or build from source
git clone https://github.com/z00m128/sjasmplus
cd sjasmplus
make
sudo make install
```

**macOS:**
```bash
brew install sjasmplus
```

#### Option B: pasmo

**Windows:**
- Download from: http://pasmo.speccy.org/

**Linux:**
```bash
sudo apt-get install pasmo
```

**macOS:**
```bash
brew install pasmo
```

### 3. Install ZX Spectrum Emulator

#### ZEsarUX (Best for debugging)
- Download: https://github.com/chernandezba/zesarux/releases
- Cross-platform (Windows, Linux, macOS)
- Excellent debugging features
- Integrates with DeZog extension

#### Fuse (Most accurate)
- Download: http://fuse-emulator.sourceforge.net/
- Cross-platform
- Very accurate emulation

#### SpecEmu (Windows)
- Download: http://www.zxemulator.com/
- Windows-focused
- Good for quick testing

### 4. Install VS Code Extensions

Open VS Code and install these extensions:

1. **Z80 Assembly** (by Imanolea)
   - Syntax highlighting
   - Code snippets
   - IntelliSense support

2. **DeZog** (by maziac)
   - Full debugging with ZEsarUX
   - Breakpoints, watch variables, step through code
   - Memory viewer

3. **Z80 Instruction Set** (by maziac)
   - Quick reference for Z80 instructions
   - Hover tooltips with instruction details

To install:
- Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)
- Search for each extension and click Install

### 5. Project Structure

Recommended folder structure:

```
RagnarRevival/
├── src/
│   ├── main.asm          # Main source file
│   ├── graphics.asm      # Graphics routines
│   ├── engine.asm        # 3D engine
│   └── data.asm          # Sprite/tile data
├── build/
│   ├── output.tap        # Compiled TAP file
│   └── output.z80        # Compiled Z80 snapshot
├── tools/
│   └── build.sh          # Build script
├── docs/
│   └── design.md         # Game design docs
└── README.md
```

### 6. Basic Build Configuration

Create a simple build script:

**build.sh (Linux/macOS):**
```bash
#!/bin/bash
sjasmplus src/main.asm --lst --raw=build/output.bin
# Add conversion to TAP/Z80 format as needed
```

**build.bat (Windows):**
```batch
@echo off
sjasmplus src\main.asm --lst --raw=build\output.bin
```

Make it executable:
```bash
chmod +x build.sh
```

### 7. VS Code Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build ZX Spectrum",
            "type": "shell",
            "command": "sjasmplus",
            "args": [
                "${workspaceFolder}/src/main.asm",
                "--lst",
                "--raw=${workspaceFolder}/build/output.bin"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}
```

Now you can build with `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (macOS).

### 8. DeZog Debugging Setup

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "dezog",
            "request": "launch",
            "name": "Debug with ZEsarUX",
            "remoteType": "zesarux",
            "zesarux": {
                "zesaruxPath": "/path/to/zesarux",
                "port": 10000,
                "loadSnap": "${workspaceFolder}/build/output.z80"
            },
            "listFiles": [
                {
                    "path": "${workspaceFolder}/build/output.lis",
                    "useFiles": true,
                    "asm": "sjasmplus"
                }
            ]
        }
    ]
}
```

## Development Workflow

1. **Write Code**: Edit `.asm` files in VS Code with syntax highlighting
2. **Build**: Press `Ctrl+Shift+B` to assemble
3. **Test**: Load the output file in your emulator
4. **Debug**: Use DeZog with ZEsarUX for step-through debugging
5. **Commit**: Use Git integration in VS Code (`Ctrl+Shift+G`)
6. **Push**: Push to GitHub regularly

## Useful Resources

### Learning Z80 Assembly

- **ZX Spectrum Assembly Tutorial**: http://www.z80.info/z80code.htm
- **Z80 Instruction Set**: http://www.z80.info/z80oplist.txt
- **Spectrum ROM Disassembly**: https://skoolkid.github.io/rom/
- **World of Spectrum**: https://worldofspectrum.org/

### Tools and Utilities

- **ZX Paintbrush**: Create graphics for your game
- **SevenuP**: Tile/sprite editor
- **BeepFX**: Sound effect generator
- **Arkos Tracker 2**: Music creation

### Communities

- **Speccy.pl Forums**: Active community
- **World of Spectrum Forums**: Classic resource
- **Reddit r/zxspectrum**: Modern community
- **ZX Spectrum Discord**: Real-time chat

## Tips for Modern ZX Spectrum Development

1. **Use Git**: Commit frequently, even for small changes
2. **Modular Code**: Split your code into logical files (main, graphics, sound, etc.)
3. **Comment Everything**: Future you will thank present you
4. **Use Macros**: sjasmplus has excellent macro support
5. **Test Often**: Run in emulator frequently, don't wait for "completion"
6. **Multiple Emulators**: Test in both ZEsarUX (debugging) and Fuse (accuracy)
7. **Memory Maps**: Document your memory usage
8. **Version Snapshots**: Save .z80/.tap files with version numbers

## Example: Hello World

```asm
; Simple Hello World for ZX Spectrum
; Assemble with: sjasmplus hello.asm

    DEVICE ZXSPECTRUM48
    ORG $8000           ; Start at 32768

Start:
    LD A, 2             ; Channel 2 (main screen)
    CALL $1601          ; ROM routine CHAN_OPEN

    LD HL, Message      ; Point to our message
    CALL PrintString    ; Print it
    RET                 ; Return to BASIC

PrintString:
    LD A, (HL)          ; Get character
    OR A                ; Check if zero
    RET Z               ; Return if end of string
    RST $10             ; ROM print character
    INC HL              ; Next character
    JR PrintString      ; Loop

Message:
    DEFB "HELLO SPECTRUM!", 0

    END Start           ; End of program, entry point

; Save as TAP file
    SAVETAP "hello.tap", CODE, Start, $ - Start
```

## Debugging Tips

### Using ZEsarUX with DeZog

1. Set breakpoints by clicking left of line numbers
2. Use Watch window to monitor variables
3. View memory in real-time
4. Step through code line by line
5. Inspect registers (A, BC, DE, HL, etc.)

### Common Debugging Tasks

- **View Screen Memory**: Memory viewer at $4000
- **Check Attributes**: Memory viewer at $5800
- **Monitor Stack**: Watch SP register
- **Timing Issues**: Use ZEsarUX's T-states counter

## File Formats

- **.asm**: Assembly source code
- **.z80**: Snapshot file (contains entire memory state)
- **.tap**: Tape image file (contains program and data)
- **.sna**: Another snapshot format
- **.scr**: Screen image (6912 bytes)
- **.lst**: Listing file (assembly output with addresses)

## Converting Between Formats

Use tools like:
- **bin2tap**: Convert binary to TAP
- **z80-snapshot**: Create Z80 snapshots
- Various Python scripts available in the community

## Next Steps

1. Extract the code from your existing .z80 snapshot file
2. Set up your source code structure
3. Start refactoring and enhancing
4. Implement your 8-layer engine
5. Build that complete game!

Good luck with your ZX Spectrum development journey!
