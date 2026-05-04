# Claude Repo Factory

This repo is a **conversation-driven project generator**. It has one purpose: when a developer is starting a new project, they run `/factory` here, Claude conducts a deep interview, and Claude itself produces a tailored project repo where Claude (running inside the *new* repo) won't hallucinate — every decision is captured, every included skill is adapted to the project, and iteration guardrails are baked into the generated `CLAUDE.md`.

**The factory is Claude. There is no Python script, no CLI tool, no external runner.** The `library/` is a corpus Claude reads from and *adapts*. It is not a static set of files to copy.

---

## How to use it

From inside this repo, in Claude Code:

```
/factory
```

The slash command instructs Claude to:

1. Read `decisions.schema.yaml` (the interview checklist) and `library/README.md` (the tag taxonomy).
2. Walk the user through the interview section by section. Gate each section. When the user is unsure, surface options with pros/cons.
3. Cross-reference earlier answers (e.g. don't ask backend questions if `role` is `frontend` only).
4. When the interview is done, scan `library/` and decide — using judgment, not just tag matching — which agents/skills/commands belong in the output repo.
5. **Adapt** each chosen artifact to this specific project: substitute the project's actual entity names, framework version, deploy target, file paths, and verification gates into the skill body.
6. Write the entire output directory directly using the Write tool: `output/<project-name>/.claude/...` plus a project-specific `CLAUDE.md`, `decisions.md` snapshot, and `PREFLIGHT.md`.
7. Run a Bash one-liner pre-flight check (`node -v`, `python --version`, `docker --version`, etc.) and surface results.
8. Optionally zip the output: `zip -r output/<project-name>.zip output/<project-name>`.

The user then drops the output into a fresh project, runs `claude`, and starts building. Claude reads the generated `CLAUDE.md` and is up-to-speed.

---

## Repo layout

```
.
├── CLAUDE.md                       # this file
├── .claude/
│   ├── commands/factory.md         # the conversational /factory command
│   └── settings.local.json
├── decisions.schema.yaml           # interview checklist (Claude reads this; no code parses it)
└── library/                        # corpus Claude learns from
    ├── README.md                   # tag taxonomy + authoring guide
    ├── agents/                     # agent definitions w/ applies_to hints
    ├── skills/                     # skill packages w/ applies_to hints
    ├── commands/                   # slash commands w/ applies_to hints
    └── claude-md-templates/        # composable CLAUDE.md fragments (esp. _guardrails.md)
```

---

## Iteration guardrails (baked into every generated `CLAUDE.md`)

These rules MUST appear in every output project's `CLAUDE.md`. They exist to prevent hallucination:

1. **Verify before next** — do not advance past a chunk until it's verified (typecheck, run, test, or render).
2. **Small chunks** — each slice ≤ ~5 files, ~150 lines; otherwise propose the breakdown and get approval first.
3. **No code dumps** — no multi-file scaffolding without stating intent and getting confirmation.
4. **No hallucination** — only reference functions/files/flags that exist in the repo or are listed in the captured decisions.
5. **Use the captured decisions** — don't introduce stacks/frameworks/databases not in the manifest.
6. **Local is a lie — think production** — race conditions, partial failures, idempotency.
7. **Never let a deadline slip silently** — surface delays early.
8. **Never read `.env` / secrets** — `.env`, `.env.*`, `secrets.*`, `credentials.*`, `*.pem`, `*.key`, `id_rsa*` are off-limits. Read the `.example` instead and ask the user for real values.

The full canonical text lives in `library/claude-md-templates/_guardrails.md`. Always include it (verbatim or adapted) in the generated `CLAUDE.md`.

---

## How the library evolves

The library is the factory's accumulated knowledge. To grow it:

- Drop a new agent/skill/command into the right `library/` subdirectory.
- Add an `applies_to:` list in its frontmatter (see `library/README.md` for tags). Treat it as a *hint* to Claude — Claude reads bodies and uses judgment when deciding inclusion.
- Real-project feedback is the main lever: when something is missing or wrong in a generated repo, fix it in `library/` so the next generation is sharper.

There is no automatic sync from external sources. Curation is intentional.
