from .base import Filter, CheckedFilter, _to_set

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

class Remove(CheckedFilter):
    def __init__(self, keys):
        super().__init__(keys)
        self.keys = _to_set(keys)

    def __call__(self, request, context):
        for key in self.keys:
            del context[key]
        return request, context

class Extract(CheckedFilter):
    def __init__(self, keys):
        super().__init__(inputs=keys)
        self.keys = _to_set(keys)

    def __call__(self, request, context):
        for key in self.keys:
            val_dict = context[key]
            if type(val_dict) != dict:
                raise TypeError("Absorb only works on dict values")
            context.update(val_dict)
            if key not in val_dict:
                del context[key]
        return request, context
