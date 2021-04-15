# Personal Blog

This is my own personal blog. I was kind of messing around and it's a bit
eccentric, but you can use it if you like.

## Quick start

1. [Install Django](https://docs.djangoproject.com/en/3.2/intro/install/) and
   [set up a Django project](https://docs.djangoproject.com/en/3.2/intro/tutorial01/).

2. Clone this repository with `git clone github.com/qualiaa/blog`.

3. Install the package with `pip install ./blog`.

4.  In your Django project's `settings.py`, add `"jamie_blog"` to
    `INSTALLED_APPS`:


    ```python
    INSTALLED_APPS = [
        ...
        "jamie_blog",
    ]
    ``` 

5. Include the `jamie_blog` URLconf in your project's `urls.py`:

   ```python
   path('blog/', include('jamie_blog.urls')),
   ```

6. Start the development server and visit http://127.0.0.1:8000/blog/
   to see the blog in action.
