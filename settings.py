import pathlib

ARTICLES_PER_PAGE = 5
MARKDOWN_FILENAME = "article.md"
ARTICLE_PATH=pathlib.Path("blog/articles/")
WIP_PATH = ARTICLE_PATH/"wip"
TAG_PATH = pathlib.Path("blog/tags")
date_glob_string = "{}-{}-{}".format("[0-9]" * 4,"[0-9]" * 2, "[0-9]" * 2)

TEMPLATE_LOCAL_URL = "STATIC"

PANDOC_EXTENSIONS = [
    "blank_before_header",
    "space_in_atx_header",
    "implicit_header_references",
    "blank_before_blockquote",
    "fenced_code_blocks",
    "fenced_code_attributes",
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
    "markdown_in_html_blocks",
    "shortcut_reference_links",
    "implicit_figures"
]

PANDOC_OPTIONS = [
    "--mathjax",
    "--no-highlight"
]
