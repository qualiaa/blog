import datetime

from . import settings as s
from . import article

def publish(slug):
    date_string = datetime.date.today().isoformat()
    source_path = s.WIP_PATH/slug

    dest_path = s.ARTICLE_PATH/"{}_{}".format(date_string,slug)

    if not source_path.exists():
        raise FileNotFoundError("Could not find article to publish",source_path)

    try:
        if dest_path.exists() or article.path_from_slug(slug):
            raise FileExistsError("Article already published",dest_path)
    except FileNotFoundError: pass

    source_path.rename(dest_path)
