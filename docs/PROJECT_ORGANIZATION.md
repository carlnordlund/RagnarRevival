# ZX Spectrum Projects Organization Guide

## Repository Structure Options

You have multiple game ideas and prototypes. Here's how to organize them.

### Option 1: Monorepo (All Projects in One Repository)

```
ZXSpectrum-Games/
├── ragnar-revival/
│   ├── src/
│   ├── assets/
│   ├── docs/
│   └── build/
├── sword-of-fargoal/
│   ├── src/
│   ├── assets/
│   ├── docs/
│   └── build/
├── prototype-3/
│   └── ...
├── shared/
│   ├── lib/           # Reusable Z80 routines
│   │   ├── keyboard.asm
│   │   ├── sprites.asm
│   │   ├── screen.asm
│   │   └── math.asm
│   └── tools/         # Build scripts, converters
│       ├── png2asm.py
│       └── build-all.sh
├── README.md
└── .gitignore
```

**Pros:**
- All your ZX Spectrum work in one place
- Easy to share code between projects
- Single setup for tools and build scripts
- See cross-project history
- Good for related projects

**Cons:**
- Repository grows large over time
- Mixed commit history
- Harder to share individual games
- Cloning gets one massive repo
- Can't set different visibility per project

**Best for:**
- Personal development
- Closely related projects
- Sharing common code
- When you want unified view

### Option 2: Separate Repositories (Recommended)

```
Repository: RagnarRevival
├── src/
├── assets/
├── docs/
└── build/

Repository: SwordOfFargoal
├── src/
├── assets/
├── docs/
└── build/

Repository: ZXSpectrumLib
├── lib/
│   ├── keyboard.asm
│   ├── sprites.asm
│   └── ...
├── docs/
└── examples/

Repository: ZXSpectrum-Tools
├── png2asm.py
├── map-generator.py
└── ...
```

**Pros:**
- Clear identity per project
- Easy to showcase individual games
- Clean commit history per game
- Can share individual projects easily
- Different collaborators per project
- Can make some private, some public

**Cons:**
- More repositories to manage
- Duplicate setup in each
- Sharing code requires extra work
- More complex build if projects depend on each other

**Best for:**
- Multiple distinct games
- Public showcasing
- Professional portfolio
- When projects are independent

### Option 3: Hybrid (Recommended for You)

Based on your situation, I recommend:

**Separate game repositories:**
- `RagnarRevival` - Your 3D isometric demo/game
- `SwordOfFargoal` - Roguelike dungeon crawler
- `[Future games...]` - Each new project

**Shared code repository:**
- `ZXSpectrum-Library` - Reusable Z80 routines

**Shared tools repository:**
- `ZXSpectrum-DevTools` - Development tools

**How to share code:**

Use Git submodules:

```bash
# In RagnarRevival repository
git submodule add https://github.com/yourusername/ZXSpectrum-Library lib/shared

# In SwordOfFargoal repository
git submodule add https://github.com/yourusername/ZXSpectrum-Library lib/shared
```

Now both projects can use the same library code.

### Option 4: Topic-Based Organization

```
Repositories:
- ZXSpectrum-3D-Engine     (isometric rendering)
- ZXSpectrum-Procgen       (procedural generation)
- RagnarRevival-Game       (uses 3D engine)
- SwordOfFargoal-Game      (uses procgen)
```

**Best for:** Research/educational projects, reusable engines

## Recommended Structure for You

Given that you have:
- Ragnar Revival (3D isometric)
- Sword of Fargoal (roguelike)
- More game ideas
- Interest in sharing/showcasing

**I recommend: Separate repositories**

```
Your GitHub:
├── RagnarRevival           (already exists!)
├── SwordOfFargoal          (create new)
├── ZXSpectrum-Library      (create when you have reusable code)
└── [Future projects...]
```

## Creating a New Game Repository

When starting a new game project:

### Step 1: Create from Template

You can turn RagnarRevival into a template:

1. Go to repository Settings on GitHub
2. Check "Template repository"
3. When creating new repo, choose "Use this template"

### Step 2: Or Copy Structure

