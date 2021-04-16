from django.apps import AppConfig
from django.conf import settings as s
from .tag import init_tags, tag_all


class BlogConfig(AppConfig):
    name = 'jamie_blog'

    def ready(self):
        for path in (s.BLOG_ARTICLE_PATH, s.BLOG_WIP_PATH, s.BLOG_CACHE_PATH,
                     s.BLOG_TAG_PATH):
            path.mkdir(mode=0o600, exist_ok=True, parents=True)

        try:
            init_tags()
        except AttributeError as e:
            if not next(s.BLOG_TAG_PATH.iterdir(), False):
                raise RuntimeError("Must either set settings.BLOG_TAGS or "
                                   "create tag subfolders in {s.BLOG_TAG_PATH}"
                                   "manually") from e
        tag_all()


default_app_config = BlogConfig
