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


class Chip8:
    def __init__(self, scale, filename):
        self.filename = filename
        self.memory = np.zeros(4096, np.uint8)#bytearray(4096)  # memory/RAM
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
        pygame.init()
        self.keyboard = {  # key mappings changed from orginal to make things easier on modern keyboards
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
        }
        self.keys = [0 for i in range(16)]  # 16 possible keys, with K_x being the first
        # screen and pygame settings
        self.scale = scale
        self.grid = np.zeros([32, 64], np.int8)  # screen pixel grid
        self.HEIGHT = 32 * scale
        self.WIDTH = 64 * scale
        # basic pygame setup
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
        pygame.display.set_caption(f"Chip-8 Emulator - {self.filename[:-4]}")
        self.screen.fill([0, 0, 0])
        pygame.display.flip()
        self.draw_flag = False
        # read program
        self.read_rom(0x200)

    # <--- Execute --->
    def decode_execute(self, opcode: str):
        # since Python doesn't have in case statements, I'll have to use if's
        if opcode[0] == '0':  # [0NNN] -> execute machine language routine
            if opcode[1] != '0':
                print("Instruction 0NNN has not be implemented")
            else:
                if opcode == '00e0':
                    self.grid = np.zeros([64, 32], np.int16)
                elif opcode == '00ee':
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
        elif opcode[0] == 'a':  # [ANNN] -> set: sets index to address NNN
            self.index = int(opcode[1:], 16)
        elif opcode[0] == 'b':  # [BNNN] -> jump: jumps (+ offset) to address NNN+V0 
            self.index = int(opcode[1:], 16) +  self.register['v0']
        elif opcode[0] == 'c':  # [CXNN] -> ANDs NN with a random number and puts it in reg VX
            randnum = random.randint(0, 255)  # generate a random number between 0 and 255
            # AND the random number with NN, and then store it in register VX
            self.register['v'+opcode[1]] = int(opcode[2:], 16) & randnum
        elif opcode[0] == 'd':  # [DXYN] -> draw to screen (VX, VY, N)
            vx = self.register['v'+opcode[1]]  # x-coordinate
            vy = self.register['v'+opcode[2]]  # y-coordinate
            self.draw(vx, vy, int(opcode[3]))  # change pixels (actual display is dealt with in the "run" method)
            if self.draw_flag:  # raise flag if a collision occured/pixel was erased (could probably just put this in the function itself)
                self.register['vf'] = 1
            else:
                self.register['vf'] = 0
        elif opcode[0] == 'e':  # [EX--] -> keyboard conditional
            if opcode[2:] == '9e':  # skip next instruction if key with the value of Vx is pressed
                vx_key = self.register['v'+opcode[1]]
                # if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2
                if self.keys[vx_key]:
                    self.pc += 2
            elif opcode[2:] == 'a1':  # skip next instruction if key with the value of Vx is not pressed
                vx_key = self.register['v'+opcode[1]]
                # if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2
                if not self.keys[vx_key]:
                    self.pc += 2
        elif opcode[0] == 'f':  # [FX--] -> handles memory, bcd, timers, and keyboard
            if opcode[2:] == '07':  # set VX = DT value
                self.register['v'+opcode[1]] = self.timers['dt']
            elif opcode[2:] == '0a':  # wait for a key press, and then store the value of the key in Vx
                key_pressed = False
                while not key_pressed:
                    event = pygame.event.wait()  # wait for an event 
                    self.keyboard_control(event_overide=event)  # check keyboard with event
                    for i in range(len(self.keys)):  # loop through all the keys
                        if self.keys[i]:  # if the key was pressed, then store it in memory VX
                            self.register['v'+opcode[1]] = i  
                            key_pressed = True
            elif opcode[2:] == '15':  # set DT = VX
                self.timers['dt'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '18':  # set ST = VX
                self.timers['st'] = self.register['v'+opcode[1]]
            elif opcode[2:] == '1e':  # set I = I + VX
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
                self.memory[self.index] = bcd // 100
                self.memory[self.index + 1] = (bcd // 10) % 10
                self.memory[self.index + 2] = bcd % 10
                print(self.memory[self.index])
                print(self.memory[self.index+1])
                print(self.memory[self.index+2])
            elif opcode[2:] == '55':  # store registers V0 through Vx in memory starting at location I
                for i in range(int(opcode[1])+1, 16):
                    reg = hex(i)[2:]
                    self.memory[self.index + i] = self.register[f'v{reg}']
            elif opcode[2:] == '65':  # read registers V0 through Vx from memory starting at location I
                for i in range(int(opcode[1])+1):
                    reg = hex(i)[2:]
                    self.register[f'v{reg}'] = self.memory[self.index + i]
        # increment the program counter by 2 after each operation
        self.pc += 2  
        # increment the timers if they contain non-zero values 
        while self.timers != 0:
            if self.timers['dt'] == 0:
                break
            self.timers['dt'] -= 1
        while self.timers != 0:
            if self.timers['st'] == 0:
                break
            self.timers['st'] -= 1
    # <--- Fetch --->
    def fetch_instr(self, operation: str=None):
        #self.index = self.pc
        if operation:
            self.opcode = operation  # used for debugging
        else:
            high = hex(self.memory[self.pc])[2:]  # high bit
            low = hex(self.memory[self.pc + 1])[2:]  # low bit
            # add padding to hex value
            if len(high) == 1:
                high = '0' + high
            if len(low) == 1:
                low = '0' + low
            self.current_opcode = high + low  # 16 bit instruction
            self.decode_execute(self.current_opcode)
    # <--- Display Functionality --->
    def draw(self, vx : int, vy : int, n : int):
        collided = False
        for i in range(n):
            pixel = self.memory[self.index + i]
            for j in range(8):
                if (pixel & (0x80 >> j)) != 0:
                    try:
                        if self.grid[vy+i][vx+j] == 1:
                            collided = True
                        self.grid[vy + i][vx + j] ^= 1
                    except:
                        continue
        if collided:
            self.draw_flag = True
    def display_loop(self):
        # draws pixels (really just rectangles) on the screen according to the grid
        rows, cols = self.grid.shape
        for i in range(rows):
            for j in range(cols):
                colour = [0, 0, 0]  # black
                # if the cell (address) contains a '1', then a white pixel should be drawn
                if self.grid[i][j] == 1:
                    colour = [255, 255, 255]  # white
                pygame.draw.rect(
                    self.screen, colour, 
                    [j*self.scale, i*self.scale, self.scale, self.scale], 0
                )
        pygame.display.flip()
    # <--- Keyboard Functionality --->
    def keyboard_control(self, event_overide: pygame.event.Event=None):
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
    # <--- Reset Functionality --->
    def reset(self):
        pass
    # <--- Read ROM --->
    def read_rom(self, offset):
        self.reset()  # reset everything to it's default values
        data = open(self.filename, 'rb').read()
        # store data in memory
        for index, value in enumerate(data):
            self.memory[offset+index] = value
    # <--- Processor Cycle Functionality -->
    def run(self):
        clock = pygame.time.Clock()
        iter = 0
        while True:
            try:
                clock.tick(300)
                self.keyboard_control()
                self.fetch_instr()
                self.display_loop()
                iter += 1
            except Exception as e:
                print(e)
                print(iter)
                break


if __name__ == '__main__':
    cpu = Chip8(10, 'Pong.ch8')
    cpu.run()