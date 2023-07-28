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
from collections import deque


class Chip8:
    def __init__(self):
        self.memory = bytearray(4096)  # memory/RAM
        self.pc = 0x200  # program counter  (starts at 512 or 0x200)
        # registers
        self.index = 0  # I/index register
        self.sp = 0x52  # stack pointer register (starts at 82 or 0x52), but for now it's just for show
        self.timers = {  # delay (DT) and sound timers (ST)
            'dt' : 0,
            'st' : 0
        }
        self.register = {}  # stores 16 general purpose registers
        for i in range(16):
            self.register['v'+str(hex(i))[2:]] = 0
        # stack
        self.stack = deque()
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
            if opcode[1] != '0':
                print("Instruction 0NNN has not be inmplemented")
            else:
                if opcode == '00E0':
                    self.clear_display()
                elif opcode == '00EE':
                    self.pc = self.stack.popleft()
        elif opcode[0] == '1':  # [1NNN] -> jump routine
            self.pc = int(opcode[1:], 16) - 2
        elif opcode[0] == '2':  # [2NNN] -> call subroutines
            self.sp += 1
            self.stack.appendleft(self.pc)
            self.pc = int(opcode[1:], 16) - 2
        elif opcode[0] == '3':  # [3XNN] -> conditional: skip instruction if VX == NN
            if self.register['v'+opcode[1]] == int(opcode[2:], 16):
                self.pc += 2
        elif opcode[0] == '4':  # [4XNN] -> conditional: skip instruction if VX != NN
            if self.register['v'+opcode[1]] != int(opcode[2:], 16):
                self.pc += 2
        elif opcode[0] == '5':  # [5XY0] -> conditional: skip instruction if VX == VY
            if self.register['v'+opcode[1]] == self.register['v'+opcode[2]]:
                self.pc += 2
        elif opcode[0] == '6':  # [6XNN] -> set: set VX to NN
            self.register['v'+opcode[1]] = int(opcode[2:], 16)
        elif opcode[0] == '7':  # [7XNN] -> arthimetic: adds NN to VX, and stores the value in VX (carry flag does not change)
            self.register['v'+opcode[1]] += int(opcode[2:], 16)
        elif opcode[0] == '8':  # [8XY-] -> arthimetic: logical operations 
            if opcode[3] == '0':  # set VX = VY
               self.register['v'+opcode[1]] = self.register['v'+opcode[2]] 
            elif opcode[3] == '1':  # set VX = (VX OR VY)
                self.register['v'+opcode[1]] = self.register['v'+opcode[1]] | self.register['v'+opcode[2]]
            elif opcode[3] == '2':  # set VX = (VX AND VY)
                self.register['v'+opcode[1]] = self.register['v'+opcode[1]] & self.register['v'+opcode[2]]
            elif opcode[3] == '3':  # set VX = (VX XOR VY)
                self.register['v'+opcode[1]] = self.register['v'+opcode[1]] ^ self.register['v'+opcode[2]]
            elif opcode[3] == '4':  # set VX = VX + VY, carry flag used
                temp = self.register['v'+opcode[1]] + self.register['v'+opcode[2]]
                if temp > 254:  # if value is greater than 8-bits, set carry flag
                    self.register['vf'] = 1
                    self.register['v'+opcode[1]] = (temp << 8) & 0xFF  # only the lower 8-bits should be stored
                else: 
                    self.register['vf'] = 0
                    self.register['v'+opcode[1]] = temp
            elif opcode[3] == '5':  # set VX = VX-VY, carry flag used
                if self.register['v'+opcode[2]] > self.register['v'+opcode[1]]:  # if VY>VX
                    self.register['vf'] = 1
                else:
                    self.register['vf'] = 0
                self.register['v'+opcode[1]] =- self.register['v'+opcode[2]]
            elif opcode[3] == '6':
                pass
            elif opcode[3] == '7':  # set VX = VY-VX, carry flag used
                if self.register['v'+opcode[2]] > self.register['v'+opcode[1]]:  # if VY>VX
                    self.register['vf'] = 1
                else:
                    self.register['vf'] = 0
                self.register['v'+opcode[1]] = self.register['v'+opcode[2]] - self.register['v'+opcode[1]]
            elif opcode[3] == 'E':
                pass
        elif opcode[0] == '9':  # [9XY0] -> conditional: skips the next instruction if VX != VY
            if self.register['v'+opcode[1]] != self.register['v'+opcode[2]]:
                self.pc += 2
        elif opcode[0] == 'A':  # [ANNN] -> set: sets index to address NNN
            self.index = int(opcode[1:], 16)
        elif opcode[0] == 'B':  # [BNNN] -> jump: jumps (+ offset) to address NNN+V0 
            self.index = int(opcode[1:], 16) +  self.register['v0']
        elif opcode[0] == 'C':  # [CXNN] -> ANDs NN with a random number and puts it in reg VX
            pass
        elif opcode[0] == 'D':  # [DXYN] -> draw to screen (VX, VY, N)
            pass
        elif opcode[0] == 'E':  # [EX--] -> keyboard conditional
            if opcode[2:] == '9E':  # skip next instruction if key with the value of Vx is pressed
                pass
            elif opcode[2:] == 'A1':  # skip next instruction if key with the value of Vx is not pressed
                pass
        elif opcode[0] == 'F':  # [FX--] -> handles memory, bcd, timers, and keyboard
            if opcode[2:] == '07':  # set VX = DT value
                self.register['v'+opcode[1]] = self.timers['dt']
            elif opcode[2:] == '0A':  # wait for a key press, and then store the value of the key in Vx
                pass
            elif opcode[2:] == '15':  # set DT = VX
                self.timers['dt'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '18':  # set ST = VX
                self.timers['st'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '1E':  # set I = I + VX
                self.index += self.register['v'+opcode[1]]
            elif opcode[2:] == '29':  # set I = location of sprite for digit Vx
                pass
            elif opcode[2:] == '33':  # store BCD representation of Vx in memory locations I, I+1, and I+2
                pass
            elif opcode[2:] == '55':  # store registers V0 through Vx in memory starting at location I
                pass
            elif opcode[2:] == '65':  # read registers V0 through Vx from memory starting at location I
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
