# Stack addendum: Node.js / Express

BRIEF: Convention overlay for Node.js + Express projects using the cognitive architecture. Read after PROTOCOLS.md and RETROFIT.md/BOOTSTRAP.md. Covers CommonJS and ES module conventions; note the module system decision point in §8.

as_of: 2026-05-22
applies_to: Node.js 18+, Express 4/5

---

## 1. Setup

```bash
# Initialize project
npm init -y

# Install Express
npm install express

# TypeScript (recommended)
npm install -D typescript @types/express @types/node ts-node

# Initialize TypeScript
npx tsc --init

# If using cognitive-arch SDK
pip install -r cognitive-arch/sdk/requirements.txt
```

Add to `PROJECT.md` frontmatter:
```yaml
build_cmd: "npm run build"
test_cmd: "npm test"
lint_cmd: "npm run lint"
```

---

## 2. Naming conventions

| Item | Convention | Example |
|------|-----------|---------|
| Files (JS/TS) | `camelCase.ts` or `kebab-case.ts` | `userService.ts` or `user-service.ts` |
| Classes | `PascalCase` | `UserRepository` |
| Functions / variables | `camelCase` | `getUserById` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_PORT` |
| Route files | `<resource>.routes.ts` | `users.routes.ts` |
| Controller files | `<resource>.controller.ts` | `users.controller.ts` |
| Service files | `<resource>.service.ts` | `users.service.ts` |
| Middleware | `<name>.middleware.ts` | `auth.middleware.ts` |
| Test files | `<module>.test.ts` or `<module>.spec.ts` | `users.service.test.ts` |

_Pick one file naming convention per project (camelCase or kebab-case) and stick to it._

---

## 3. Project structure

```
src/
  app.ts             # Express app factory (no listen() here)
  server.ts          # Entry point — imports app, calls listen()
  config/
    index.ts         # Env var validation (zod or joi)
  routes/
    index.ts         # Router aggregator
    users.routes.ts  # Feature routes
  controllers/
    users.controller.ts
  services/
    users.service.ts
  middleware/
    auth.middleware.ts
    error.middleware.ts
  models/            # DB models (Prisma schema, Mongoose models, etc.)
  utils/             # Shared helpers
tests/
  users.service.test.ts
  users.routes.test.ts
cognitive-arch/      # Architecture scaffold
package.json
tsconfig.json
.env.example
```

---

## 4. Test command

```bash
npm test                     # jest (default for most setups)
npx jest --runInBand         # CI mode (sequential)
npx vitest                   # vitest alternative
npx supertest                # HTTP integration testing (import in tests)
```

Set in `PROJECT.md`: `test_cmd: "npm test"`

---

## 5. Lint command

```bash
npm run lint                 # eslint (standard config)
npx eslint src --ext .ts     # explicit
npx tsc --noEmit             # type check (separate from lint)
```

Set in `PROJECT.md`: `lint_cmd: "npm run lint"`

---

## 6. HOT file additions for Express projects

Add to `INDEX.md` WARM section:

| File | Brief |
|------|-------|
| `src/app.ts` | Express app factory; middleware stack, router mounts |
| `src/server.ts` | Entry point; port binding, graceful shutdown |
| `src/config/index.ts` | Env var validation and typed config object |
| `src/routes/index.ts` | Route aggregator — all feature routers registered here |
| `.env.example` | Required env vars with example values |
| `package.json` | Scripts, dependencies, engine constraint |

---

## 7. Code header example (TypeScript)

```typescript
// PURPOSE: <what this module/route/service does>
// INPUTS:  <Request params, body, query | function arguments>
// OUTPUTS: <Response object | return type>
// DEPS:    <key libraries — Prisma, Redis, Nodemailer, etc.>
// SEE:     design/<relevant-doc>.md
```

---

## 8. Node.js-specific cognitive-arch notes

**Module system decision (make this in Phase 0):**
- `"type": "module"` in `package.json` → ES modules (`import`/`export`); requires `.js` extensions in imports
- No `"type": "module"` → CommonJS (`require()`/`module.exports`); simpler for beginners

Document the choice in `design/` or `phase-0/01-stack-and-tools.md`. Do not mix.

**Other notes:**
- `[code-only]` axioms (P1, C1–C6) apply to all `.ts`/`.js` files
- Express error middleware MUST have 4 params `(err, req, res, next)` — document this in `design/`
- ORM choice (Prisma vs Drizzle vs Mongoose) is a design decision: ADR in `decisions/`
- Block manifests touching routes + controllers + services should be Tier M

End of node-express addendum.
