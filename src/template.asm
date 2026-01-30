; ============================================================================
; Ragnar Revival - Template Source File
; ============================================================================
; ZX Spectrum 48K
; Z80 Assembly Language
; ============================================================================

    DEVICE ZXSPECTRUM48     ; Target Spectrum 48K
    ORG $8000               ; Start at 32768 (safe user area)

; ============================================================================
; Constants
; ============================================================================

; Screen memory addresses
SCREEN_MEM      EQU $4000   ; Screen pixel data (6144 bytes)
ATTR_MEM        EQU $5800   ; Attribute data (768 bytes)

; Colors (INK color + PAPER color * 8 + BRIGHT * 64)
BLACK           EQU 0
BLUE            EQU 1
RED             EQU 2
MAGENTA         EQU 3
GREEN           EQU 4
CYAN            EQU 5
YELLOW          EQU 6
WHITE           EQU 7

; ROM routines
ROM_CLS         EQU $0DAF   ; Clear screen
ROM_CHAN_OPEN   EQU $1601   ; Open channel
ROM_PRINT_CHAR  EQU $10     ; Print character (RST $10)

; ============================================================================
; Main Program Entry Point
; ============================================================================

Start:
    CALL Initialize
    CALL MainLoop
    RET                     ; Return to BASIC

; ============================================================================
; Initialize
; ============================================================================

Initialize:
    ; Set up screen
    LD A, 2                 ; Channel 2 (main screen)
    CALL ROM_CHAN_OPEN
    CALL ROM_CLS

    ; Set border color
    LD A, BLACK
    OUT ($FE), A

    ; Clear attributes to white on black
    LD HL, ATTR_MEM
    LD DE, ATTR_MEM + 1
    LD BC, 767
    LD (HL), WHITE          ; White ink on black paper
    LDIR

    RET

; ============================================================================
; Main Game Loop
; ============================================================================

MainLoop:
    CALL CheckKeyboard
    CALL UpdateGame
    CALL RenderScreen

    ; Add a small delay
    HALT                    ; Wait for frame (50Hz PAL / 60Hz NTSC)

    ; Check for exit condition
    LD A, (ExitFlag)
    OR A
    JR Z, MainLoop

    RET

; ============================================================================
; Check Keyboard Input
; ============================================================================

CheckKeyboard:
    ; Read keyboard half-row (example: reads CAPS to V)
    LD BC, $FEFE            ; Half-row: SHIFT, Z, X, C, V
    IN A, (C)

    ; Check if key pressed (bit will be 0 if pressed)
    BIT 0, A                ; Check SHIFT
    JR Z, .ShiftPressed

    ; Add more key checks here

    RET

.ShiftPressed:
    ; Handle shift key
    RET

; ============================================================================
; Update Game Logic
; ============================================================================

UpdateGame:
    ; Update game state here
    RET

; ============================================================================
; Render Screen
; ============================================================================

RenderScreen:
    ; Render graphics here
    RET

; ============================================================================
; Data Section
; ============================================================================

ExitFlag:
    DEFB 0                  ; 0 = continue, 1 = exit

; ============================================================================
; Helper Routines
; ============================================================================

; Print a null-terminated string
; Input: HL = pointer to string
PrintString:
    LD A, (HL)
    OR A                    ; Check for null terminator
    RET Z
    RST ROM_PRINT_CHAR      ; Print character
    INC HL
    JR PrintString

; ============================================================================
; Program End
; ============================================================================

ProgramEnd:

    ; Calculate program size
    DISPLAY "Program size: ", $ - Start, " bytes"
    DISPLAY "Free memory: ", 65536 - $, " bytes"

    ; Save as TAP file
    SAVETAP "build/ragnar.tap", CODE, Start, $ - Start

; ============================================================================
; End of File
; ============================================================================
