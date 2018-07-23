from abc import abstractmethod

from .. import article

from .errors import FilterError

class Input:
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

    def __gt__(self, f):
        return f(*self.args, **self.kargs)

class ContextInput(Input):
    def __init__(self, request, **kargs):
        self.context = kargs
        super().__init__(request, context=self.context)

    def __gt__(self, f):
        inputs = set(self.context.keys())
        if not inputs.issuperset(f._in):
            raise TypeError("Inputs not satisfied: {}".format(f._in - inputs))
        print(self.context)
        return super().__gt__(f)

# TODO: LsPath
class PublishedPaths(ContextInput):
    def __init__(self, request):
        super().__init__(request, paths=article.get_article_paths())

