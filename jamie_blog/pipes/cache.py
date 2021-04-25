import logging

from django.conf import settings as s

from .base import CheckedPipe

class CacheError(Exception): pass
class CacheFileNotFound(CacheError): pass
class CacheFileOlderThanSource(CacheError): pass

def cache_file_path(article_path, stub):
    suffix = ".html"
    if stub:
        suffix = ".stub.html"

    return (s.BLOG_CACHE_PATH/article_path.name).with_suffix(suffix)

class CachedText(CheckedPipe):
    def __init__(self, stub=False):
        super().__init__(inputs="article", outputs="article")
        self.stub = stub

    def __call__(self, request, context):
        path = context["article"]["path"]
        text_path = context["article"]["text_path"]
        cache_file = cache_file_path(path, self.stub)

        if not cache_file.exists():
            raise CacheFileNotFound(cache_file)

        if text_path.stat().st_mtime > cache_file.stat().st_mtime:
            raise CacheFileOlderThanSource()

        logging.debug("Loading %s from cache", cache_file)

        with cache_file.open() as f:
            context["article"]["html"] = f.read()

        # check stub finished state, stored as .finished file
        if self.stub:
            finished_path = cache_file.with_suffix(".finished")
            if finished_path.exists():
                finished = True
            else:
                finished = False
            context["article"]["finished"] = finished
        return request, context


class CacheHTML(CheckedPipe):
    def __init__(self, stub=False):
        super().__init__(inputs="article", outputs="article")
        self.stub = stub

    def __call__(self, request, context):
        html = context["article"]["html"]
        path = context["article"]["path"]

        cache_file = cache_file_path(path, self.stub)
        logging.debug("Writing %s to cache", cache_file)
        with cache_file.open("w") as f:
            f.write(html)

        # Save finished state as empty file
        if self.stub:
            finished_path = cache_file.with_suffix(".finished")
            if not context["article"]["finished"] and finished_path.exists():
                finished_path.unlink()
            elif context["article"]["finished"] and not finished_path.exists():
                f = finished_path.open("w")
                f.close()
        return request, context
