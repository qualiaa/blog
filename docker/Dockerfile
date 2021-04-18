FROM python:3-alpine

# Django and uWSGI system-wide
RUN apk add gcc musl-dev linux-headers \
    && pip install django uwsgi \
    && apk del gcc musl-dev linux-headers

# Install pandoc
RUN wget https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-linux-amd64.tar.gz \
    && tar xf pandoc-2.13-linux-amd64.tar.gz \
    && mv pandoc*/bin/* /usr/bin \
    && rm -r pandoc*

# Create and configure blog user
RUN adduser -D blog
USER blog
WORKDIR /home/blog
ENV PATH="/home/blog/.local/bin:$PATH"

# Install the blog app
RUN django-admin startproject mysite
COPY . app/
RUN pip install ./app \
    && cp app/docker/*.py mysite/mysite \
    && python mysite/manage.py collectstatic

CMD ["uwsgi", "--ini", "app/docker/uwsgi.ini"]
