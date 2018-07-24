from .base import CheckedFilter
from .. import settings as s

class CacheError(Exception): pass
class CacheFileNotFound(CacheError): pass
class CacheFileOlderThanSource(CacheError): pass

def cache_file_path(article_path, stub):
    suffix = ".html"
    if stub:
        suffix = ".stub.html"

    return (s.CACHE_PATH/article_path.name).with_suffix(suffix)

class CachedText(CheckedFilter):
    def __init__(self, stub=False):
        super().__init__(inputs="article", outputs="article")
        self.stub = stub

    def __call__(self, request, context):
        path = context["article"]["path"]
        markdown_path = context["article"]["markdown"]
        cache_file = cache_file_path(path, self.stub)

        if not cache_file.exists():
            raise CacheFileNotFound()
        if markdown_path.stat().st_mtime > cache_file.stat().st_mtime:
            raise CacheFileOlderThanSource()
        print("Loading {} from cache".format(cache_file))
        with cache_file.open() as f:
            context["article"]["html"] = f.read()

        return request, context

class CacheHTML(CheckedFilter):
    def __init__(self, stub=False):
        super().__init__(inputs="article", outputs="article")
        self.stub = stub

    def __call__(self, request, context):
        html = context["article"]["html"]
        path = context["article"]["path"]

        cache_file = cache_file_path(path, self.stub)
        print ("Writing {} to cache".format(cache_file))
        with cache_file.open("w") as f:
            f.write(html)

        return request, context
