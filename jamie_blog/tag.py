from os.path import relpath

from django.conf import settings as s

if __name__ == "__main__":
    import article
else:
    from . import article


def get_articles_for_tag(tag):
    return [x.resolve() for x in (s.BLOG_TAG_PATH/tag).iterdir()]


def _clear_existing_tags():
    for tag_folder in s.BLOG_TAG_PATH.iterdir():
        for tagged_article in tag_folder.iterdir():
            tagged_article.unlink()


def add_article_to_tag(article_folder, tag):
    # TODO: Warn on nonexistent tags
    tag_folder = s.BLOG_TAG_PATH/tag
    symlink = tag_folder/article_folder.name
    article_relative_to_tag_folder = relpath(article_folder, tag_folder)
    if tag_folder.exists():
        symlink.symlink_to(article_relative_to_tag_folder)
    else:
        raise FileNotFoundError


def tag_article(folder_path):
    markdown_path = folder_path/s.BLOG_MARKDOWN_FILENAME
    metadata = article.extract_metadata(markdown_path)
    for tag in metadata.get("tags"):
        add_article_to_tag(folder_path, tag)


def init_tags():
    """ Create a folder for each tag

    Raises:
        AttributeError if settings.BLOG_TAGS not set
    """
    for tag in s.BLOG_TAGS:
        (s.BLOG_TAG_PATH/tag).mkdir(mode=0o600, exist_ok=True, parents=True)


def tag_all():
    _clear_existing_tags()

    paths = list(article.get_article_paths())
    if len(paths) == 0:
        raise FileNotFoundError("No articles to tag")

    for folder_path in paths:
        tag_article(folder_path)


if __name__ == "__main__":
    tag_all()
