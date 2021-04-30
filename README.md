# Personal Blog

This is my own personal blog. I was kind of messing around and it's a bit
eccentric, but you can use it if you like.

## Quick start (local install)

1. [Install Django](https://docs.djangoproject.com/en/3.2/intro/install/) and
   [set up a Django project](https://docs.djangoproject.com/en/3.2/intro/tutorial01/).

2. Clone this repository with `git clone --recursive github.com/qualiaa/blog`.

3. Install the package with `pip install ./blog`.

4.  In your Django project's `settings.py`, add `"jamie_blog"` to
    `INSTALLED_APPS`:


    ```python
    INSTALLED_APPS = [
        ...
        "jamie_blog",
    ]
    ``` 

5. Copy the `BLOG_` settings from `docker/settings.py` and adjust to suit your
   needs.

6. Include the `jamie_blog` URLconf in your project's `urls.py`:

   ```python
   path('blog/', include('jamie_blog.urls')),
   ```

7. Start the development server with `python manage.py runserver` and visit
   http://127.0.0.1:8000/blog/ to see the blog in action.

## Quick start (Docker Compose)

1. Clone this repository with `git clone --recursive github.com/qualiaa/blog`.

2. Configure [`docker/settings.py`](docker/settings.py) to suit your needs.

3. You may want to make `wip` folder and add it as bind-mount in
   [`docker/docker-compose.yml`](docker/docker-compose.yml).

4. Run `docker-compose -f docker/docker-compose up`