```bash
# Create new repository on GitHub first, then:

git clone https://github.com/yourusername/SwordOfFargoal
cd SwordOfFargoal

# Copy structure from RagnarRevival
mkdir -p src assets docs tools build .vscode
cp ../RagnarRevival/.vscode/*.json .vscode/
cp ../RagnarRevival/tools/*.py tools/
cp ../RagnarRevival/tools/*.sh tools/
cp ../RagnarRevival/.gitignore .

# Create README
cat > README.md << 'EOF'
# Sword of Fargoal

ZX Spectrum version of the classic roguelike dungeon crawler.

## Features
- 3D isometric graphics
- Procedurally generated infinite dungeons
- Classic Fargoal gameplay

[...]
EOF

git add .
git commit -m "Initial project structure"
git push
```

## Shared Code Strategy

### Creating a Shared Library

When you find yourself copying code between projects:

```bash
# Create ZXSpectrum-Library repository
mkdir ZXSpectrum-Library
cd ZXSpectrum-Library

# Organize by function
mkdir -p lib/{graphics,input,sound,math,utils}

# Example: lib/graphics/sprite.asm
# Example: lib/input/keyboard.asm
# Example: lib/math/multiply.asm
```

### Using Shared Code

**Method 1: Git Submodules**

```bash
# In your game project
git submodule add https://github.com/you/ZXSpectrum-Library lib/shared
```

In your main.asm:
```asm
    INCLUDE "lib/shared/lib/graphics/sprite.asm"
    INCLUDE "lib/shared/lib/input/keyboard.asm"
```

**Method 2: Copy and Customize**

Sometimes it's better to copy code and modify for specific project:

```bash
# Copy library routines to project
cp ~/ZXSpectrum-Library/lib/graphics/sprite.asm src/lib/sprite.asm

# Customize for this game
# No dependency on external repo
```

**Method 3: Package Management (Advanced)**

Create a simple package system:

```bash
# tools/update-libs.sh
#!/bin/bash
curl https://raw.githubusercontent.com/you/ZXSpectrum-Library/main/lib/graphics/sprite.asm \
  -o src/lib/sprite.asm
```

## Documentation Strategy

### Per-Project Documentation

Each game repository:

```
RagnarRevival/
├── README.md              # Project overview, building, running
├── DESIGN.md             # Game design document
├── TECHNICAL.md          # Technical architecture
└── docs/
    ├── CONTROLS.md       # How to play
    ├── BUILDING.md       # Build instructions
    └── DEVELOPMENT.md    # Development guide
```

### Shared Documentation

ZXSpectrum-Library:

```
ZXSpectrum-Library/
├── README.md             # Library overview
├── docs/
│   ├── API.md           # API reference
│   ├── EXAMPLES.md      # Usage examples
│   └── INTEGRATION.md   # How to integrate
└── examples/
    └── sprite-demo/
```

## Build System

### Per-Project Build

Each game has its own build scripts:

```
RagnarRevival/tools/build.sh
SwordOfFargoal/tools/build.sh
```

But they can share common tools:

```
RagnarRevival/tools/png2asm.py      (symlink or copy)
SwordOfFargoal/tools/png2asm.py     (symlink or copy)
```

### Centralized Tools

Or keep tools separate:

```
ZXSpectrum-DevTools/
├── png2asm.py
├── map-editor.py
└── music-converter.py
```

Use via PATH or direct reference:

```bash
# In project build script
python3 ../ZXSpectrum-DevTools/png2asm.py ...
```

## GitHub Organization (Optional)

For many projects, consider a GitHub Organization:

```
GitHub Organization: YourName-ZXSpectrum
├── RagnarRevival
├── SwordOfFargoal
├── Library
└── Tools
```

**Pros:**
- Professional presentation
- Separate from personal repos
- Can add collaborators
- Good for open source

**Cons:**
- Extra complexity
- Overkill for personal projects

## Release Strategy

### Per-Game Releases

Each game repository:
- Use GitHub Releases
- Attach .tap/.z80 files
- Version tags (v1.0, v1.1, etc.)
- Release notes

