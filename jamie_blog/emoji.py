import json
import pathlib
import re
from functools import reduce
from operator import add

from django.conf import settings as s

def slack2unicode(input_string):
    with s.BLOG_EMOJI_JSON_FILE.open() as f:
        emoji_lookup = json.load(f)
    with s.BLOG_EMOJI_SHORT_NAMES_FILE.open() as f:
        short_name_lookup = json.load(f)

    working_string = input_string
    for match in re.finditer(":([0-9a-zA-Z_-]+):",input_string):
        short_name = match[1]

        character = None
        if short_name in emoji_lookup:
            character = emoji_lookup[short_name]
        else:
            for name, others in short_name_lookup.items():
                if short_name in others:
                    character = emoji_lookup[name]
                    break

        if character is not None:
            working_string = re.sub(match[0], character, working_string)

    return working_string

def generate_emoji_list(json_path):
    with open(json_path) as f:
        emoji_json = json.load(f)

    short_names = [x["short_name"]         for x in emoji_json]
    other_names = [x["short_names"]        for x in emoji_json]
    codepoints  = [x["unified"].split("-") for x in emoji_json]

    characters = [reduce(add,[chr(int(hx,16)) for hx in codepoint])
            for codepoint in codepoints]
    emoji_lookup = dict(zip(short_names,characters))

    short_name_lookup = {}
    for name, others in zip(short_names, short_name_lists):
        others.remove(name)
        if len(others) == 0: continue
        short_name_lookup[name] = others

    with s.BLOG_EMOJI_JSON_FILE.open("w") as f:
        json.dump(emoji_lookup,f,separators=(',',':'))
    with s.BLOG_SHORT_NAMES_FILE.open("w") as f:
        json.dump(short_name_lookup,f,separators=(',',':'))


if __name__ == "__main__":
    emoji_path = pathlib.Path(s.BLOG_DATA_DIR/"third_party/slack_emoji.json")
    generate_emoji_list(emoji_path)
