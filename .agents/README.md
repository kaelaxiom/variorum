# `.agents/` — continuity protocol

Shared context between agent sessions. Any agent arriving at this repository must be able to continue work without talking to whoever was here before.

## Reading order

1. [STATE.md](STATE.md) — where the work stands, what is next
2. [HANDOFF.md](HANDOFF.md) — what the last session left open
3. [CONTEXT.md](CONTEXT.md) — architecture, design, structure
4. [MEMORY.md](MEMORY.md) — lessons learned, mistakes not to repeat
5. [PLAN.md](PLAN.md) — roadmap and checklist

## Writing order (end of session)

1. `SESSION.md` — append what happened
2. `STATE.md` — update reality
3. `HANDOFF.md` — leave the next session a clean start
4. `MEMORY.md` — only if something was learned the hard way

## Rules

- These files are **append-mostly**. Never rewrite history to look better.
- `STATE.md` describes reality, not intention. If a section is a stub, say so.
- Dates in ISO 8601 (`2026-11-22`). Times with offset (`2026-11-22T03:00:00-06:00`).
- Written in English, like everything agent-facing in this repository.
