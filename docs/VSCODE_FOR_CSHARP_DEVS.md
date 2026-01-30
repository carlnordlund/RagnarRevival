# VS Code for C# Developers

A guide for developers familiar with Visual Studio Community who are learning VS Code for ZX Spectrum assembly development.

## The Big Picture

**Visual Studio Community** and **Visual Studio Code** are completely different products that happen to share a name:

| Aspect | Visual Studio Community | Visual Studio Code |
|--------|------------------------|-------------------|
| **Type** | Full IDE | Code Editor |
| **Size** | ~7 GB | ~200 MB |
| **Startup** | 10-30 seconds | Instant |
| **Languages** | .NET-focused (C#, F#, VB.NET, C++) | Any language via extensions |
| **Project System** | Solutions (.sln), Projects (.csproj) | Folders (no project files) |
| **Built-in Compiler** | Yes (MSBuild, Roslyn) | No (uses external tools) |
| **Debugging** | Built-in for .NET | Via extensions |
| **IntelliSense** | Built-in for .NET | Via extensions |
| **Platform** | Windows (Mac version differs) | Identical on Windows/Linux/macOS |
| **Updates** | Major versions yearly | Monthly |
| **Philosophy** | Integrated Development Environment | Extensible Editor Platform |

## Quick Translation Guide

### Concepts You Know → VS Code Equivalent

| Visual Studio | VS Code | Notes |
|--------------|---------|-------|
| Solution Explorer | File Explorer (Ctrl+Shift+E) | Just shows folder structure |
| Solution (.sln) | Workspace | Can be multi-folder |
| Project (.csproj) | Folder | No project files needed |
| Build (F6) | Task (Ctrl+Shift+B) | Configured in tasks.json |
| Debug (F5) | Launch (F5) | Configured in launch.json |
| NuGet Packages | npm/pip/etc | Language-specific |
| Extensions | Extensions | Similar concept |
| Team Explorer | Source Control (Ctrl+Shift+G) | Built-in Git support |
| Output Window | Terminal (Ctrl+`) | Integrated terminal |
| Error List | Problems (Ctrl+Shift+M) | Similar |
| References | Go to Definition (F12) | Via language extensions |

## Key Differences

### 1. No Built-in Project System

**Visual Studio:**
```
File → New → Project → Choose template → VS creates structure
```

**VS Code:**
```
File → Open Folder → Create files manually
```

In VS Code, you just open a folder and start coding. No .sln or .csproj files (unless you're actually doing C# development).

### 2. External Build Tools

**Visual Studio:**
- MSBuild is built-in
- Click Build button → compiles

**VS Code:**
- You configure external tools (sjasmplus, gcc, npm, etc.)
- Tasks defined in `.vscode/tasks.json`
- Ctrl+Shift+B runs configured build task

### 3. Extension-Based Features

**Visual Studio:**
- IntelliSense for C# is built-in
- Debugger for .NET is built-in

**VS Code:**
- Everything is an extension
- Install "C#" extension for C# support
- Install "Z80 Assembly" for Z80 support
- Install "Python" for Python support

### 4. Configuration Files

**Visual Studio:** Hidden configuration in .sln/.csproj

**VS Code:** JSON configuration files

```
.vscode/
├── tasks.json       # Build tasks (like MSBuild config)
├── launch.json      # Debug configurations
└── settings.json    # Workspace settings
```

## GitHub Integration

### Visual Studio Community

- Team Explorer panel
- Basic Git operations
- Some GitHub integration
- Pull requests via extension

### VS Code

**Built-in Git (Better than VS!)**
- Source Control panel (Ctrl+Shift+G)
- Visual diff editor
- Staging area
- Commit, push, pull
- Branch management
- All visual, no command line needed

**GitHub Pull Requests Extension** (highly recommended)
- Create PRs from VS Code
- Review PRs in editor
- Comment inline
- Merge from VS Code

**GitLens Extension** (game-changer!)
- See who changed each line (blame)
- View commit history inline
- Compare commits
- File history
- Much more powerful than VS Community's Git

### Git Workflow in VS Code

```
1. Make changes
2. Ctrl+Shift+G (open Source Control)
3. Click + to stage files
4. Type commit message
5. Click ✓ to commit
6. Click ... → Push
```

Or use integrated terminal:
```
Ctrl+` (open terminal)
git add .
git commit -m "message"
git push
```

## Keyboard Shortcuts

Many are similar, but here are the important ones:

| Task | Visual Studio | VS Code |
|------|--------------|---------|
| Build | F6 / Ctrl+Shift+B | Ctrl+Shift+B |
| Run/Debug | F5 | F5 |
| Command Palette | Ctrl+Shift+P | Ctrl+Shift+P |
| Go to File | Ctrl+, (Navigate To) | Ctrl+P |
| Find in Files | Ctrl+Shift+F | Ctrl+Shift+F |
| Terminal | Ctrl+` | Ctrl+` |
| Explorer | Ctrl+Alt+L | Ctrl+Shift+E |
| Source Control | Team Explorer | Ctrl+Shift+G |
| Extensions | Tools → Extensions | Ctrl+Shift+X |
| Problems | Error List | Ctrl+Shift+M |
| Go to Definition | F12 | F12 |
| Find All References | Shift+F12 | Shift+F12 |
| Rename Symbol | F2 / Ctrl+R,R | F2 |
| Format Document | Ctrl+K, Ctrl+D | Shift+Alt+F |
| Comment/Uncomment | Ctrl+K,C / Ctrl+K,U | Ctrl+/ |
| Multi-cursor | Alt+Click | Alt+Click |
| Select Next Occurrence | (Extension) | Ctrl+D |

## Project Setup Comparison

### C# Project in Visual Studio

```
1. File → New → Project
2. Choose "Console App (.NET 6.0)"
3. Name: MyApp
4. VS creates:
   MyApp/
   ├── MyApp.sln
   ├── MyApp/
   │   ├── MyApp.csproj
   │   ├── Program.cs
   │   └── Properties/
   └── ...

5. Press F5 to build and run
```

### Z80 Assembly in VS Code

```
1. File → Open Folder
2. Select RagnarRevival folder
3. Create files manually:
   RagnarRevival/
   ├── src/
   │   └── main.asm
   ├── build/
   ├── .vscode/
   │   ├── tasks.json      (configure build)
   │   └── launch.json     (configure debug)
   └── tools/
       └── build.sh

4. Ctrl+Shift+B to build (runs sjasmplus)
5. F5 to debug (launches ZEsarUX)
```

## IntelliSense / Code Completion

### Visual Studio
- Built-in for C#
- Excellent, instant
- Shows documentation
- Parameter hints

### VS Code
- Depends on extension
- **C#**: Excellent (via OmniSharp extension)
- **Z80 Assembly**: Basic (via Z80 Assembly extension)
  - Keyword completion
  - Label completion
  - Instruction reference
  - Not as smart as C# IntelliSense

## Debugging Comparison

### Visual Studio C# Debugging

```
1. Set breakpoint (click in margin)
2. Press F5
3. Built-in debugger starts
4. Step through (F10, F11)
5. Watch variables
6. Immediate window
```

### VS Code Z80 Debugging (with DeZog)

```
1. Install DeZog extension
2. Configure launch.json
3. Set breakpoint (click in margin)
4. Press F5
5. ZEsarUX emulator starts with debugger
6. Step through (F10, F11)
7. Watch memory, registers
8. View screen in real-time
```

Very similar experience!

## Multiple Projects

### Visual Studio

One solution, multiple projects:

```
MySolution.sln
├── Project1/
│   └── Project1.csproj
├── Project2/
│   └── Project2.csproj
└── Project3/
    └── Project3.csproj
```

### VS Code

**Option 1**: Open individual folders separately

```
RagnarRevival/        (open this)
SwordOfFargoal/       (or open this)
```

**Option 2**: Multi-root workspace

File → Add Folder to Workspace → Save Workspace

Creates `.code-workspace` file:

```json
{
  "folders": [
    { "path": "RagnarRevival" },
    { "path": "SwordOfFargoal" },
    { "path": "ZXSpectrumLib" }
  ],
  "settings": {
    "...": "..."
  }
}
```

## Extensions You'll Want

### Essential

1. **GitLens** - Supercharged Git
2. **Code Spell Checker** - Catch typos in comments
3. **Path Intellisense** - Autocomplete file paths
4. **Better Comments** - Colorize different comment types

### For ZX Spectrum Development

1. **Z80 Assembly** (Imanolea) - Syntax highlighting
2. **DeZog** (maziac) - Debugging
3. **Z80 Instruction Set** (maziac) - Reference

### If You Also Code C# in VS Code

1. **C#** (Microsoft) - Language support
2. **C# Dev Kit** (Microsoft) - Project system
3. **IntelliCode** - AI-assisted completions

## Settings

### Visual Studio
Tools → Options → massive tree of settings

### VS Code
File → Preferences → Settings (or Ctrl+,)

**User Settings**: Apply to all projects
**Workspace Settings**: Apply to current project only

Both stored as JSON (can edit directly).

Example `.vscode/settings.json`:

```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "files.exclude": {
    "**/*.tap": true,
    "**/*.z80": true,
    "**/build/": true
  },
  "z80-asm.preferredCase": "upper",
  "terminal.integrated.defaultProfile.windows": "Git Bash"
}
```

## Terminal Integration

### Visual Studio
- Package Manager Console (PowerShell)
- Developer Command Prompt
- Separate windows

### VS Code
- Integrated terminal (Ctrl+`)
- Multiple terminals
- Split terminals
- Choose shell (bash, PowerShell, cmd, zsh)
- Right there in the editor!

This is **huge** for ZX Spectrum development:

```
Terminal 1: Build output
Terminal 2: Git commands
Terminal 3: Run emulator
```

All without leaving VS Code!

## Using Both Together

**You can (and should) use both!**

### Use Visual Studio Community for:
- C# projects
- .NET development
- ASP.NET websites
- Complex C++ projects
- Visual designers (WinForms, WPF)

### Use VS Code for:
- ZX Spectrum assembly
- Python scripts
- JavaScript/TypeScript
- Web development (HTML/CSS)
- Configuration files (JSON, YAML)
- Quick edits
- Cross-platform work

They coexist perfectly. Many professional developers use both daily.

## Example: Mixed Workflow

You could:

1. **Write a C# tool** in Visual Studio Community
   - Converts level data format
   - Generates lookup tables
   - Processes sprites

2. **Use the C# tool** from VS Code terminal
   - `dotnet run MyTool.dll input.dat output.asm`

3. **Edit the Z80 assembly** in VS Code
   - Include generated data
   - Build with sjasmplus

4. **Debug** in VS Code with DeZog

This is actually a great workflow!

## Learning Curve

If you're comfortable with Visual Studio Community:

- **Day 1**: VS Code feels weird, too simple
- **Day 3**: You appreciate the speed
- **Week 1**: You understand the extension model
- **Week 2**: You're productive
- **Month 1**: You prefer it for many tasks

The concepts transfer well because you already understand:
- Debugging
- Source control
- Project organization
- Build systems

You're just learning a different tool for the same concepts.

## Quick Start Checklist

- [ ] Download and install VS Code
- [ ] Install Git (if not already)
- [ ] Install extensions: Z80 Assembly, DeZog, GitLens
- [ ] Clone your repository
- [ ] Open folder in VS Code
- [ ] Create .vscode/tasks.json for build
- [ ] Ctrl+Shift+B to build
- [ ] Enjoy!

## When You Get Stuck

**Command Palette is your friend**: `Ctrl+Shift+P`

Type what you want to do:
- "git push"
- "format document"
- "change language mode"
- "install extensions"
- etc.

It's like the Quick Launch in Visual Studio but more powerful.

## Final Thoughts

VS Code is **not** a replacement for Visual Studio Community for C# development. They serve different purposes:

- **VS Community**: Professional IDE for .NET ecosystem
- **VS Code**: Universal code editor for everything else

For ZX Spectrum assembly, VS Code is perfect because:
- Fast and lightweight
- Great Git integration
- Excellent terminal
- Cross-platform
- Free and open-source
- Active extension ecosystem

You'll pick it up quickly with your Visual Studio experience. The concepts are the same, just a different (and often faster) way of working!

Welcome to VS Code! 🚀
