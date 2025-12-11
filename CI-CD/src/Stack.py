class Stack:
    def __init__(self):
        self.data = [None]
        self.size = 0
        self.capacity = 1
        
    def empty(self):
        return self.size == 0
    
    def put(self, item):
        if self.size == self.capacity:
            self.data += [None] * self.capacity
            self.capacity *= 2
        self.data[self.size] = item
        self.size += 1
        
    def get(self):
        if self.empty():
            return None
        self.size -= 1
        item = self.data[self.size]
        self.data[self.size] = None
        return item
    def __repr__(self):
        return f"{self.data}"