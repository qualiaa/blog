FROM python:3-alpine

RUN apk add uwsgi \
    && pip install django \
    && django-admin startproject mysite

COPY . app/
RUN pip install ./app \
    && ln -sf app/docker/settings.py mysite/mysite/settings.py

CMD ["uwsgi", "--ini", "app/docker/uwsgi.ini"]
