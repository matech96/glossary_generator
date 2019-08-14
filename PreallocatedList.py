class PreallocatedList:
    def __init__(self, size, dtype):
        self._data = size * [dtype]
        self.last_i = 0

    def append(self, obj):
        self._data[self.last_i] = obj
        self.last_i += 1

    def tolist(self):
        return self._data[:self.last_i]
