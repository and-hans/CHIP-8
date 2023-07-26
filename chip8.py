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
        self.reg = {}  # stores 16 general purpose registers
        for i in range(16):
            self.reg['v'+str(hex(i))[2:]] = 0