import datetime
from collections import defaultdict
from itertools import repeat

from django.urls import reverse

from . import article

def context():
    # TODO: rewrite when it's not 4am
    # TODO: only list current tags?
    # TODO: stable sorting
    paths = article.get_article_paths()
    date_and_slug = [article.extract_date_and_slug_from_path(x) for x in paths]
    dates = set(datetime.date(x.year,x.month, 1) for x, _ in date_and_slug)
    years = set(x.year for x in dates)

    context = dict(zip(years,repeat({})))

    for date in dates:
        context[date.year][date.strftime("%B")] = []

    for date, slug, path in zip(*list(zip(*date_and_slug)),paths):
        title = article.slug_to_title(slug)
        markdown_path = article.markdown_path_from_folder_path(path)
        try:
            metadata = article.extract_metadata(markdown_path)
            title = metadata.get("title", title)
        except FileNotFoundError: pass
        url = reverse("blog:article",kwargs={"slug":slug})
        context[date.year][date.strftime("%B")].append((url,title))


    return {"archive": context}
