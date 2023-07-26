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
        self.opcode = '0000'  # current operation
    
    # <--- Execute --->
    def decode_execute(self, operation: str):
        # increment the program counter by 2 after each operation
        self.pc += 2  

    # <--- Fetch --->
    def fetch_instr(self, operation: str=None):
        if operation:
            self.opcode = operation  # used for debugging
        else:
            high = self.memory[self.pc]  # high bit
            low = self.memory[self.pc + 1]  # low bit
            self.opcode = high + low  # 16 bit instruction
            self.decode_execute(self.opcode)

