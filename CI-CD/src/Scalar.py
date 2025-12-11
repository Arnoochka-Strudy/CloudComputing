from .Stack import Stack

class Scalar:
    def __init__(self, data: float, _children=(), _op='input'):
        self.data = data
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __repr__(self):
        return f"Scalar(data={self.data}, grad={self.grad})"

    def __add__(self, other: "Scalar") -> "Scalar":
        other = other if isinstance(other, Scalar) else Scalar(other)
        node = Scalar(self.data + other.data, (self, other), 'add')

        def _backward():
            self.grad += node.grad
            other.grad += node.grad
        node._backward = _backward

        return node

    def __mul__(self, other: "Scalar") -> "Scalar":
        node = Scalar(self.data * other.data, (self, other), 'mul')
        def _backward():
            self.grad += other.data * node.grad
            other.grad += self.data * node.grad
        node._backward = _backward
        
        return node
    

    def relu(self) -> "Scalar":
        relu = lambda x: x if x > 0.0 else 0.0
        node = Scalar(relu(self.data), (self,), 'relu')
        def _backward():
            drelu = lambda x: 1.0 if x > 0.0 else 0.0
            self.grad += drelu(self.data) * node.grad
        node._backward = _backward
        
        return node
    
    def backward(self):
        topo = []
        visited = set()
        stack = Stack()
        stack.put(self)
        temp_mark = set()
        while not stack.empty():
            node = stack.get()

            if node in visited:
                continue

            if node in temp_mark:
                visited.add(node)
                topo.append(node)
            else:
                temp_mark.add(node)
                stack.put(node)
                for child in node._prev:
                    if child not in visited:
                        stack.put(child)
        self.grad = 1.0
        
        for node in reversed(topo):
            node._backward()
            
if __name__ == "__main__":
    a = Scalar(5)
    b = Scalar(-7)
    c = (a + b) * a
    d = c * c + (a * b) * c
    e = (a + b + c) * d
    f = e.relu()
    f.backward()
    print(f"a={a}\nb={b}\nc={c}\nd={d}\ne={e}\nf={f}")
                        
        