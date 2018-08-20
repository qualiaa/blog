from django.http import HttpResponseNotModified, HttpResponseBadRequest

from .filters import article as a
from .filters import errors as e
from .filters.flow import Either, For
from .filters.inputs import ContextInput
from .filters.outputs import JSON, ToRequestContext
from .filters.postprocessing import postprocessing
from .filters.utils import Extract, Remove, Lambda
from .filters.Paginate import Paginate
from .filters.Tags import Tags

from . import settings as s

def wip(request, slug):
    path = s.WIP_PATH / slug 
    markdown_path = path / s.MARKDOWN_FILENAME
    local_mtime = markdown_path.stat().st_mtime 
    if "mtime" in request.POST:
        if int(local_mtime) <= float(request.POST["mtime"]):
            return HttpResponseNotModified()

    return ContextInput(request, path=path, slug=slug, mtime=local_mtime) >\
            a.MetadataSafe()   |\
            Either(a.MetadataDangerous() | a.GetFullText() | postprocessing(),
                   e.NotFound) |\
            Extract("article")  |\
            Remove({"path","markdown"}) |\
            JSON()

def tags(request):
    try:
        tags = request.POST["tags"]
        page = request.POST["page"]
    except KeyError:
        return HttpResponseBadRequest("Require tags and page in POST")

    @Lambda
    def article_error(r, c):
        c["article"]["html"] = "Could not load article"
        return r, c

    return Tags(tags)                                               |\
            Paginate(page=page, items_per_page=s.ARTICLES_PER_PAGE) |\
            For(over="paths", to="path", giving="article", result="article_list",
                    f=a.DateAndSlugFromPath() | 
                        a.MetadataSafe() |
                        Alternative(a.MetadataDangerous(), article_error) |
                        Alternative(c.CachedText(stub=True),
                            Alternative(a.GetStub() |
                                    postprocessing() |
                                    c.CacheHTML(stub=True),
                                article_error)) |
                        Remove({"markdown","path"}))                |\
            JSON()
