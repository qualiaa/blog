import re

from .base import CheckedFilter

from ..pandoc import pandoc2mathjax
from ..emoji import slack2unicode
from .. import settings as s

class PandocToMathJax(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        context["article"]["html"] = pandoc2mathjax(context["article"]["html"])
        return request, context

class SlackToUnicode(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        context["article"]["html"] = slack2unicode(context["article"]["html"])
        return request, context

class ResolveLocalURLs(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        slug = context["article"]["slug"]
        html = context["article"]["html"]
        context["article"]["html"] = re.sub(s.TEMPLATE_LOCAL_URL, slug, html)
        return request, context

def postprocessing():
    return ResolveLocalURLs()
    #return PandocToMathJax() | SlackToUnicode() | ResolveLocalURLs()
