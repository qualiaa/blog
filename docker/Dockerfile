FROM python:3-alpine

RUN apk add uwsgi-python3 \
    && adduser -D http
USER http
WORKDIR /home/http
ENV PATH="/home/http/.local/bin:$PATH"
RUN pip install django \
    && django-admin startproject mysite
COPY . app/
RUN pip install ./app \
    && ln -sf app/docker/settings.py mysite/mysite/settings.py

CMD ["uwsgi", "--ini", "app/docker/uwsgi.ini"]
