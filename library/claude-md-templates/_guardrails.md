## Iteration guardrails (non-negotiable)

These rules apply to every chunk of work in this repo. They were baked in by the Claude Repo Factory and are not project-specific opinions — they are the operating contract.

### 1. Verify before next
Do not advance to the next chunk until the current chunk is verified by at least one of the gates listed in **Verification gates** above. Examples of valid verification:
- Typecheck passes (`tsc --noEmit`, `mypy`, `cargo check`)
- The new endpoint returns the expected response when curled
- The unit test passes locally
- The page renders correctly in the browser

If you cannot verify, **stop and tell the user** rather than continuing with assumed correctness.

### 2. Small chunks
Implement in slices small enough that the user can review each one in under ~2 minutes. A "chunk" is roughly one of:
- One endpoint
- One component
- One migration
- One config change + the code that reads it

If a slice would touch more than ~5 files or ~150 lines, **stop, propose the breakdown, and get user approval** before continuing.

### 3. No code dumps
Never emit a multi-file scaffold without first stating the intent in 2-3 sentences and getting confirmation. The user explicitly asked for chunked, verified development — code dumps violate that contract.

### 4. No hallucination
Only reference functions, files, libraries, flags, or environment variables that:
- Exist in this repo (verify with Read or Grep before referencing), OR
- Are explicitly listed in `decisions.yaml`

If you need something that doesn't yet exist, **announce that you're about to create it**, and get a yes before creating.

### 5. Use the captured decisions
`decisions.yaml` (in this directory) is the contract. Do not introduce languages, frameworks, databases, or deployment targets that are not in the manifest. If the user asks for something outside the manifest, surface the conflict — don't silently expand scope.

### 6. Local is a lie — think production
Wherever the code runs concurrently in production (workers, request handlers, distributed jobs), think about race conditions, partial failures, and idempotency. "Works on my machine in a single process" is not a valid stopping point.

### 7. Never let a deadline slip silently
If a chunk is going to take significantly longer than expected, surface it early. Don't disappear into a long tool sequence — interrupt yourself and tell the user.

### 8. Never read `.env` files
You MUST NOT Read, Grep, or otherwise open any `.env`, `.env.*`, `*.env`, `secrets.*`, `credentials.*`, or `*.pem` / `*.key` file in this repo. These files contain secrets that the user does not want loaded into the model context.
- If you need a configuration value, read its **example** file (`.env.example`, `.env.template`) and ask the user for the real value instead of reading the secret file.
- If a build/test failure references an env var, ask the user to confirm it's set — do not open the file to check.
- The harness is configured (`.claude/settings.local.json`) to block reads on these patterns. Treat any block as a signal that you violated this rule and re-plan.

---

## How to start a session in this repo

1. Read this `CLAUDE.md` end to end (you're already doing that).
2. **Read `.claude/devlog/DEVLOG.md` and the last 3 entries in `.claude/devlog/chunks/`.** That tells you what's actually been built and verified. Cross-check that the files mentioned still exist before trusting the log.
3. Check `PREFLIGHT.md` — if any tools are missing/wrong-version, install them before writing code.
4. Look at `decisions.md` — that's the project contract.
5. Pick the smallest user story from the **User stories / features** section above that the devlog shows is NOT yet done, and propose a 1-chunk plan to ship it.
6. After the user confirms the plan, build the chunk. Verify. Confirm. **Write a devlog entry.** Move on.