```bash
# Tag a release
git tag -a v1.0 -m "First playable version"
git push origin v1.0

# Create release on GitHub with .tap file attached
```

### Collection Releases

Could also create a "collection" repository:

```
ZXSpectrum-Collection/
└── releases/
    ├── ragnar-revival-v1.0.tap
    ├── sword-of-fargoal-v1.0.tap
    └── all-games.zip
```

## Migration from Monorepo to Separate Repos

If you start with monorepo and want to split later:

```bash
# Extract RagnarRevival to its own repo with history
git filter-branch --subdirectory-filter ragnar-revival -- --all

# Now ragnar-revival folder becomes the root
# Push to new repository

# Repeat for each project
```

(GitHub has tools to make this easier)

## Recommended: Start Simple, Grow Organically

### Phase 1: Two Separate Repos (Now)

```
RagnarRevival/    (already exists)
SwordOfFargoal/   (create new)
```

### Phase 2: Extract Common Code (Later)

When you notice code duplication:

```
RagnarRevival/
SwordOfFargoal/
ZXSpectrum-Library/    (create when needed)
```

### Phase 3: Tools Repository (If Needed)

When tools become complex:

```
RagnarRevival/
SwordOfFargoal/
ZXSpectrum-Library/
ZXSpectrum-DevTools/
```

## Example: Setting Up Sword of Fargoal Repository

```bash
# 1. Create repository on GitHub
# (use web interface: New Repository → SwordOfFargoal)

# 2. Clone locally
git clone https://github.com/yourusername/SwordOfFargoal
cd SwordOfFargoal

# 3. Copy structure from RagnarRevival
mkdir -p src assets/graphics docs tools build .vscode
cp ../RagnarRevival/.vscode/*.json .vscode/
cp ../RagnarRevival/tools/*.py tools/
cp ../RagnarRevival/tools/*.sh tools/
cp ../RagnarRevival/tools/*.bat tools/
cp ../RagnarRevival/.gitignore .
cp ../RagnarRevival/DEVELOPMENT.md docs/
cp ../RagnarRevival/GETTING_STARTED.md docs/

# 4. Create project-specific README
cat > README.md << 'EOF'
# Sword of Fargoal - ZX Spectrum Edition

A 3D isometric roguelike dungeon crawler for the ZX Spectrum, inspired by
the classic Commodore 64 game.

## Features

- **Procedurally generated** infinite dungeons
- **3D isometric graphics** with smooth scrolling
- **Classic roguelike** gameplay with permadeath
- **Multiple levels** with increasing difficulty
- **Items, combat, and exploration**

## Building

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

## Playing

[Instructions once game is playable...]

## History

Based on my original 1980s ZX Spectrum BASIC version.
Now reimplemented in Z80 assembly with enhanced graphics and gameplay.

## License

[Your choice]
EOF

# 5. Create game-specific design doc
cat > DESIGN.md << 'EOF'
# Sword of Fargoal Design Document

## Concept

[Your design ideas...]

## Technical Architecture

[Your technical approach...]
EOF

# 6. Initial commit
git add .
git commit -m "Initial project structure for Sword of Fargoal

Set up development environment with:
- Build scripts
- VS Code configuration
- Graphics conversion tools
- Documentation templates"

git push
```

## Summary

**For your situation, I recommend:**

1. ✅ **Separate repository for each game**
   - RagnarRevival (exists)
   - SwordOfFargoal (create new)
   - Future projects (create as needed)

2. ✅ **Shared library when needed**
   - Create ZXSpectrum-Library when you have reusable code
   - Use git submodules to include in projects

3. ✅ **Keep tools in each project** (for now)
   - Copy png2asm.py and build scripts to each project
   - Extract to separate repo later if they grow complex

4. ✅ **Use RagnarRevival as template**
   - Copy structure to new projects
   - Consistent organization
   - Easier to switch between projects

This approach:
- Keeps each game focused and showcaseable
- Allows code sharing when needed
- Scales as you add more projects
- Works well with GitHub
- Professional presentation

Start with separate repos for Ragnar and Fargoal, then add shared library if/when needed. Don't over-engineer at the start! 🎮
