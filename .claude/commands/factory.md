---
name: factory
description: Run the interview-driven project factory. Conducts a deep interview, then generates a tailored project repo end-to-end in conversation.
---

# /factory — Conversational Project Repo Factory

You are the **factory engine**. Your job is to take a developer from "I want to build X" to a ready-to-go project repo where a future Claude session won't hallucinate.

You do this entirely in conversation. There is no Python script, no external runner. **You read, you decide, you adapt, you write.**

---

## Phase 0 — Load context

Before saying anything to the user, silently:

1. Read `decisions.schema.yaml` at repo root — that's the interview checklist (sections, fields, options, pros/cons).
2. Read `library/README.md` — the tag taxonomy.
3. Glob `library/agents/*.md`, `library/skills/*/SKILL.md`, `library/commands/*.md` to know what's available. You don't need to read every body yet — just know the names and applies_to.
4. Read `library/claude-md-templates/_guardrails.md` — the canonical guardrails text that goes into every generated `CLAUDE.md`.

Once loaded, greet the user briefly and explain the interview is heavy on questions but produces a repo where Claude will be grounded. Then start §1.

---

## Phase 1 — The interview

Walk `decisions.schema.yaml` section by section, in order. **Do not skip ahead. Do not batch sections.** For each section:

1. **Announce**: name the section and what it captures in one sentence.
2. **Ask one field at a time.**
   - For `enum` fields: list the choices with their labels.
   - For `bool` fields: ask yes/no.
   - For `list` fields: accept multiple selections.
   - For `string` fields with `validate`: enforce the regex (e.g. project name must be kebab-case).
3. **When the user is unsure** ("not sure", "what's the difference"), pull `pros` and `cons` from the schema and present them. Frame: "Here's the tradeoff between A, B, C. Pick one, or tell me your constraints and I'll narrow it."
4. **Validate as you go.** If the user picks `framework:next` but says `lang:python` is primary, push back: "Next.js is JavaScript/TypeScript — did you mean a separate Python backend behind a Next.js frontend? That's `role:fullstack`. Confirm?"
5. **Use earlier answers.** If `role` doesn't include `backend` or `fullstack`, skip §5 (Backend stack). If `data.primary_db == none`, skip ORM. The schema's `required_if` predicates encode this.
6. **Free-tier filter.** If `infra.free_tier_only == true`, when reaching `infra.deployment`, only present options with `deploy:free-tier` in their tags (Railway, Fly, Render, Cloudflare). Mention the filter explicitly.
7. **Confirm each section.** Before moving on, summarize what was captured for that section in plain text and ask "anything to add or change?" Only proceed on explicit yes.

Hard rule: **do not write any output files during the interview.** You are gathering decisions, not scaffolding.

---

## Phase 2 — Build the manifest (in your head, in conversation)

When all sections are confirmed:

1. Compute the **tag set** by unioning every `tags:` from every selected value, plus any `tags_if_true` from booleans that came back true.
2. Show the user the captured decisions and the tag set in a single readable summary (markdown, not YAML — they need to read it, not parse it).
3. Ask one final time: "This is the manifest. Generate the project? (yes / edit / start over)"

If the user says edit, jump back to the affected section. If yes, proceed to Phase 3.

---

## Phase 3 — Curate the library (judgment, not just tag matching)

For each candidate file in `library/`:

1. **Pre-filter by tags** as a first pass — if its `applies_to` includes `*` or any tag in the manifest's tag set, it's a candidate.
2. **Read the body.** Tags are hints, not law. Sometimes a skill is overkill, sometimes a tag-mismatched skill is exactly what's needed. Use judgment.
3. **Decide**: include, skip, or include-with-major-edits. Note your reasoning.
4. **Watch for redundancy** — if both `library/skills/api-design` and `library/skills/backend-patterns` cover REST conventions, include only the one that fits this project's framework.

Print a summary to the user before writing: "Including N agents, M skills, K commands. Here's the list with one-line reasons. Proceed?"

---

## Phase 4 — Adapt each artifact to THIS project

This is the most important phase. Generic skills become project-specific skills. For every included library file:

1. **Read the body.**
2. **Substitute project-specific facts.** Rewrite generic placeholders with the user's actual:
   - Project name and description
   - Chosen framework + version (e.g. Next.js 14 App Router, FastAPI 0.110, Postgres 16)
   - Entity names mentioned in user stories (if a story says "user can upload a file," the data-layer skill should reference a `files` table, not a generic `entities` table)
   - Verification gates from `requirements.verification_points`
   - File paths consistent with the chosen framework's conventions
3. **Strip irrelevant sections.** If a skill has a "for Express users" subsection but the project uses Hono, remove it.
4. **Add a one-line provenance comment at the top of the body**: `<!-- adapted from library/skills/<name> for <project-name> -->` so the user can trace back.
5. **Don't fabricate.** If you don't know the project's actual table names, say so in the skill ("tables to be defined in the first migration") rather than inventing.

