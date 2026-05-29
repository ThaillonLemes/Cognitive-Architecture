# board — multi-agent dashboard (AI-only)
# Format: one row per agent. See _syntax.md for vocabulary.
# When real agents start, replace placeholder row with live rows.

agent:implementer b:135 group:17C status:done lock:ready deps:- ts:2026-05-29 last_done:block-135
agent:master b:- group:- status:idle lock:ready deps:- ts:2026-05-27

# Example rows (delete when first real agent is created):
# agent:governor   b:- group:- status:idle lock:ready deps:- ts:2026-05-19T14:00Z
# agent:1a         b:031 group:1a status:wip lock:in-progress deps:- ts:2026-05-19T14:22Z
# agent:1b         b:032 group:1b status:wait lock:ready deps:block-031 ts:2026-05-19T14:22Z
# agent:reviewer   b:- group:- status:idle lock:ready deps:- ts:2026-05-19T14:00Z
