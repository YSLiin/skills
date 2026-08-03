"""
The Taiwanese -> Mandarin dictionary does two jobs: `sync_lookup()` rebuilds the local copy, and
`lookup()` reads terms back out of it. Point this at a different source of truth by reimplementing
those two -- everything else here is specific to the one we use.

Ours is g0v/moedict-data-twblg, which republishes MOE's 臺灣閩南語常用詞辭典 as two flat JSON files
keyed directly by headword: dict-twblg.json for the main entries, dict-twblg-ext.json for the
supplementary 華語對照表. A few MB in total, against a 259MB clone of the pre-sharded data behind
moedict.tw. It's a national reference work rather than a live corpus, so an occasional sync is
plenty -- no submodule, and no network access at query time.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path


REPO = 'g0v/moedict-data-twblg'
FILES = ['dict-twblg.json', 'dict-twblg-ext.json']

# The local copy lives outside the skill directory, which gets replaced wholesale on update and
# isn't guaranteed writable. ~/.local/share is the XDG default and the convention CLI tools follow
# on macOS too, so one fallback covers both platforms.
DATA_HOME = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
OUTPUT_DIR = DATA_HOME / 'translating-taiwanese'
LOOKUP_FILE = OUTPUT_DIR / 'twblg_lookup.json'
META_FILE = OUTPUT_DIR / '_meta.json'


# TODO: fuzzy query using homophone if no terms found
def lookup(term: str) -> list[str]:
    """Look up Taiwanese -> Mandarin. Empty list if the term isn't in the dictionary."""
    return _load_lookup().get(term, [])


@lru_cache(maxsize=1)
def _load_lookup() -> dict[str, list[str]]:
    """Read the flattened {term: [candidate, ...]} map, syncing it first if it's missing."""
    if not LOOKUP_FILE.exists():
        print(f'{LOOKUP_FILE} not found, syncing dictionary...', file=sys.stderr)
        n_terms = sync_lookup()
        print(f'Synced {n_terms} terms.', file=sys.stderr)

    with LOOKUP_FILE.open(encoding='utf-8') as f:
        return json.load(f)


def sync_lookup() -> int:
    """
    Download the dictionary to dictionary/twblg_lookup.json, plus dictionary/_meta.json
    (sync timestamp, terms count). Returns the number of terms written.
    """
    datasets = []
    for f in FILES:
        url = f'https://raw.githubusercontent.com/{REPO}/master/{f}'
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                datasets.append(json.loads(resp.read().decode('utf-8')))
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            raise RuntimeError(f'failed to sync {f} from {REPO}: {e}') from e

    terms = _build_lookup(datasets)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOOKUP_FILE.write_text(json.dumps(terms, ensure_ascii=False, indent=2), encoding='utf-8')
    META_FILE.write_text(
        json.dumps(
            {
                'source_repo': REPO,
                'source_files': FILES,
                'ref': 'master',
                'synced_at': datetime.now().astimezone().isoformat(),
                'term_count': len(terms),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding='utf-8',
    )

    return len(terms)


# TODO: sanitize titles, e.g., "一粒米，百粒汗。" to "一粒米百粒汗"
def _build_lookup(datasets: list[list[dict]]) -> dict[str, list[str]]:
    """
    flatten the dictionary into a map of {term: [candidate, ...]}
    """
    terms: dict[str, list[str]] = defaultdict(list)

    for entries in datasets:
        for entry in entries:
            title = entry.get('title')
            if not title:
                continue

            if not (candidates := _candidates_for_entry(entry)):
                continue

            terms[title].extend(c for c in candidates if c and c not in terms[title])

    return terms


def _candidates_for_entry(entry: dict) -> list[str]:
    """
    Pull every plausible Mandarin candidate out of one dictionary entry across all of its
    heteronyms (pronunciation variants). Synonyms come first since they're closer to a direct
    term-for-term swap; definitions follow since they're explanatory rather than substitutable,
    but still useful context for picking the right sense.
    """

    def split_synonyms(raw: str) -> list[str]:
        return [s.strip() for s in re.split('[、,]', raw) if s.strip()]

    candidates: list[str] = []

    for heteronym in entry.get('heteronyms', []):
        synonyms = heteronym.get('synonyms')
        if isinstance(synonyms, str):
            candidates.extend(split_synonyms(synonyms))
        elif isinstance(synonyms, list):
            for s in synonyms:
                candidates.extend(split_synonyms(s))

        for definition in heteronym.get('definitions', []):
            if def_text := definition.get('def'):
                candidates.append(def_text.strip())

    return candidates
