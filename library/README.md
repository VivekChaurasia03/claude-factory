# `library/` — Tag Taxonomy & Authoring Guide

Every file in `library/agents/`, `library/skills/`, and `library/commands/` declares an `applies_to:` list in its frontmatter. **These tags are hints to Claude, not hard filters.** When `/factory` runs, Claude reads each candidate file's body and decides — using judgment — whether it belongs in the output. Tags shape the first-pass shortlist; bodies decide the final cut.

A useful first-pass rule of thumb: a file is a candidate iff its `applies_to` list contains `*` or any tag in the project's manifest. Claude can include outside that set when the file is genuinely useful, and exclude inside it when redundant.

The special tag `"*"` means **strong default — almost always include** (e.g. `code-reviewer`, `architect`, `planner`, `security-review`). Claude can still skip a `*` file if it would clutter the output.

---

## Tag taxonomy

Tags are flat strings of the form `category:value`. The interview maps the user's answers into this tag set. Adding new tags is fine — just keep them within the categories below or add a new category here.

### `lang:`  (programming language)
`lang:python`, `lang:node`, `lang:typescript`, `lang:javascript`, `lang:go`, `lang:rust`, `lang:java`, `lang:kotlin`, `lang:swift`, `lang:csharp`, `lang:ruby`, `lang:php`, `lang:elixir`

### `framework:`  (application framework)
**Backend**: `framework:fastapi`, `framework:django`, `framework:flask`, `framework:starlette`, `framework:express`, `framework:nestjs`, `framework:fastify`, `framework:hono`, `framework:koa`, `framework:gin`, `framework:echo`, `framework:fiber`, `framework:axum`, `framework:actix`, `framework:rocket`, `framework:spring-boot`, `framework:rails`, `framework:laravel`, `framework:phoenix`

**Frontend**: `framework:next`, `framework:nuxt`, `framework:remix`, `framework:react`, `framework:vue`, `framework:svelte`, `framework:sveltekit`, `framework:astro`, `framework:solid`, `framework:react-native`, `framework:expo`, `framework:flutter`

### `db:`  (databases)
**Primary (OLTP)**: `db:postgres`, `db:mysql`, `db:sqlite`, `db:mongodb`, `db:dynamodb`, `db:cosmosdb`
**Analytical (OLAP)**: `db:clickhouse`, `db:bigquery`, `db:snowflake`, `db:redshift`, `db:duckdb`
**Search/Vector**: `db:elasticsearch`, `db:meilisearch`, `db:pinecone`, `db:weaviate`, `db:qdrant`

### `cache:`
`cache:redis`, `cache:memcached`, `cache:dragonfly`

### `queue:`
`queue:kafka`, `queue:rabbitmq`, `queue:sqs`, `queue:redis-streams`, `queue:nats`, `queue:pubsub`

### `orm:`
`orm:prisma`, `orm:drizzle`, `orm:sqlalchemy`, `orm:typeorm`, `orm:sequelize`, `orm:gorm`, `orm:diesel`, `orm:django-orm`

### `auth:`
`auth:jwt`, `auth:oauth`, `auth:clerk`, `auth:auth0`, `auth:supabase-auth`, `auth:nextauth`, `auth:firebase-auth`

### `infra:`
`infra:docker`, `infra:docker-compose`, `infra:kubernetes`, `infra:serverless`, `infra:bare-vm`, `infra:edge`

### `deploy:`  (deployment target)
`deploy:vercel`, `deploy:netlify`, `deploy:railway`, `deploy:fly`, `deploy:render`, `deploy:cloudflare`, `deploy:aws`, `deploy:gcp`, `deploy:azure`, `deploy:digitalocean`, `deploy:self-hosted`, `deploy:free-tier`

### `ci:`
`ci:github-actions`, `ci:gitlab`, `ci:circleci`, `ci:buildkite`

### `pm:`  (package manager)
`pm:npm`, `pm:pnpm`, `pm:yarn`, `pm:bun`, `pm:pip`, `pm:poetry`, `pm:uv`, `pm:cargo`, `pm:go-mod`, `pm:maven`, `pm:gradle`

### `test:`
`test:pytest`, `test:jest`, `test:vitest`, `test:playwright`, `test:cypress`, `test:go-test`, `test:cargo-test`, `test:junit`

### `repo:`  (repo layout)
`repo:single`, `repo:monorepo`, `repo:library`, `repo:cli`

### `role:`  (what this codebase does)
`role:frontend`, `role:backend`, `role:fullstack`, `role:cli`, `role:library`, `role:data-pipeline`, `role:ml`

### `has:`  (capabilities present)
`has:api`, `has:database`, `has:auth`, `has:tests`, `has:realtime`, `has:background-jobs`, `has:file-uploads`, `has:payments`

### `*`  (universal)
Always included.

---

## Authoring rules

1. **Frontmatter is required** for every file. Missing `applies_to` = Claude won't shortlist the file.
2. **Be conservative** — if a skill might confuse Claude in projects where it doesn't apply, narrow the tags. Better to under-include than to drown the generated repo in noise.
3. **One concept per file** — don't bundle "Python + Postgres" patterns into one file with `applies_to: [lang:python, db:postgres]`. Tag matching is OR-style at the shortlist stage, so this would surface the file for Python-only OR Postgres-only projects too. Split into two.
4. **Universal tag (`*`) is rare** — reserve it for things every project benefits from (architect, code-reviewer, planner, basic security review).
5. **Bodies must be self-contained.** Claude adapts each chosen file by substituting project-specific values into the body. Make sure the file makes sense when read in isolation by a future Claude session.

---

## Skill authoring

Skills live in `library/skills/<skill-name>/SKILL.md` (with optional sibling files in the same directory). The generator copies the entire skill directory.

```yaml
---
name: my-skill
description: <one-line activation hint>
applies_to: [tag1, tag2]
---

# Skill body
```

## Agent authoring

Agents live in `library/agents/<agent-name>.md`.

```yaml
---
name: my-agent
description: <one-line>
tools: ["Read", "Edit", ...]
model: sonnet
applies_to: [tag1, tag2]
---

# Agent body
```

## Command authoring

Commands live in `library/commands/<command>.md`.

```yaml
---
name: my-command
description: <one-line>
applies_to: [tag1]
---

# Command body
```
