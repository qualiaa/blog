import pathlib
import re
import subprocess

from django.conf import settings

extensions = [
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

options = [
    "--mathjax",
    "--no-highlight"
]

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
        *options,
        "-f", "+".join(["markdown"]+extensions),
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
