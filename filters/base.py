from abc import ABC, abstractmethod

from .errors import FilterError

def _to_set(v):
    if type(v) != set:
        if type(v) == str:
            v = {v}
        else:
            v = set(v)
    return v

class Filter(ABC):
    @abstractmethod
    def __call__(self): pass

    def __or__(self, other):
        return Composition(self, other)
        """
        def composition(*args, **kargs): 
            try:
                my_result = self(*args,**kargs)
                if type(my_result) == tuple:
                    return other(*my_result)
                else:
                    return other(my_result)
            except TypeError as e:
                e.args += (type(self), type(other))
                raise RuntimeError(*e.args)

        return Lambda(composition)
        """

class CheckedFilter(Filter):
    def __init__(self, inputs={}, outputs={}):
        self._in = _to_set(inputs)
        self._out = _to_set(outputs)

    def __or__(self, other):
        if issubclass(self, Composition):
            raise RuntimeError("This should never happen")
        inputs, outputs = self._resolve_deps(self, other)

        return CheckedComposition(
                composition=super().__or__(other),
                inputs=inputs,
                outputs=outputs)

    @property
    def _true_outputs(self):
        """ true output includes input """
        return self._in | self._out

    @staticmethod
    def _resolve_deps(left, right):
        inputs = left._in | (right._in - left._true_outputs)
        outputs = left._out | right._out
        return inputs, outputs

class Composition(Filter):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __or__(self, other):
        self.right = self.right | other
        return self

    def __call__(self, *args, **kargs):
        try:
            try:
                left_result = self.left(*args,**kargs)
            except FilterError as e:
                print("DOING THE THING")
                return e.handler()

            if type(left_result) == tuple:
                return self.right(*left_result)
            else:
                return self.right(left_result)
        except TypeError as e:
            e.args += (type(self.left), type(self.right))
            raise RuntimeError(*e.args)

class CheckedComposition(Composition, CheckedFilter):
    def __init__(self, left=None, right=None, inputs={}, outputs={}, composition=None):
        CheckedFilter.__init__(self, inputs, outputs)
        if composition is not None:
            Composition.__init__(self, composition.left, composition.right)
        elif left is not None and right is not None:
            Composition.__init__(self, left, right)
        else:
            raise TypeError("CheckedComposition not provided with left and right")

class Lambda(Filter):
    def __init__(self, func):
        self.func = func

    def __call__(self,*args, **kargs):
        return self.func(*args, **kargs)

class CheckedLambda(CheckedFilter):
    def __init__(self, func, inputs={}, outputs={}):
        super().__init__(inputs, outputs)
        if type(func) == Lambda:
            self.func = func.func
        else:
            self.func = func

    def __call__(self, *args, **kargs):
        return self.func(*args, **kargs)
