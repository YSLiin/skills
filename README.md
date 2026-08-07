# skills

Agent skills, split by who they are for.

| | |
| --- | --- |
| [`daily/`](daily/) | Everyday use. No terminal required beyond the install. |
| `dev/` | Technical work — coding, tooling, repo workflows. |

## Skills

| Skill | What it does |
| --- | --- |
| [`daily/translating-taiwanese`](daily/translating-taiwanese) | Translates Taiwanese (台語) into natural Mandarin, glossing every term against the MOE dictionary first. |

## Install

The whole collection:

```bash
npx skills add YSLiin/skills
```

Or one skill by name:

```bash
npx skills add YSLiin/skills --skill translating-taiwanese
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

## License

[MIT](LICENSE), covering the code and documentation here. Skills that rely on third-party data
carry that data's terms and attribution in their own README, so it travels with the installed skill.
