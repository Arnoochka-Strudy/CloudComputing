from src.Scalar import Scalar
import pytest

class TestScalar:
    def test_add(self):
        a = Scalar(5.0)
        b = Scalar(3.0)
        c = a + b
        c.backward()
        
        assert c.data == 8.0
        assert c.grad == 1.0
        assert a.grad == 1.0
        assert b.grad == 1.0

    def test_mul(self):
        a = Scalar(4.0)
        b = Scalar(2.0)
        c = a * b
        c.backward()
        
        assert c.data == 8.0
        assert c.grad == 1.0
        assert a.grad == 2.0
        assert b.grad == 4.0

    def test_relu(self):
        a = Scalar(-2.0)
        b = a.relu()
        b.backward()
        
        assert b.data == 0.0
        assert b.grad == 1.0
        assert a.grad == 0.0

    def test_chain_rule_1(self):
        a = Scalar(2.0)
        b = Scalar(3.0)
        c = a * b
        d = c + Scalar(4.0)
        e = d.relu()
        f = e * Scalar(2.0)
        f.backward()
        
        assert f.data == 20.0
        assert f.grad == 1.0
        assert e.grad == 2.0
        assert d.grad == 2.0
        assert c.grad == 2.0 
        assert a.grad == 6.0
        assert b.grad == 4.0 
        
    def test_chain_rule_2(self):
        a = Scalar(2)
        b = Scalar(-3)
        c = Scalar(10)
        d = a + b * c
        e = d.relu()
        e.backward()
        
        assert e.data == 0.0
        assert e.grad == 1.0
        assert d.data == -28.0
        assert d.grad == 0.0

    def test_chain_rule_3(self):
        a = Scalar(1.0)
        b = Scalar(2.0)
        c = Scalar(3.0)
        
        d = a * b
        e = b * c
        f = d + e
        g = f.relu()
        h = g * Scalar(0.5)
        h.backward()
        
        assert h.data == 4.0
        assert h.grad == 1.0
        assert g.grad == 0.5
        assert f.grad == 0.5
        assert d.grad == 0.5 
        assert e.grad == 0.5
        assert a.grad == 1.0
        assert b.grad == 2.0 
        assert c.grad == 1.0