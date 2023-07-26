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
        elif opcode[0] == '6':  # [6XNN] -> set: set vx to nn
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
