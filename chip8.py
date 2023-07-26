class Chip8:
    def __init__(self):
        self.memory = bytearray(4096)
        self.PC = 0  # program counter
        self.index = 0  # I register
        self.stack = 0 
