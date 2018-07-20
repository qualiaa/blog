from . import Filter as F

class Plus(F.Filter):
    def __init__(self, n):
        self.n = n

    def __call__(self,x):
        return x + self.n

class Mult(F.Filter):
    def __init__(self, n):
        self.n = n

    def __call__(self,x):
        return x * self.n

def run():
    half = F.Lambda(lambda x: x//2)
    return F.Input(5) | (Plus(2) | Mult(10) | half | Plus(3))

