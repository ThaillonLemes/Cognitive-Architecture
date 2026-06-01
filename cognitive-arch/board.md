# board — multi-agent dashboard (AI-only)
# Format: one row per agent. See _syntax.md for vocabulary.
# When real agents start, replace placeholder row with live rows.

agent:implementer b:- group:- status:idle lock:ready deps:- ts:2026-06-01 last_done:block-175
agent:master b:- group:- status:idle lock:ready deps:- ts:2026-05-27
agent:tracker b:track-block-001 group:tracks status:wip lock:ready deps:- ts:2026-05-31 focus:track/orquestracao-paralelismo

# Example rows (delete when first real agent is created):
# agent:governor   b:- group:- status:idle lock:ready deps:- ts:2026-05-19T14:00Z
# agent:1a         b:031 group:1a status:wip lock:in-progress deps:- ts:2026-05-19T14:22Z
# agent:1b         b:032 group:1b status:wait lock:ready deps:block-031 ts:2026-05-19T14:22Z
# agent:reviewer   b:- group:- status:idle lock:ready deps:- ts:2026-05-19T14:00Z
