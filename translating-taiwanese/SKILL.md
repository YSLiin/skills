---
name: translating-taiwanese
description: >-
  Translate Taiwanese (台語) into natural Mandarin, glossing every term against the MOE dictionary
  before composing. Use when the user shares Taiwanese/Hokkien text — lyrics, an article, or a line
  of speech — and wants it rendered in Mandarin.
---

# Translating Taiwanese

Machine translation for Taiwanese is thin, and a bare pass produces fluent-sounding Mandarin that
quietly gets specific terms wrong — idioms, colloquialisms, cultural references. So split the work.
`gloss.py` reports what the dictionary knows and guesses nothing; you supply the judgment and the
fluency. Neither half works alone: the gloss cannot pick a sense, and you cannot recall vocabulary
you have never seen.

## 1. Gloss the source

Run from this skill's `scripts/` directory, on the whole source text:

```bash
./gloss.py path/to/lyrics.txt  # file path
./gloss.py "無你我欲去佗位 我愛你毋但彼當時"  # inline
printf '%s' "$text" | ./gloss.py  # stdin
```

The first run downloads the dictionary (~2 MB, a few seconds). Pass `--build-dict` to refresh it.
Leave `--pretty` off — it is for humans reading the JSON, not for you.

Output is a flat JSON map, `term -> [candidate, ...]`:

```json
{
  "心":   ["人體器官之一", "思想、意念。", "心地、心性。"],
  "心悶": ["形容內心愁苦煩悶的狀態", "思念、想念之意"],
  "悶":   ["心中不愉快", "不暢快的心緒。"]
}
```

Three things about that map govern how you read it:

- **It is a menu, not a segmentation.** Every substring the dictionary knows is listed, so `心`,
  `心悶`, and `悶` all appear for one phrase. Segmenting is your job. Reach for the longer term
  first — that is how compounds and idioms land whole — but treat length as a default, not a rule:
  `無才調` (to be unable to) offers both `無才` and `才調`, and only `無` + `才調` reads. Take the
  split whose pieces make one coherent phrase. Whitespace bounds a term, so a phrase the source
  broke across a space arrives as two lookups.
- **Candidates run synonyms first, then definitions.** A synonym (`溫馴`, `思念`) is a word you can
  substitute; a definition (`形容內心愁苦煩悶的狀態。`) explains a sense in dictionary prose. Read
  a definition for its sense and write the Mandarin yourself.
- **A single character mapped only to itself is absent from the dictionary.** Translate it — and
  everything else the gloss missed, such as function words, names and loanwords — from your own
  knowledge of the pair.

Done when the gloss covers every line the user gave you.

## 2. Compose the Mandarin

Write the translation from the source text and the gloss together. One principle governs all of it:
**be creative in the Mandarin, faithful to the original.** Every image, every beat, every blunt or
ugly word the source chose is a choice you carry across. Your invention goes into _how_ it lands in
Mandarin; _what_ gets said stays the source's.

- **Keep the source's shape.** Verse for verse, line for line, and its spaces and punctuation where
  it put them — including where it used none. In lyrics a mid-line space is a breath and a bare
  line end is a held note; reproduce both.
- **Read the register off the text itself, and off the user.** What follows are illustrations of
  the kind of judgment to make, not a taxonomy to sort into. The source's own texture decides, and
  anything the user tells you about tone overrides all of it.
  - An _article_ tracks whatever it is: plain and simple for something shaped like a fable,
    composed and written for something shaped like a news report.
  - _Song lyrics_ come out sung rather than written — loose, rhythmic, a little raw, singable,
    colloquial where the source is colloquial, swaggering where it swaggers.
  - _Emotional punctuation_ (`！`, `？`, `⋯`, repetition, a trailing 啦／喔／齁) asks for speech:
    the particles and the breath a speaker would use.
  - Text sending none of these signals stays neutral and plain.
- **Choose each candidate against its context.** Position in the list carries no weight.
- **Rephrase where Mandarin runs out.** Taiwanese is a distinct language, and some of it has no
  Mandarin word waiting — when the gloss offers a definition and no synonym, spend a phrase to
  carry the sense rather than forcing a near-miss single word. Where Mandarin does have the term,
  keep the source's own wording.

Done when every line of the source has its Mandarin counterpart, the spacing and punctuation match
the source, and each candidate you picked was picked against context.

## 3. Deliver

Give the translation first. Then, briefly and only where it earns the space, flag the places a
reader would want to know about: a term genuinely ambiguous even in context, a cultural reference
that does not map cleanly, a span you translated without dictionary support.
