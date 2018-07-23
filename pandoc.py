import pathlib
import re
import subprocess

from . import settings as s


def pandoc2mathjax(string):
    string = re.sub("<span class=\"math inline\">"+re.escape(r"\(")+
                    "(.*)" + re.escape(r"\)") + "</span>",
                    "<script type=\"math/tex\">\g<1></script>", string)
    string = re.sub("<span class=\"math display\">"+re.escape(r"\[")+
                    "(.*)" + re.escape(r"\]") + "</span>",
                    "<script type=\"math/tex; mode=display\">\g<1></script>",
                    string)
    return string


def md2html(path_or_string):
    command = [
        "pandoc",
        *s.PANDOC_OPTIONS,
        "-f", "+".join(["markdown"]+s.PANDOC_EXTENSIONS),
        "-t", "html"]

    if type(path_or_string) == str:
        stdin=str.encode(path_or_string)
    elif issubclass(type(path_or_string), pathlib.Path):
        stdin=None
        command += [str(path_or_string)]
    else:
        raise TypeError

    completed_process = subprocess.run(
        command,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True)

    return completed_process.stdout.decode("utf-8")
