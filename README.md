# CHIP-8

An easy to read CHIP-8 emulator. 

## Overview
This project explores fundamental emulation architectures by implementing a CHIP-8 virtual machine. The emulator accurately parses and executes standard CHIP-8 ROMs, providing instruction handling, display rendering, and input processing to faithfully recreate the classic system's fetch-decode-execute cycle.

## Features
* Full support for the standard CHIP-8 instruction set
* Accurate fetch-decode-execute timing and cycle handling
* Dynamic ROM loading and execution
* Keypad input mapping

## How to Run a ROM
1. Open chip8.py and scroll to the last three lines.
2. Locate the Chip8 object instantiation (`cpu = Chip8(10, 'programs/Pong.ch8')`).
3. Change the second argument to the file path of your desired .ch8 program.
4. Run the Python script to see the emulator in action.
