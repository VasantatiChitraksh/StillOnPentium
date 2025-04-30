import math
from collections import deque

class CacheLine:
    def __init__(self, block_size):
        self.block_size = block_size
        self.tag = None
        self.block = [0] * (block_size // 4)  # 4 bytes per word

class CacheSet:
    def __init__(self, associativity, block_size):
        self.lines = [CacheLine(block_size) for _ in range(associativity)]
        self.lru = deque(self.lines)  # LRU ordering

class Cache:
    def __init__(self,cache_size=64, block_size=8, associativity=4):
        self.cache_size = cache_size  # in bytes
        self.block_size = block_size   # bytes
        self.associativity = associativity
        self.num_blocks = self.cache_size // self.block_size
        self.num_sets = self.num_blocks // self.associativity
        self.sets = [CacheSet(self.associativity, self.block_size) for _ in range(self.num_sets)]

        self.offset_bits = int(math.log2(self.block_size))
        self.index_bits = int(math.log2(self.num_sets))

        self.misses = 0
        self.hits = 0

    def _parse_address(self, address):
        offset = address % self.block_size
        index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)
        return tag, index, offset

    def findCache(self, address):
        tag, index, offset = self._parse_address(address)
        cache_set = self.sets[index]

        for line in cache_set.lines:
            if line.tag == tag:
                # Move line to the end (most recently used)
                cache_set.lru.remove(line)
                cache_set.lru.append(line)
                word_index = offset // 4
                return True, line.block[word_index]

        return False, None

    def replaceCacheLine(self, address, block_data):
        tag, index, _ = self._parse_address(address)
        cache_set = self.sets[index]

        # Evict least recently used
        victim = cache_set.lru.popleft()
        victim.tag = tag
        victim.block = block_data.copy()
        cache_set.lru.append(victim)

    def update_word(self, address, value):
        tag, index, offset = self._parse_address(address)
        cache_set = self.sets[index]

        for line in cache_set.lines:
            if line.tag == tag:
                word_index = offset // 4  
                line.block[word_index] = value

                if line in cache_set.lru:
                    cache_set.lru.remove(line)
                cache_set.lru.append(line)
                return  
            
        raise ValueError(f"Trying to update a word not found in cache! Address: {address}")

