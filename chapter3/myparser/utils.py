class BitVector():
    def __init__(self, size=None):
        self.len = 1
        if size is not None:
            self.len = size
        self.bits = [0] * self.len

    def get(self, idx):
        if idx < self.len:
            return self.bits[idx]
        return None

    def set(self, idx):
        if idx < self.len:
            self.bits[idx] = 1
        else:
            self.len = self.len * 2 # expand the bit set
            self.bits += [0] * self.len
            self.set(idx) # call set recursively as expand once may not enough.

    def clear(self, idx):
        self.bits[idx] = 0