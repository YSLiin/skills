# translating-taiwanese

A Claude skill for translating Taiwanese into natural Mandarin.

Machine translation for Taiwanese is thin, and a bare LLM pass produces fluent-sounding Mandarin
that quietly gets specific terms wrong. The skill splits the job in two:

- [`scripts/gloss.py`](scripts/gloss.py) looks every term in the source up against the MOE
  dictionary and reports the candidates without guessing, and
- the model picks the sense and writes the Mandarin.

## Why "Taiwanese" and not "Hokkien"

Both names point at the same language here, and the skill answers to either. It leads with
**Taiwanese** because that is what speakers in Taiwan call it, because the dictionary behind it is
Taiwan's own — the Ministry of Education's 臺灣閩南語常用詞辭典 — and because `tt` is a nicer
abbreviation than the alternatives.

The academic name might be *Taiwanese Hokkien*, and the distinction matters if you came here from
elsewhere: Taiwanese is the variety of Hokkien spoken in Taiwan, and it has diverged from the
varieties spoken in Fujian, Penang, Medan or Singapore in vocabulary, loanwords and some grammar —
roughly the way Mexican and peninsular Spanish have diverged. The glosses this skill produces are
Taiwan's. Expect misses on terms specific to another Hokkien-speaking region.

## Install

Just this skill:

```bash
npx skills add YSLiin/skills/translating-taiwanese
```

Or the whole collection it lives in:

```bash
npx skills add YSLiin/skills
```

Either way, paste Taiwanese text into a conversation afterwards — the skill triggers on its own —
or invoke it by name. Cloning the directory into your skills folder (`~/.claude/skills/` for a
personal skill) works just as well.

## Use

The glosser also stands alone as a CLI, with or without an agent:

```bash
cd scripts && ./gloss.py "心悶你溫柔的聲" --pretty
```

It takes a file path, inline text, or stdin, and prints `{term: [candidate, ...]}` as JSON —
`--pretty` indents it for reading. The first run downloads the dictionary; `--build-dict` refreshes
it afterwards. Nothing else touches the network.

## Customization

**Swapping the dictionary.** [`scripts/dictionary.py`](scripts/dictionary.py) exposes exactly two
functions to the rest of the skill: `sync_lookup()` rebuilds the local copy, and `lookup(term)`
returns a term's candidates. Reimplement those two and everything else — a different corpus, a
database, a remote API — drops in unchanged. The current pair pulls two flat JSON files from
[g0v/moedict-data-twblg](https://github.com/g0v/moedict-data-twblg), which republishes the MOE
dictionary (~20,000 terms, a few MB) with no network access needed at query time.

**Where the data lives.** `$XDG_DATA_HOME/translating-taiwanese`, falling back to
`~/.local/share/translating-taiwanese` — outside the skill directory, which gets replaced wholesale
on update and is not guaranteed writable. `_meta.json` alongside it records the source and sync time.

**Tuning the translation itself.** The candidate list is built by `_candidates_for_entry()`, which
takes synonyms before definitions from every heteronym of an entry; narrow or widen it there. How
the model writes is governed by step 2 of [`SKILL.md`](SKILL.md), which carries a register table
(article / lyrics / plain prose / oral) — that is the place to add house style or a target variety
of Mandarin.
