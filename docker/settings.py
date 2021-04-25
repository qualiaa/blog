"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import inspect
import secrets
from pathlib import Path

import jamie_blog

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = secrets.token_urlsafe()
DEBUG = "DJANGO_DEBUG" in os.environ

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Application definition

INSTALLED_APPS = [
    "jamie_blog",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Blog settings

BLOG_ARTICLES_PER_PAGE = 5

BLOG_ROOT_DIR = Path(inspect.getfile(jamie_blog)).parent
BLOG_DATA_DIR = BLOG_ROOT_DIR / "data"

BLOG_EMOJI_JSON_FILE = BLOG_DATA_DIR / "emoji.json"
BLOG_EMOJI_SHORT_NAMES_FILE = BLOG_DATA_DIR / "short_names.json"
BLOG_CSL_FILE = BLOG_DATA_DIR / "third_party/ieee.csl"

_blog_path = Path("/home/blog")
BLOG_ARTICLE_PATH = _blog_path / "articles"
BLOG_WIP_PATH = _blog_path / "wip"
BLOG_TAG_PATH = _blog_path / "tags"
BLOG_CACHE_PATH = _blog_path / "cache"

BLOG_ARTICLE_FILENAME = "article"
BLOG_TEMPLATE_LOCAL_URL = "LOCAL"

BLOG_DATE_GLOB_STRING = f"{'[0-9]' * 4}-{'[0-9]' * 2}-{'[0-9]' * 2}"

BLOG_PANDOC_PATH = "pandoc"
BLOG_PANDOC_MARKDOWN_EXTENSIONS = [
    "blank_before_header",
    "space_in_atx_header",
    "implicit_header_references",
    "blank_before_blockquote",
    "emoji",
    "fenced_code_blocks",
    "fenced_code_attributes",
    "inline_code_attributes",
    "line_blocks",
    "fancy_lists",
    "definition_lists",
    "startnum",
    "table_captions",
    "yaml_metadata_block",
    "all_symbols_escapable",
    "intraword_underscores",
    "strikeout",
    "superscript",
    "subscript",
    "raw_html",
    "tex_math_dollars",
    "latex_macros",
    "markdown_in_html_blocks",
    "shortcut_reference_links",
    "implicit_figures",
]

BLOG_PANDOC_OPTIONS = [
    "--mathjax",
    "--no-highlight",
]

BLOG_TAGS = ["diary", "games", "machine learning", "notes", "opinions", "programming", "writing"]

BLOG_TAG_COLORS = [
    (47, 66, 90),
    (int("7a", 16), int("82", 16), int("ab", 16)),
    (217, 93, 57),
    (130, 163, 161),
    (int("bf", 16), int("ab", 16), int("25", 16)),
    (int("85", 16), int("2f", 16), int("5a", 16)),
    (212, 154, 175),
]

STATIC_ROOT = _blog_path/"static"
