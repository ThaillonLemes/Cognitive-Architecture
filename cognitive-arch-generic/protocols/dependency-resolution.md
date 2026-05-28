---
protection: guarded
protection_reason: Defines automated dependency resolution behavior; changes affect block lifecycle.
---

# Protocol: Dependency resolution

BRIEF: When a block closes (BLOCK_LOG append), `sdk/dependency_resolver.py` scans pending manifests and identifies any blocks whose `dependencies:` are now fully satisfied. Master Agent is notified and updates board.md accordingly. Auto-start is never performed — always user-initiated.

## Trigger

The resolver runs automatically when:
1. A block closes (implementer writes to BLOCK_LOG.md).
2. Master Agent's `dependency-check` tool is invoked explicitly.
3. User asks Master "what's unblocked?"

## Process flow

```
1. Read BLOCK_LOG → collect set of done block IDs
2. Read manifests/*.md → extract (id, dependencies) for each pending block
3. For each pending block:
   a. If all deps ∈ done_blocks → block is newly unblocked
4. Produce notification list
5. Master Agent:
   a. Logs to agents/master-log.md
   b. Updates board.md: wait → pending for each newly-unblocked block
   c. Notifies user (inline text if in session; no push notifications)
```

## Manifest dependency format

```yaml
---
id: block-105
dependencies: [block-103, block-104, block-107]
---
```

Dependencies listed as block IDs. Empty list `[]` = no dependencies.

## Board update rule (Master Agent action)

When resolver returns unblocked block IDs:
1. For each `block_id` in unblocked list:
   - Find the board.md row for that block (if exists).
   - If `status:wait` → change to `status:pending`.
   - If row doesn't exist → no action (new rows added when block starts).
2. Append to master-log.md:
   ```
   [2026-05-27T12:00Z] DEPS_RESOLVED blocks:[block-105] (deps:[block-103,block-104,block-107] all done)
   ```

## Conservative approach (safety)

- Resolver only marks blocks as unblocked if **all** declared dependencies are `done` in BLOCK_LOG.
- Partial satisfaction (some deps done) = no notification.
- If BLOCK_LOG is unreadable → resolver returns empty list (fail-safe, no false unblocks).
- Resolver never modifies manifests; it reads them read-only.

## Notification message format

Resolver produces an `AgentMessage` (kind: `notification`) per unblocked block:
```yaml
from: master
to: implementer
kind: notification
payload:
  event: dep_unblocked
  data:
    block_id: block-105
    deps_satisfied: [block-103, block-104, block-107]
```

## Out of scope

- Transitive dependency analysis (A depends on B depends on C — C done → A still not unblocked until B is done).
- Cross-project dependency resolution.
- Auto-starting unblocked blocks.
- Visualizing dependency graph (dashboard responsibility).

End of dependency-resolution protocol.
