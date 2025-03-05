class Memory:
    def __init__(self, size_in_bytes=4096):
        self.size = size_in_bytes
        # // is used as it returns an integer value instead of float
        self.word = [0] * (size_in_bytes // 4)

    def read_word(self, address: int, core_id: int) -> int:
        if address % 4 != 0 or address < 0 or address >= 1024:
            # Check for valid address
            raise ValueError(f"Invalid address requested : {address} ")
        index = address//4 + (256*core_id)
        return self.word[index]

    def write_word(self, address: int, value: int, core_id: int):
        if address % 4 != 0 or address < 0 or address >= 1024:
            raise ValueError(
                f"Invalid address requested : {address} for core id : {core_id}")
        index = address//4 + (256*core_id)
        self.word[index] = value

    def write_data_to_memory(self, address: int, value: int):
        index = address//4 + (256*3)
        self.word[index] = value