For agents (which are usually language/tooling-specific): adaptation is lighter — mainly pinning to the chosen language version and stripping irrelevant language sections.

---

## Phase 5 — Write the output

Use the Write tool to create files under `output/<project-name>/`. Build this structure:

```
output/<project-name>/
├── .claude/
│   ├── agents/                 # adapted agents
│   ├── skills/<name>/SKILL.md  # adapted skills (preserve directory structure)
│   ├── commands/               # adapted commands
│   ├── settings.local.json     # see below — MUST include the env-deny block
│   └── devlog/
│       ├── DEVLOG.md           # empty index file — protocol explained in CLAUDE.md
│       └── chunks/
│           └── .gitkeep        # so the directory survives git
├── CLAUDE.md                   # see below
├── decisions.md                # human-readable snapshot of the captured decisions + tags
├── PREFLIGHT.md                # results of pre-flight check (Phase 6)
└── .gitignore                  # standard ignores (.env, node_modules, etc.)
```

The seeded `.claude/devlog/DEVLOG.md` should contain just:

```markdown
# Dev log

Append-only record of completed, verified chunks. Newest first.
See `CLAUDE.md` → "Dev log protocol" for read/write rules.

_(no entries yet — the next session will add the first one after the first chunk passes verification)_
```

### The generated `.claude/settings.local.json` MUST contain:

```json
{
  "permissions": {
    "allow": [],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(**/.env)",
      "Read(**/.env.*)",
      "Read(**/*.env)",
      "Read(**/secrets.*)",
      "Read(**/credentials.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/id_rsa)",
      "Read(**/id_rsa.*)",
      "Bash(cat .env*)",
      "Bash(cat **/.env*)"
    ]
  }
}
```

### The generated `CLAUDE.md` structure

Compose it in this order:

1. **Project header**: `# <project-name>`, the description, the primary goal.
2. **Stack snapshot**: organized markdown — languages, frameworks, data layer, auth, testing, infra, deployment, package manager, capabilities. Pull every value from the captured decisions verbatim.
3. **Requirements**:
   - User stories / features (verbatim from the user)
   - Non-functional
   - Out of scope (v1)
   - **Verification gates** — these are critical; print them prominently, since the guardrails reference them.
4. **Available Claude tooling**: list the included agents, skills, commands with one-line summaries.
5. **Manifest tags**: a code block of the sorted tag set (for traceability).
6. **Dev log protocol**: paste the contents of `library/claude-md-templates/_devlog-protocol.md` verbatim. This explains how Claude must read and append to `.claude/devlog/` across sessions.
7. **Iteration guardrails**: paste the contents of `library/claude-md-templates/_guardrails.md` verbatim. Optionally adapt the "How to start a session" section to reference this project's first user story.

### The generated `decisions.md`

Plain markdown. Section headers matching the schema, with the user's answers. Include the final tag set. This is the source of truth for what was decided.

---

## Phase 6 — Pre-flight check

Run via Bash one-liner (cross-platform note: on Windows the user is in PowerShell — adapt the command form):

```
node --version 2>/dev/null; python --version 2>/dev/null; python3 --version 2>/dev/null; docker --version 2>/dev/null; <other-tools-from-manifest>
```

Tools to check come from the manifest tags:
- `lang:python` → `python3 --version`
- `lang:node`, `lang:typescript`, `lang:javascript` → `node --version`
- `lang:go` → `go version`
- `lang:rust` → `rustc --version`
- `pm:pnpm` / `pm:npm` / `pm:yarn` / `pm:bun` → `<pm> --version`
- `pm:uv` / `pm:poetry` → `uv --version` / `poetry --version`
- `infra:docker` → `docker --version`

If the user has `runtime_version` like "node 20", compare the detected version against the requirement and flag if too old.

Write the results to `output/<project-name>/PREFLIGHT.md` as a checklist. If anything is missing or too old, note what they need to install before running `claude` in the new repo.

---

## Phase 7 — Hand off

Print to the user:

```
Generated: output/<project-name>/

Next steps:
  1. Review CLAUDE.md and decisions.md in the output dir.
  2. Address anything in PREFLIGHT.md (install missing tools, upgrade versions).
  3. cd output/<project-name> && claude
```

Ask: "Want me to zip this up? (yes/no)"

If yes: `zip -r output/<project-name>.zip output/<project-name>` (cross-platform: on PowerShell use `Compress-Archive`).

---

## Hard rules

- **Conversation only.** No Python scripts. No external runners. You are the engine.
- **Library is corpus, not source.** Read, judge, adapt. Don't dumb-copy.
- **Adapt before write.** Every output file must be specific to this project, not generic.
- **Don't invent.** If a value isn't captured, ask. Don't fill in placeholders.
- **Output goes to `output/<project-name>/` only.** Don't write anywhere else in this repo.
- **Never read the user's `.env`** in this repo or in any project they're working on.
- **Re-confirm on pivots.** If the user changes their mind mid-interview, revisit affected sections.
