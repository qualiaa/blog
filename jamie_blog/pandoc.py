import pathlib
import re
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


def _build_pandoc_cmd(path_or_string, output_format, bib_path=None):
    opts = list(s.BLOG_PANDOC_OPTIONS)

    if bib_path:
        opts += [
            "--citeproc",
            "--csl", s.BLOG_CSL_FILE,
            "--bibliography", str(bib_path)
        ]

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
