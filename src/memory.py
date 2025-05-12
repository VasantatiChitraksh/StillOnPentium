class Memory:
    def __init__(self, size_in_bytes=4096):
        self.size = size_in_bytes
        # // is used as it returns an integer value instead of float
        self.word = [0] * (size_in_bytes // 4)
        self.data_section_end = 0

    def read_word(self, address: int) -> int:
        if address % 4 != 0 or address < 0 or address >= self.size//4:
            # Check for valid address
            if address <= (self.size-4) and address >= self.data_section_end:
                index = address//4
                return self.word[index]
            raise ValueError(
                f"Invalid address requested : {address*4} max is 4095 4Kb")
        index = address//4
        return self.word[index]

    def write_word(self, address: int, value: int):
        if address % 4 != 0 or address < 0 or address >= self.size//4:
            if address <= (self.size-4) and address >= self.data_section_end:
                index = address//4
                self.word[index] = value
                return
            raise ValueError(
                f"Invalid address requested : {address*4} max is 4095 4Kb")
        index = address//4
        self.word[index] = value

    def set_data_section_end(self, address: int):
        self.data_section_end = address
