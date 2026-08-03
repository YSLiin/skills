#!/usr/bin/env python3
"""
Takes raw Taiwanese text, and build possible list of vocabularies with candidate translations.
The default source is the MOE Taiwanese dictionary from g0v/moedict-data-twblg.  The result is
output as JSON to STDOUT. Use --pretty to pretty-print the JSON for readability, which is not
enabled by default because it is intended to be used by agents. Run with --build-dict in order
to update the local MOE Taiwanese dictionary.

Usage:
    ./gloss.py "倒佇故鄉街市的中央 笑看世界咧轉踅" --build-dict --pretty
    ./gloss.py 這個社會討趁 欲生活越來越無簡單
    ./gloss.py 心悶.txt
"""

import argparse
import json
import sys
import typing as t
from pathlib import Path

from dictionary import lookup, sync_lookup


class Args(t.Protocol):
    in_: list[str]
    pretty: bool
    build_dict: bool


def main() -> int:
    args = parse_arguments()

    if args.build_dict:
        sync_lookup()

    if not args.in_:
        text = sys.stdin.read()
    elif len(args.in_) == 1 and Path(args.in_[0]).is_file():
        text = Path(args.in_[0]).read_text(encoding='utf-8')
    else:
        text = ' '.join(args.in_)

    text = text.strip()
    if not text:
        print('error: no input text provided', file=sys.stderr)
        return 1

    vocabularies = build_vocabularies(text)

    indent = 2 if args.pretty else None
    print(json.dumps(vocabularies, ensure_ascii=False, indent=indent))
    return 0


def parse_arguments() -> Args:
    parser = argparse.ArgumentParser(
        description='Gloss Taiwanese text: every known term in it -> its Mandarin candidates (JSON).',
    )
    parser.add_argument(
        'in_',
        nargs='*',
        metavar='INPUT',
        help='Taiwanese text (quoted/unquoted) or file path. If omitted, reads from stdin.',
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print the JSON output (indented, readable).',
    )
    parser.add_argument(
        '--build-dict',
        action='store_true',
        help='Build the local MOE Taiwanese Hokkien dictionary.',
    )
    return parser.parse_args()


# TODO: sanitize text
def build_vocabularies(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}

    # NOTE:
    # Keep expanding the term until the entire sentence is covered so that we don't
    # miss cases like when "風" and "風風雨雨", but not "風風", appears in the dictionary.
    # Setting a upper limit might work given that the longest term exists in the current
    # dictionary is 14 characters, after sanitized, but we can't guarantee that won't
    # change in the future.
    for sentence in text.split():
        for i in range(len(sentence)):
            for j in range(i + 1, len(sentence) + 1):
                if (term := sentence[i:j]) in out:
                    continue

                candidates = lookup(term)
                if not candidates and len(term) > 1:
                    continue

                # NOTE: If no candidates is found even for 1-char term, keep it as is.
                out[term] = candidates or [term]

    return out


if __name__ == '__main__':
    sys.exit(main())
