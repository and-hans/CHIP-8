# used Cowgod's Chip-8 guide for reference to the ISA and general configuration
# <-- Instruction Variables -->
"""
NNN = 12-bit value, lower 12-bits of the 16-bit instruction
N = 4-bit value, lower 4-bits of the 16-bit instruction
X = 4-bit value, lower 4-bits of first 8-bits of an instruction (high byte)
Y = 4-bit value, upper 4-bits of the last 8-bits of an instruction (low byte)
KK = 8-bit value, lowest 8-bits of the 16-bit instruction
"""
# <-- End of Instruction Variables -->

class Chip8:
    def __init__(self):
        self.memory = bytearray(4096)  # memory/RAM
        self.pc = 0x200  # program counter  (starts at 512 or 0x200)
        # registers
        self.index = 0  # I/index register
        self.sp = 0x52  # stack pointer register (starts at 82 or 0x52)
        self.timers = {  # delay and sound timers
            'delay' : 0,
            'sound' : 0
        }
        self.register = {}  # stores 16 general purpose registers
        for i in range(16):
            self.register['v'+str(hex(i))[2:]] = 0
        # others
        self.current_opcode = '0000'  # current operation
        fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i in range(len(fonts)):  # load the font set into memory
            self.memory[i] = fonts[i]

    # <--- Execute --->
    def decode_execute(self, opcode: str):
        # since Python doesn't have in case statements, I'll have to use if's
        if opcode[0] == '0':  # [0NNN] -> execute machine language routine
            pass
        elif opcode == '00E0':  # clears the display
            self.clear_display()
        elif opcode[0] == '1':  # [1NNN] -> jump routine
            pass
        elif opcode[0] == '2':  # [2NNN] -> call subroutines
            pass
        elif opcode[0] == '3':  # [3XNN] -> conditional: skip instruction if VX == NN
            pass
        elif opcode[0] == '4':  # [4XNN] -> conditional: skip instruction if VX != NN
            pass
        elif opcode[0] == '5':  # [5XY0] -> conditional: skip instruction if VX == VY
            pass
        elif opcode[0] == '6':  # [6XNN] -> set: set VX to NN
            pass
        elif opcode[0] == '7':  # [7XNN] -> arthimetic: adds NN to VX (carry flag does not change)
            pass
        elif opcode[0] == '8':  # [8XY-] -> arthimetic: logical operations 
            pass
        elif opcode[0] == '9':  # [9XY0] -> conditional: skips the next instruction if VX != VY
            pass
        elif opcode[0] == 'A':  # [ANNN] -> set: sets index to address NNN
            pass
        elif opcode[0] == 'B':  # [BNNN] -> jump: jumps (+ offset) to address NNN+V0 
            pass
        elif opcode[0] == 'C':  # [CXNN] -> ANDs NN with a random number and puts it in reg VX
            pass
        elif opcode[0] == 'D':  # [DXYN] -> draw to screen (VX, VY, N)
            pass
        elif opcode[0] == 'E':  # [EX--] -> keyboard conditional
            pass
        elif opcode[0] == 'F':  # [FX--] -> handles memory, bcd, timers, and keyboard
            pass
        # increment the program counter by 2 after each operation
        self.pc += 2  

    # <--- Fetch --->
    def fetch_instr(self, operation: str=None):
        if operation:
            self.opcode = operation  # used for debugging
        else:
            high = self.memory[self.pc]  # high bit
            low = self.memory[self.pc + 1]  # low bit
            self.current_opcode = high + low  # 16 bit instruction
            self.decode_execute(self.current_opcode)
    # <--- Display Functions --->
    def clear_display(self):
        pass

    def draw(self):
        pass
