# skills

Agent skills, split by who they are for.

| | |
| --- | --- |
| [`daily/`](daily/) | Everyday use. No terminal required beyond the install. |
| [`dev/`](dev/) | Technical work — coding, tooling, repo workflows. |

## Skills

| Skill | What it does |
| --- | --- |
| [`daily/translate-taiwanese`](daily/translate-taiwanese) | Translates Taiwanese (台語) into natural Mandarin, glossing every term against the MOE dictionary first. |
| [`dev/read-code`](dev/read-code) | Answers one question about existing code: direct, factual, read-only, ending in `file:line` pointers. Invoke with `/read-code`. |
| [`dev/study-code`](dev/study-code) | Socratic mentor mode for studying a codebase. Stays on until you send `::wrap-up`. Invoke with `/study-code`. |

## Install

The whole collection:

```bash
npx skills add YSLiin/skills
```

Or one skill by name:

```bash
npx skills add YSLiin/skills --skill translate-taiwanese
```

## Layout rule

**Every skill lives under a category directory. Nothing sits at the repo root.**

This is load-bearing, and breaking it fails silently. The `skills` CLI scans a fixed list of
priority locations — the repo root, `skills/`, and a set of agent-specific paths — and only falls
back to a recursive search when that scan finds *nothing*. Category directories are not on the
list, so every skill here is found by the fallback.

Put one skill at the repo root and the priority scan succeeds, the fallback never runs, and every
categorized skill disappears from `npx skills add` with no error. `--skill` cannot rescue them
either, since it filters after discovery. Fully nested or fully flat — never mixed.

## Shared rule blocks

`read-code` and `study-code` each install on their own, so the reading rules they share are
copied into both, between `<!-- shared:begin -->` and `<!-- shared:end -->`. The two blocks must
stay byte-identical: edit one, copy it to the other.

`scripts/check-shared.sh` diffs them (`--staged` checks the index instead of the working tree).
A [lefthook](https://github.com/evilmartians/lefthook) pre-commit hook runs it whenever either
SKILL.md is staged. Enable it once per clone:

```bash
lefthook install
```

## License

[MIT](LICENSE), covering the code and documentation here. Skills that rely on third-party data
carry that data's terms and attribution in their own README, so it travels with the installed skill.
