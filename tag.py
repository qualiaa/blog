from os.path import relpath
import pathlib

import yaml

if __name__ == "__main__":
    import article
    import settings
else:
    from . import article
    from . import settings

TAG_PATH = pathlib.Path("blog/tags")

def get_articles_for_tag(tag):
    return [x.resolve() for x in (TAG_PATH/tag).iterdir()]

def _clear_existing_tags():
    for tag_folder in TAG_PATH.iterdir():
        for tagged_article in tag_folder.iterdir():
            tagged_article.unlink()

def add_article_to_tag(article_folder, tag):
    # TODO: Warn on nonexistent tags
    tag_folder = TAG_PATH/tag
    symlink = tag_folder/article_folder.name
    article_relative_to_tag_folder = relpath(article_folder, tag_folder)
    if tag_folder.exists():
        symlink.symlink_to(article_relative_to_tag_folder)
    else:
        raise FileNotFoundError

def tag_article(folder_path):
    markdown_path = folder_path/s.MARKDOWN_FILENAME
    metadata = article.extract_metadata(markdown_path)
    for tag in metadata.get("tags"):
        add_article_to_tag(folder_path, tag)

def tag_all():
    _clear_existing_tags()

    paths = list(article.get_article_paths())
    if len(paths) == 0:
        raise FileNotFoundError

    for folder_path in paths:
        tag_article(folder_path)

if __name__ == "__main__":
    tag_all()
