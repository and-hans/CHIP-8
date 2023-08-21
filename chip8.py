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
import pygame
import numpy as np
import random
import sys
from collections import deque

pygame.init()

class Chip8:
    def __init__(self, scale, filename):
        self.filename = filename
        self.memory = bytearray(4096)  # memory/RAM
        self.pc = 0x200  # program counter  (starts at 512 or 0x200)
        # registers
        self.index = 0  # I/index register
        self.sp = 0  # stack pointer register, but for now it's just for show
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
        # font
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
        # keyboard input settings
        self.keyboard = {  # key mappings changed from orginal to make things easier on modern keyboards
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
        }
        self.keys = [0 for i in range(16)]  # 16 possible keys, with K_x being the first
        # screen and pygame settings
        self.grid = np.zeros([32, 64])  # screen pixel grid
        self.HEIGHT = 64 * scale
        self.WIDTH = 32 * scale
        # basic pygame setup
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
        pygame.display.set_caption(f"Chip-8 Emulator - {self.filname[:-4]}")
        self.screen.fill([0, 0, 0])
        pygame.display.flip()

    # <--- Execute --->
    def decode_execute(self, opcode: str):
        # since Python doesn't have in case statements, I'll have to use if's
        if opcode[0] == '0':  # [0NNN] -> execute machine language routine
            if opcode[1] != '0':
                print("Instruction 0NNN has not be inmplemented")
            else:
                if opcode == '00E0':
                    self.grid = np.zeros([32, 64])
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
                '''
                Probably did this wrong
                '''
                temp = self.register['v'+opcode[1]] + self.register['v'+opcode[2]]
                if temp > 254:  # if value is greater than 8-bits, set carry flag
                    self.register['vf'] = 1
                    self.register['v'+opcode[1]] = (temp << 8) & 0xFF  # only the lower 8-bits should be stored
                else: 
                    self.register['vf'] = 0
                    self.register['v'+opcode[1]] = temp
            elif opcode[3] == '5':  # set VX = VX-VY, carry flag used
                '''
                Probably did this wrong too
                '''
                if self.register['v'+opcode[2]] > self.register['v'+opcode[1]]:  # if VY>VX
                    self.register['vf'] = 1
                else:
                    self.register['vf'] = 0
                self.register['v'+opcode[1]] =- self.register['v'+opcode[2]]
            elif opcode[3] == '6':  # Set Vx = Vx SHR 1
                # if the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0
                self.register['vf'] = self.register['v'+opcode[1]] & 0x1
                self.register['v'+opcode[1]] >>= 1  # shift right
            elif opcode[3] == '7':  # set VX = VY-VX, carry flag used
                if self.register['v'+opcode[2]] > self.register['v'+opcode[1]]:  # if VY>VX
                    self.register['vf'] = 1
                else:
                    self.register['vf'] = 0
                self.register['v'+opcode[1]] = self.register['v'+opcode[2]] - self.register['v'+opcode[1]]
            elif opcode[3] == 'E':  # Set Vx = Vx SHL 1
                # if the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0
                self.register['vf'] = (self.register['v'+opcode[1]] & 0x80) >> 7   # either 7 or 8
                self.register['v'+opcode[1]] <<= 1  # left shift
        elif opcode[0] == '9':  # [9XY0] -> conditional: skips the next instruction if VX != VY
            if self.register['v'+opcode[1]] != self.register['v'+opcode[2]]:
                self.pc += 2
        elif opcode[0] == 'A':  # [ANNN] -> set: sets index to address NNN
            self.index = int(opcode[1:], 16)
        elif opcode[0] == 'B':  # [BNNN] -> jump: jumps (+ offset) to address NNN+V0 
            self.index = int(opcode[1:], 16) +  self.register['v0']
        elif opcode[0] == 'C':  # [CXNN] -> ANDs NN with a random number and puts it in reg VX
            randnum = random.randint(0, 255)  # generate a random number between 0 and 255
            # AND the random number with NN, and then store it in register VX
            self.register['v'+opcode[1]] = int(opcode[2:], 16) & randnum
        elif opcode[0] == 'D':  # [DXYN] -> draw to screen (VX, VY, N)
            vx = self.register['v'+opcode[1]]
            vy = self.register['v'+opcode[2]]
            sprite = self.memory[self.index: self.index+int(opcode[3])]  # grab the sprite from memory
            if self.draw(sprite, vx, vy):  # raise flag if a collision occured/pixel was erased 
                self.register['vf'] = 1
            else:
                self.register['vf'] = 0
        elif opcode[0] == 'E':  # [EX--] -> keyboard conditional
            if opcode[2:] == '9E':  # skip next instruction if key with the value of Vx is pressed
                vx_key = self.register['v'+opcode[1]]
                # if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2
                if self.keys[vx_key]:
                    self.pc += 2
            elif opcode[2:] == 'A1':  # skip next instruction if key with the value of Vx is not pressed
                vx_key = self.register['v'+opcode[1]]
                # if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2
                if not self.keys[vx_key]:
                    self.pc += 2
        elif opcode[0] == 'F':  # [FX--] -> handles memory, bcd, timers, and keyboard
            if opcode[2:] == '07':  # set VX = DT value
                self.register['v'+opcode[1]] = self.timers['dt']
            elif opcode[2:] == '0A':  # wait for a key press, and then store the value of the key in Vx
                key_pressed = False
                while not key_pressed:
                    event = pygame.event.wait()  # wait for an event 
                    self.keyboard(event_overide=event)  # check keyboard with event
                    for i in range(len(self.keys)):  # loop through all the keys
                        if self.keys[i]:  # if the key was pressed, then store it in memory VX
                            self.register['v'+opcode[1]] = i  
                            key_pressed = True
            elif opcode[2:] == '15':  # set DT = VX
                self.timers['dt'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '18':  # set ST = VX
                self.timers['st'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '1E':  # set I = I + VX
                self.index += self.register['v'+opcode[1]]
            elif opcode[2:] == '29':  # set I = location of sprite for digit Vx
                self.index = self.register['v'+opcode[1]]*5  # sprites are 5 bytes long (8x5 pixels)
            elif opcode[2:] == '33':  # store BCD representation of Vx in memory locations I, I+1, and I+2
                '''
                hundreds -> index
                tens -> index+1
                ones -> index+2
                '''
                bcd = self.register['v'+opcode[1]]
                # load BCD values into memory address pointed at the address loaded into the index register
                self.memory[self.index] = bcd[0]
                self.memory[self.index + 1] = bcd[1]
                self.memory[self.index + 2] = bcd[2]
            elif opcode[2:] == '55':  # store registers V0 through Vx in memory starting at location I
                for i in range(int(opcode[1])+1):
                    self.memory[self.index + i] = self.register[f'v{i}']
            elif opcode[2:] == '65':  # read registers V0 through Vx from memory starting at location I
                for i in range(int(opcode[1])+1):
                    self.register[f'v{i}'] = self.memory[self.index + i]
        # increment the program counter by 2 after each operation
        self.pc += 2  
        # check for key input
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         sys.exit(0)
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key in self.keyboard:  # check if the key is valid
        #             for key, value in self.keyboard.items():
        #                 if key == event.key:
        #                     self.keys[value] = 1  # set the specific key to true
        #         elif event.key == pygame.K_ESCAPE:  # quit program if the escape was pressed
        #             pygame.quit()
        #             sys.exit(0)
        #     elif event.type == pygame.KEYUP:
        #        if event.key in self.keyboard:  # check if the key is valid
        #             for key, value in self.keyboard.items():
        #                 if key == event.key:
        #                     self.keys[value] = 0  # set the specific key to false
    # <--- Fetch --->
    def fetch_instr(self, operation: str=None):
        if operation:
            self.opcode = operation  # used for debugging
        else:
            high = self.memory[self.pc]  # high bit
            low = self.memory[self.pc + 1]  # low bit
            self.current_opcode = high + low  # 16 bit instruction
            self.decode_execute(self.current_opcode)
    # <--- Display Functionality --->
    def draw(self, sprite : list, vx : int, vy : int):
        collided = False
        for i in range(len(sprite)):
            for j in range(8):
                # if a pixel in the sprite was erased, set the collision to True
                if self.grid[vy + i][vx + j] == 1 and int(sprite[i][j]) == 1:
                    collided = True
                # CHIP-8 XOR's the bits of the sprite onto the screen
                self.grid[vy + i][vx + j] = self.grid[vy + i][vx + j] ^ int(sprite[i][j])
        return collided
    # <--- Keyboard Functionality --->
    def keyboard(self, event_overide: pygame.event.Event=None):
        for event in pygame.event.get():
            if event_overide:  # set the loop event to the custom event (this may serve useful for later on)
                event=event_overide
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in self.keyboard:  # check if the key is valid
                    for key, value in self.keyboard.items():
                        if key == event.key:
                            self.keys[value] = 1  # set the specific key to true
                elif event.key == pygame.K_ESCAPE:  # quit program if the escape was pressed
                    pygame.quit()
                    sys.exit(0)
            elif event.type == pygame.KEYUP:
               if event.key in self.keyboard:  # check if the key is valid
                    for key, value in self.keyboard.items():
                        if key == event.key:
                            self.keys[value] = 0  # set the specific key to false
