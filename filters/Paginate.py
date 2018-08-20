from django.urls import reverse

from .base import CheckedFilter

class Paginate(CheckedFilter):
    def __init__(self, page, items_per_page=5, on="paths"):
        super().__init__(inputs=on, outputs=[on,"page"])
        self.on = on
        self.page = page
        self.items_per_page = items_per_page

    def __call__(self, request, context):
        context["page"] = {"num": self.page}

        article_paths = context[self.on]
        #TODO: Sort filter
        article_paths = sorted(list(article_paths), reverse=True)

        num_pages = (len(article_paths)-1) // self.items_per_page + 1
        page_index = self.page - 1
        if page_index < 0 or page_index >= num_pages:
            raise Http404

        url_name = request.resolver_match.url_name
        url_name = "blog:" + url_name
        if url_name.find("page") < 0: url_name += "-page"
        if self.page > 1:
            context["page"]["prev"] = reverse(url_name, kwargs={"page":self.page-1})
        if self.page < num_pages:
            context["page"]["next"] = reverse(url_name, kwargs={"page":self.page+1})

        start_article = page_index*self.items_per_page


        article_paths = article_paths[
            page_index*self.items_per_page:(page_index+1)*self.items_per_page]
        context[self.on] = article_paths

        return request, context
