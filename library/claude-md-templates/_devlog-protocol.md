## Dev log protocol (read this BEFORE writing any code)

This project keeps an append-only **dev log** in `.claude/devlog/`. The dev log is the source of truth for what has actually been built, tested, and verified in this repo. It survives session boundaries — every fresh Claude session must read it before doing anything else.

### Layout

```
.claude/devlog/
├── DEVLOG.md             # index — newest entry on top
└── chunks/
    ├── 0001-<slug>.md
    ├── 0002-<slug>.md
    └── ...
```

### Read protocol (start of every session)

At the start of every session, before reading any source code or proposing any work:

1. Read `.claude/devlog/DEVLOG.md` end to end.
2. Read the **last 3 chunk files** in `.claude/devlog/chunks/` — they describe the most recent work.
3. Cross-check: do the files claimed in those entries actually exist? If not, flag the discrepancy to the user instead of trusting the log blindly.
4. Only after that, ask the user what they want to work on next.

### Write protocol (after every passing chunk)

A "chunk" is one verified slice of work — typically one feature, endpoint, component, migration, or refactor. **Do not write a devlog entry for a chunk until at least one verification gate (from `CLAUDE.md` → Verification gates) has passed.**

After a chunk passes:

1. Pick the next sequential chunk number (e.g. `0007`).
2. Create `.claude/devlog/chunks/0007-<short-slug>.md` with this structure:

```markdown
# 0007 — <short title>

**Date**: YYYY-MM-DD
**Status**: completed
**Verification**: <which gate(s) passed and how — e.g. "pnpm typecheck ✓ ; curl /health → 200 ✓">

## What was built
- <bullet list of the user-facing outcome>

## Files touched
- `path/to/file.ts` (created | modified | deleted)
- `path/to/other.tsx` (modified)

## Key decisions
- <any non-obvious choice made and why>

## Gotchas / things future-Claude must NOT assume
- <e.g. "the /api/users endpoint is auth-gated; calling it without a session cookie returns 401, not 403">
- <e.g. "we deferred X to chunk 0010">

## Tests added
- `tests/foo.test.ts` — covers <case>

## Open questions / TODOs
- <left for the next chunk>
```

3. Append a one-line entry at the **top** of `.claude/devlog/DEVLOG.md` (newest first):

```markdown
- `0007` (YYYY-MM-DD) — <short title>. Verified: <one-word gate>. See `chunks/0007-<slug>.md`.
```

4. Commit the devlog entry **with** the code change in the same commit. The devlog is part of the change, not a side-effect.

### Rules

- **Append-only.** Never edit a past chunk file to "fix" it. If you discover a past entry was wrong, write a new chunk that supersedes it and reference the old one.
- **One chunk = one entry.** Don't batch.
- **Don't lie.** If verification didn't fully pass, mark `Status: partial` with what's missing. Future sessions need to trust the log.
- **No secrets in the log.** Never paste env values, tokens, or credentials. Reference the env var name only.
- **No essays.** Each entry should be readable in under 60 seconds. Bullets > paragraphs.

### Why this exists

A future Claude session has no memory of this conversation. Without the devlog, it would have to re-derive everything from the code — and would inevitably hallucinate (assume a function exists that doesn't, miss a constraint that's not in the code but was a real decision). The devlog turns volatile session memory into durable project memory.
