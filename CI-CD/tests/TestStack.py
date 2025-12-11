from src.Stack import Stack
import pytest

class TestStack:
    def test_empty(self):
        stack = Stack()
        assert stack.empty() == True
        stack.put(1)
        assert stack.empty() == False

    def test_put_get(self):
        stack = Stack()
        stack.put(1)
        stack.put(2)
        stack.put(3)
        
        assert stack.get() == 3
        assert stack.get() == 2
        assert stack.get() == 1
        assert stack.get() is None
        assert stack.empty() == True

    def test_capacity_expansion(self):
        stack = Stack()
        initial_capacity = stack.capacity
        for i in range(initial_capacity + 1):
            stack.put(i)
        
        assert stack.capacity == initial_capacity * 2
        assert stack.size == initial_capacity + 1