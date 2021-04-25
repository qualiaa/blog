from . import base as F
from .Input import Input, ContextInput

from .Paginate import Paginate
from .AddArchive import AddArchive
from .Tags import Tags
from .Render import Render
from .For import For
from .article import SlugToPath, Metadata, GetFullText, GetStub


class Plus(F.Pipe):
    def __init__(self, n):
        super().__init__()
        self.n = n

    def __call__(self,x):
        return x + self.n

class Mult(F.Pipe):
    def __init__(self, n):
        super().__init__()
        self.n = n

    def __call__(self,x):
        return x * self.n

def run():
    half = F.Lambda(lambda x: x//2)
    return Input(5) > Plus(2) | Mult(10) | half | Plus(3)

def deps_test():
    f1 = ContextInput(None, context={"url": "asdsd"}) >AddArchive() | Paginate(5)
    return f1._in, f1._out, f1._true_outputs

def slug_test():
    return (ContextInput(request=None, slug="test")>SlugToPath())[1]["path"]

def article_test():
    slug = "test"
    pipes = SlugToPath() | Metadata() | GetFullText()
    return (ContextInput(request=None, slug=slug) > pipes)[1]

def paginate_test():
    class B:
        url_name = "index"
    class A:
        resolver_match = B()

    request = A()

    pipes = Tags(["diary"]) | Paginate(1) |\
        For(over="paths",target="path",to="article_list",f=
            Metadata() | GetStub())

    return (ContextInput(request) > pipes)[1]
