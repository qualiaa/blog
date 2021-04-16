from django.conf import settings as s
from django.http import HttpResponseNotModified

from .filters import article as a
from .filters import errors as e
from .filters import cache as c
from .filters.flow import Either, Alternative
from .filters.inputs import ContextInput
from .filters.outputs import JSON, ToRequestContext
from .filters.postprocessing import postprocessing
from .filters.utils import Extract, Remove


def wip(request, slug):
    path = s.BLOG_WIP_PATH / slug
    markdown_path = path / s.BLOG_MARKDOWN_FILENAME
    local_mtime = markdown_path.stat().st_mtime
    print("Server mtime:",local_mtime)
    if "mtime" in request.POST:
        print("Client mtime:",request.POST["mtime"])
        if int(local_mtime) <= float(request.POST["mtime"]):
            return HttpResponseNotModified()

    return ContextInput(request, path=path, slug=slug, mtime=local_mtime) >\
            a.MetadataSafe()   |\
            Alternative(c.CachedText(),
                Either(a.MetadataDangerous() | a.GetFullText() |
                    postprocessing() | c.CacheHTML(),
                       e.NotFound)) |\
            Extract("article")  |\
            Remove({"path","markdown"}) |\
            JSON()
