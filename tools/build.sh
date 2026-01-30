#!/bin/bash
# Build script for Ragnar Revival
# Usage: ./tools/build.sh [source_file.asm]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}  Ragnar Revival Build Script${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Check if sjasmplus is installed
if ! command -v sjasmplus &> /dev/null; then
    echo -e "${RED}Error: sjasmplus not found!${NC}"
    echo "Please install sjasmplus:"
    echo "  - Ubuntu/Debian: sudo apt-get install sjasmplus"
    echo "  - macOS: brew install sjasmplus"
    echo "  - Or download from: https://github.com/z00m128/sjasmplus"
    exit 1
fi

# Create build directory if it doesn't exist
mkdir -p build

# If a specific file is provided, build it
if [ $# -eq 1 ]; then
    SOURCE_FILE="$1"
    if [ ! -f "$SOURCE_FILE" ]; then
        echo -e "${RED}Error: File not found: $SOURCE_FILE${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Building: $SOURCE_FILE${NC}"
    sjasmplus "$SOURCE_FILE" --lst

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Build successful!${NC}"

        # List generated files
        if [ -d "build" ]; then
            echo -e "\n${GREEN}Generated files:${NC}"
            ls -lh build/
        fi
    else
        echo -e "${RED}Build failed!${NC}"
        exit 1
    fi
else
    # Build all .asm files in src/
    if [ ! -d "src" ]; then
        echo -e "${RED}Error: src/ directory not found${NC}"
        exit 1
    fi

    ASM_FILES=$(find src -name "*.asm" 2>/dev/null)

    if [ -z "$ASM_FILES" ]; then
        echo -e "${YELLOW}No .asm files found in src/${NC}"
        exit 0
    fi

    FAILED=0
    SUCCEEDED=0

    for file in $ASM_FILES; do
        echo -e "${YELLOW}Building: $file${NC}"
        if sjasmplus "$file" --lst 2>&1; then
            ((SUCCEEDED++))
            echo -e "${GREEN}✓ Success${NC}\n"
        else
            ((FAILED++))
            echo -e "${RED}✗ Failed${NC}\n"
        fi
    done

    echo -e "${GREEN}==================================${NC}"
    echo -e "Build complete:"
    echo -e "  ${GREEN}Succeeded: $SUCCEEDED${NC}"
    if [ $FAILED -gt 0 ]; then
        echo -e "  ${RED}Failed: $FAILED${NC}"
    fi
    echo -e "${GREEN}==================================${NC}"

    # List generated files
    if [ -d "build" ]; then
        echo -e "\n${GREEN}Generated files in build/:${NC}"
        ls -lh build/
    fi

    exit $FAILED
fi
