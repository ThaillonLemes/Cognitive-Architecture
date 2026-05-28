# Protocol: Code header

BRIEF: Every code file MUST start with a 3-5 line header. Standardized format across all languages. Enables fast scanning and consistent navigation.

## Why

- Brief sits at top → AI processes it first regardless of full or partial read
- Cross-references (`SEE:` field) let AI navigate without re-grep
- Consistent format across files and projects = AI predictability
- Cheap to write (5 lines), high return (per-read efficiency)

## Mandatory fields

Every code file starts with these fields, in this order:

| Field | Meaning | Example |
|-------|---------|---------|
| `PURPOSE` | What this file does (1 line) | "Server-authoritative movement system" |
| `INPUTS` | What it consumes | "InputIntent component, movement_max_speed_mps" |
| `OUTPUTS` | What it produces | "SpatialMutation queue updates" |
| `DEPS` | What it depends on | "spatial_v2 (read), movement_v1 flag" |
| `SEE` | Related docs and code | "docs/arch/13-movement.md, src/movement/mod.rs" |

## Format per language

### Rust (`.rs`)

```rust
// PURPOSE: <one-line purpose>
// INPUTS: <inputs>
// OUTPUTS: <outputs>
// DEPS: <deps>
// SEE: <links>

use ...
```

### TypeScript / JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`)

```typescript
// PURPOSE: <one-line purpose>
// INPUTS: <inputs>
// OUTPUTS: <outputs>
// DEPS: <deps>
// SEE: <links>

import ...
```

### Python (`.py`)

```python
# PURPOSE: <one-line purpose>
# INPUTS: <inputs>
# OUTPUTS: <outputs>
# DEPS: <deps>
# SEE: <links>

import ...
```

### Go (`.go`)

```go
// PURPOSE: <one-line purpose>
// INPUTS: <inputs>
// OUTPUTS: <outputs>
// DEPS: <deps>
// SEE: <links>

package ...
```

### C / C++ (`.c`, `.cpp`, `.h`, `.hpp`)

```cpp
// PURPOSE: <one-line purpose>
// INPUTS: <inputs>
// OUTPUTS: <outputs>
// DEPS: <deps>
// SEE: <links>

#include ...
```

### Java / Kotlin (`.java`, `.kt`)

```java
// PURPOSE: <one-line purpose>
// INPUTS: <inputs>
// OUTPUTS: <outputs>
// DEPS: <deps>
// SEE: <links>

package ...
```

### Shell (`.sh`)

```bash
#!/usr/bin/env bash
# PURPOSE: <one-line purpose>
# INPUTS: <inputs (e.g., env vars, args)>
# OUTPUTS: <outputs (e.g., files written, exit code)>
# DEPS: <deps (e.g., tools, env)>
# SEE: <links>
```

### HTML / XML (top of body or as initial comment)

```html
<!--
PURPOSE: <one-line>
INPUTS: <inputs>
OUTPUTS: <outputs>
DEPS: <deps>
SEE: <links>
-->
```

### YAML / TOML / JSON-with-comments

For YAML/TOML: use `#` comments at top:

```yaml
# PURPOSE: <one-line>
# INPUTS: <inputs>
# ... etc
```

JSON doesn't support comments natively. For JSON config files, put the header in a sibling `<file>.README.md`.

## Content rules

### PURPOSE

- One line, < 80 characters
- Active voice ("Validates X", not "X is validated")
- Specific (not "utility functions") — say WHAT it does

### INPUTS

- List things this file READS or RECEIVES
- For functions in a module: list the main types/configs it uses
- Limit to top 3-5 — not exhaustive
- Use comma-separated

### OUTPUTS

- What this file PRODUCES or SIDE-EFFECTS
- Return types, mutations, files written, events emitted
- Top 3-5

### DEPS

- Required runtime dependencies (other modules, flags, services)
- NOT package imports (those are visible in code)
- Things that, if missing, this file breaks

### SEE

- Related docs (`docs/arch/X.md`)
- Related code (`src/module/Y.rs`)
- Related ADRs (`decisions/ADR-NNN.md`)
- Up to 5 references

## When header is updated

Update when:
- Purpose changes (new functionality added that shifts what file does)
- Major dependencies added/removed
- Related docs/code added that should be linked

Do NOT update for every small change. Header is stable orientation, not changelog.

## Audit

`audit.sh` (or doc-keeper agent) checks:
- Every code file has a header (presence)
- Header has all 5 mandatory fields
- SEE: links resolve (file exists)

Missing header → audit warning. Missing field → audit error.

## Migration guidance

For existing projects adopting this protocol:
- Don't refactor all at once (risk + churn)
- Add header to every file you NEWLY create or modify
- Sweep oldest/most-referenced files first
- Use doc-keeper agent to track coverage progress

## Examples

### Good header (Rust)

```rust
// PURPOSE: Tick-based movement system with server-authoritative position
// INPUTS: InputIntent component, movement_max_speed_mps tunable
// OUTPUTS: SpatialMutation::Move events to mutation queue
// DEPS: spatial_v2 (read positions), movement_v1 flag, ECS scheduler
// SEE: docs/arch/13-movement.md, docs/design/movement.md, ADR-014

use crate::components::InputIntent;
```

### Bad header

```rust
// Movement stuff
// Takes input, produces movement

use crate::components::InputIntent;
```

Why bad: vague purpose, no specific INPUTS/OUTPUTS, no SEE references.

End of code-header-protocol.
