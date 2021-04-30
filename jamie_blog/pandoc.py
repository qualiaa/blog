import pathlib
import subprocess

from django.conf import settings as s


def pandoc2mathjax(string):
    """
    string = re.sub("<span class=\"math inline\">"+re.escape(r"\(")+
                    "(.*?)" + re.escape(r"\)") + "</span>",
                    "<script type=\"math/tex\">\g<1></script>", string)
    string = re.sub("<span class=\"math display\">"+re.escape(r"\[")+
                    "(.*?)" + re.escape(r"\]") + "</span>",
                    "<script type=\"math/tex; mode=display\">\g<1></script>",
                    string)
    """
    return string


def md2html(path_or_string, bib_path=None):
    return _run_cmd(*_build_pandoc_cmd(
        path_or_string,
        "+".join(["markdown"]+s.BLOG_PANDOC_MARKDOWN_EXTENSIONS),
        bib_path))


def org2html(path_or_string, bib_path=None):
    return _run_cmd(*_build_pandoc_cmd(
        path_or_string,
        "org+smart",
        bib_path))


def _run_cmd(command, stdin):
    return subprocess.run(
        command,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True).stdout.decode("utf-8")


class PandocFilter:
    def __init__(self, path):
        self.path = path
        self.priority = int(path.name[:2])
        self.lua = path.suffix == ".lua"

    def flag(self):
        return ["--lua-filter" if self.lua else "--filter", self.path]


def _get_filters():
    filter_paths = (s.BLOG_ROOT_DIR/"pandoc_filters").glob("[0-9][0-9]-*")
    pre, post = [], []
    for f in sorted(map(PandocFilter, filter_paths), key=lambda f: f.priority):
        (pre if f.priority < 50 else post).append(f)
    return pre, post


def _resolve_filters(filters):
    return sum((f.flag() for f in filters), start=[])


def _build_pandoc_cmd(path_or_string, output_format, bib_path=None):
    opts = list(s.BLOG_PANDOC_OPTIONS)

    pre_filters, post_filters = _get_filters()
    opts += _resolve_filters(pre_filters)
    if bib_path:
        opts += [
            "--citeproc",
            "--csl", s.BLOG_CSL_FILE,
            "--bibliography", str(bib_path)
        ]
    opts += _resolve_filters(post_filters)

    command = [
        s.BLOG_PANDOC_PATH,
        *opts,
        "-f", output_format,
        "-t", "html"
    ]

    if isinstance(path_or_string, str):
        stdin = str.encode(path_or_string)
    elif isinstance(path_or_string, pathlib.Path):
        stdin = None
        command += [str(path_or_string)]
    else:
        raise TypeError("path_or_string must be Path or str")
    return command, stdin
