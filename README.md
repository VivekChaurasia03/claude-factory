# Claude Repo Factory

A **conversation-driven project generator** that produces ready-to-go repos where Claude Code won't hallucinate.

You open this repo in Claude Code, run `/factory`, and Claude conducts a thorough interview about the project you want to build — language, frameworks, database, deployment, user stories, verification gates, everything. When the interview is done, Claude produces a tailored output repo for you. That output repo contains:

- A project-specific `CLAUDE.md` with your stack, requirements, and verification gates baked in
- A curated `.claude/` directory with only the agents/skills/commands relevant to your project — adapted, not just copied, to reference your actual entity names and framework choices
- An append-only **dev log** (`.claude/devlog/`) that Claude reads at the start of every future session to know exactly what's been built and verified
- Hard `deny:` rules so Claude can never read `.env` files
- Iteration guardrails: verify-before-next, small chunks, no code dumps, no hallucination

You drop the output into a fresh project, run `claude` inside it, and start building. The Claude session is up-to-speed from the first message.

---

## Why this exists

Starting a new project with Claude Code usually means one of two failure modes:

1. **Cold start** — Claude has no project context, makes assumptions, hallucinates frameworks/files/functions that aren't there.
2. **Over-eager scaffolding** — Claude dumps multi-file scaffolds in one shot before you've reviewed anything.

The factory solves both: a deep interview captures every decision *before* code is written, and the generated `CLAUDE.md` contains hard guardrails (verify each chunk before the next, no scaffolds without confirmation, never fabricate). The dev log keeps that grounding intact across sessions.

---

## Repo layout

```
.
├── README.md                           # this file
├── CLAUDE.md                           # how Claude operates inside the factory itself
├── .claude/
│   ├── commands/factory.md             # the /factory slash command (interview + generation)
│   └── settings.local.json
├── decisions.schema.yaml               # the interview checklist (Claude reads it; nothing parses it)
└── library/                            # corpus Claude learns from when generating
    ├── README.md                       # tag taxonomy + authoring guide
    ├── agents/                         # 32 adaptable agent definitions
    ├── skills/                         # 51 adaptable skill packages
    ├── commands/                       # 5 adaptable slash commands
    └── claude-md-templates/
        ├── _guardrails.md              # iteration rules baked into every output CLAUDE.md
        └── _devlog-protocol.md         # devlog read/write protocol baked into every output
```

---

## How to use it

### 1. Clone this repo

```bash
git clone https://github.com/<you>/claude-repo-factory
cd claude-repo-factory
```

### 2. Open it in Claude Code

```bash
claude
```

### 3. Run the factory

```
/factory
```

Claude will:

1. Read the schema and library
2. Walk you through the interview, section by section, with pros/cons when you're unsure
3. Show you the captured decisions and tag set
4. Curate the library — judgment-based, not just tag matching
5. **Adapt** each chosen artifact to your project (substituting your entity names, framework version, deploy target, etc.)
6. Write the entire output repo into `output/<project-name>/`
7. Run a pre-flight check on your machine (right tool versions installed?)
8. Optionally zip it

### 4. Use the generated repo

```bash
cd output/<project-name>
claude
```

Claude reads your project-specific `CLAUDE.md` + `decisions.md` + `.claude/devlog/` and is immediately oriented. No re-explanation of stack, conventions, or what's been built.

---

## What the dev log gives you

Every chunk of work that passes verification gets logged in `.claude/devlog/chunks/NNNN-<slug>.md`:

- What was built
- Files touched
- Key decisions (with the *why*)
- Gotchas future-Claude must NOT assume
- Tests added
- Open questions / TODOs

A one-line index lives in `.claude/devlog/DEVLOG.md`. At the start of every new session, Claude reads it and the most recent entries before doing anything else. Session memory becomes durable project memory.

The protocol is committed to git alongside code, so it survives switching machines, losing sessions, or handing the repo to a teammate.

---

## How the library evolves

The `library/` is the factory's accumulated knowledge. To grow it:

- Drop a new file into `library/agents/`, `library/skills/<name>/SKILL.md`, or `library/commands/`.
- Add an `applies_to:` list in the frontmatter (see `library/README.md` for the tag taxonomy).
- Tags are *hints* to Claude — Claude reads bodies and uses judgment when deciding what to include.
- Real-project feedback is the main lever: when something is missing or wrong in a generated repo, fix it in `library/` so the next generation is sharper.

There is no automatic sync from external sources. Curation is intentional.

---

## Status

Early-stage. Recent milestones:

- ✅ Core interview schema (`decisions.schema.yaml`) covering 13 sections of project decisions
- ✅ Library seeded from `affaan-m/everything-claude-code` (curated, tagged)
- ✅ Hard `.env` / secrets deny rules baked into every generated repo
- ✅ Iteration guardrails (verify-before-next, no code dumps, no hallucination)
- ✅ Dev log protocol (durable cross-session project memory)
- ✅ Conversational `/factory` (no Python pipeline; Claude does the entire flow)

Open work:
- Adaptation rulebook (how Claude rewrites generic skills for a specific project)
- First real-project run + feedback loop
- Library quality grading (which seeded skills are gold vs. noise)
- "Remix from past project" path
- Cross-platform validation (PowerShell on Windows)

---

## Philosophy

The factory is **Claude**, not a CLI tool. There is no Python runner, no external generator. Claude reads, judges, adapts, and writes. The library is a corpus to learn from, not a static set of files to copy. This keeps the factory's output specific to each project rather than generic — which is the only way the anti-hallucination promise actually holds.
