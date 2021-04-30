import json
import os
import sys
from functools import reduce
from pathlib import Path
from operator import add

DATA_ROOT = Path(sys.argv[0]).absolute().parents[1] / "jamie_blog/data"
EMOJI_JSON = os.getenv("EMOJI_DATA", DATA_ROOT/"third_party/slack_emoji.json")
LOOKUP_OUTPUT = os.getenv("LOOKUP_OUTPUT", DATA_ROOT/"emoji.json")
SHORT_NAMES_OUTPUT = os.getenv("LOOKUP_OUTPUT", DATA_ROOT/"short_names.json")


def generate_emoji_list(json_path):
    with open(json_path) as f:
        emoji_data = json.load(f)

    short_names = [x["short_name"] for x in emoji_data]
    other_names = [x["short_names"] for x in emoji_data]
    codepoints = [x["unified"].split("-") for x in emoji_data]

    characters = [
        reduce(add, [chr(int(hx,16)) for hx in codepoint])
        for codepoint in codepoints
    ]
    emoji_lookup = dict(zip(short_names,characters))

    short_name_lookup = {}
    for name, others in zip(short_names, other_names):
        others.remove(name)
        if len(others) == 0:
            continue
        short_name_lookup[name] = others

    with LOOKUP_OUTPUT.open("w") as f:
        json.dump(emoji_lookup, f, separators=(',', ':'))
    with SHORT_NAMES_OUTPUT.open("w") as f:
        json.dump(short_name_lookup, f, separators=(',', ':'))


if __name__ == "__main__":
    generate_emoji_list(EMOJI_JSON)
