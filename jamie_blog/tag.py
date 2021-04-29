import logging
from os.path import relpath
from pathlib import Path

from django.conf import settings as s

if __name__ == "__main__":
    import article
else:
    from . import article


class Tag:
    def __init__(self, name: str, *, create=False):
        self._machine_name = self._munge(name)

        if not self.folder.exists():
            if create:
                self._create()
            else:
                raise FileNotFoundError(f"No folder {self.folder} for "
                                        f"{self.pretty_name}")

    @property
    def pretty_name(self) -> str:
        return self._unmunge(self.machine_name)

    @property
    def machine_name(self) -> str:
        return self._machine_name

    @property
    def article_paths(self):
        yield from map(Path.resolve, self.folder.iterdir())

    @property
    def folder(self) -> Path:
        return s.BLOG_TAG_PATH/self.machine_name

    def add_article(self, article_folder: Path):
        # TODO: Warn on nonexistent tags
        symlink = self.folder/article_folder.name
        article_relative_to_tag_folder = relpath(article_folder, self.folder)
        symlink.symlink_to(article_relative_to_tag_folder)

    def _create(self):
        self.folder.mkdir(mode=0o700, exist_ok=True, parents=True)

    def clear_articles(self):
        for article_link in self.article_paths:
            article_link.unlink()

    @staticmethod
    def _munge(name: str) -> str:
        return name.lower().replace(" ", "_")

    @staticmethod
    def _unmunge(name: str) -> str:
        return name.title().replace("_", " ")


def _clear_existing_tags():
    for tag_folder in s.BLOG_TAG_PATH.iterdir():
        for tagged_article in tag_folder.iterdir():
            tagged_article.unlink()


def tag_article(folder_path):
    try:
        path = article.get_text_path(folder_path)
    except FileNotFoundError as e:
        logging.error("Could not tag article: %s", e.args[0])
        return
    metadata = article.extract_metadata(path)
    tag_names = metadata.get("tags", [])
    if not tag_names:
        logging.warning("No tags for article: %s", path)
    for tag in map(Tag, tag_names):
        tag.add_article(folder_path)


def init_tags():
    """ Create a folder for each tag

    Raises:
        AttributeError if settings.BLOG_TAGS not set
    """
    for tag in s.BLOG_TAGS:
        Tag(tag, create=True)


def tag_all():
    _clear_existing_tags()
    for folder_path in article.get_article_paths():
        tag_article(folder_path)


if __name__ == "__main__":
    tag_all()
