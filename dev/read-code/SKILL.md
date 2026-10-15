---
name: read-code
description: >-
  Answer one question about existing code: a direct, factual, read-only lookup that ends with
  file:line pointers. Invoke explicitly with /read-code.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

# Read code

`/read-code` is a manual lookup: one question in, one factual answer out. It is a single
**transaction**. These rules govern the reply to this invocation only. Afterwards the session
returns to whatever it was doing, and that includes resuming an active `/study-code` session.

## The answer

- Answer the question directly, at the depth the code supports.
- When a question has more than one plausible reading, answer the most probable factual one. The
  other reading goes in the closing as an escape hatch ("if you meant the write path, it starts at
  `flush.go:40`").
- The transaction is read-only from start to finish. If a write request comes bundled with the
  question ("…and fix it"), answer the question, and use one closing pointer to say the fix was
  skipped and should be asked again outside `/read-code`.
- At a dependency boundary (framework, third-party library, stdlib), stop and state the
  contract: what it is called with and what it promises back. Go inside only when asked.
- Draw a diagram only when the question asks for one.

## The closing

End with 1–2 factual pointers to where to look next: "The interface is in `types.go:12`; the main
implementation is `redis_store.go:40`." Write them as statements. A `/read-code` reply asks the
user nothing.

<!-- shared:begin -->
## Reading rules

### Trace the thread

Follow one thread of execution from its trigger to its effect, citing `file:line` at each hop. A
file is a stop along a thread, so describe what the thread does there rather than summarizing the
file from top to bottom.

When asked what a file does, the body has exactly three parts:

1. Its responsibility or contract, in one sentence.
2. Its public entry points, as bullets.
3. The state it owns, or the external systems it mutates.

Leave out private helpers, imports, and boilerplate. The closing follows as usual.

### Peripheral code

What counts as peripheral depends on the question. Observability, marshalling, framework
boilerplate, defensive branches, and transparent optimizations get one clause ("marshals the
payload") or nothing. The exception is when they are the subject, for example when studying the
tracing setup or admiring a zero-allocation parser.

### Budget

Lead with the answer and stop early. Prose, including the closing, stays under 250 words. Code
blocks, diagrams, and terminal output don't count toward that. When a diagram is drawn, prose
drops under 100 words, because the diagram replaces the explanation.

### Diagrams

Use Mermaid, with at most 10 nodes or participants, drawn at architectural boundaries rather than
one box per function call. Use `sequenceDiagram` for request lifecycles and handoffs between
actors, and `graph TD` for branching logic and state machines.

### Bugs

A bug gets one ⚠ line only when it sits on the traced path *and* fails at runtime: a panic, a
race, an unhandled exception. Style, lint, and logic outside the question go unmentioned. A
flagged bug stays a flag: fixes and fix plans wait until the user asks.

### History

Code tells you what. History tells you why, but only ask why if the what makes no sense. Reach for
git on exactly two triggers:

- **Irrationality**: a magic number or workaround that the surrounding code doesn't explain.
- **Regression**: the user asks when it changed, who wrote it, or why it changed.

Otherwise explain intent from the code itself, and label it as inference ("the structure
suggests…").

Escalate lazily, and stop the moment the intent is found:

1. `git blame` on the confusing lines only.
2. `git log -1 <commit>` for that commit's message.
3. `git log -S` / `--grep` to find where a snippet or keyword entered the history.
4. `gh pr view` / `gh issue view` when a commit message cites a number.

Report what the code does and what the history says, citing the hash, date, author, and PR or
issue number so the user can follow up. When the history is vague or contradictory, say so, and
leave the theory unwritten.

### Tools

Prefer the built-in read and search tools. Only these shell signatures are pre-cleared:

```
rg -n -C <N> <pattern> [path]
find <path> -name <glob> -type <f|d>
git blame -w -M -C -L <start>,<end> <file>
git log -<N> [<commit>]
git log [-<N>] -S "<keyword>"
git log [-<N>] --grep "<keyword>"
git show --stat <commit>
gh auth status
gh pr view <number>
gh issue view <number>
```

Run `gh auth status` once, silently, before the first `gh` call. If it fails, fall back to
`git log --grep`.

**Permission gate.** For any other command you decide to run (an unlisted binary or flag, a
complex argument, a pipeline, a redirect), stop first. Print the exact command in a code block,
say why it's needed, and wait for the user's explicit yes.
<!-- shared:end -->
