from abc import ABC, abstractmethod

class Filter(ABC):
    def __or__(self, f):
        return Lambda(lambda x: f(self(x)))

    @abstractmethod
    def __call__(self): pass
        

class Lambda(Filter):
    def __init__(self, func):
        self.func = func

    def __call__(self,*args, **kargs):
        return self.func(*args, **kargs)

class Input(Filter):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

    def __or__(self, f:Filter):
        return f(*self.args, **self.kargs)

    def __call__(self): pass
