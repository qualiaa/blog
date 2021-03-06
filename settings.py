import pathlib

ARTICLES_PER_PAGE       = 5

ROOT_DIR                = pathlib.Path("blog")
DATA_DIR                = ROOT_DIR/"data"


ARTICLE_PATH            = ROOT_DIR/"articles"
WIP_PATH                = ARTICLE_PATH/"wip"

TAG_PATH                = ROOT_DIR/"tags"
CACHE_PATH              = ROOT_DIR/"cache"

EMOJI_JSON_FILE         = DATA_DIR/"emoji.json"
EMOJI_SHORT_NAMES_FILE  = DATA_DIR/"short_names.json"
CSL_FILE                = DATA_DIR/"third_party/ieee.csl"

MARKDOWN_FILENAME       = "article.md"
TEMPLATE_LOCAL_URL      = "LOCAL"

date_glob_string = "{}-{}-{}".format("[0-9]" * 4,"[0-9]" * 2, "[0-9]" * 2)



PANDOC_EXTENSIONS = [
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

PANDOC_OPTIONS = [
    "--mathjax",
    "--no-highlight",
]

TAG_COLORS = [
    (47, 66, 90),
    (int("7a",16), int("82",16), int("ab",16)),
    (217, 93, 57),
    (130, 163, 161),
    (int("bf",16), int("ab",16), int("25",16)),
    (int("85",16), int("2f",16), int("5a",16)),
    (212, 154, 175)
]
