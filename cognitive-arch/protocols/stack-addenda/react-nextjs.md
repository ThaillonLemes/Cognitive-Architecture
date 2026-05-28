# Stack addendum: React / Next.js

BRIEF: Convention overlay for React + Next.js (App Router) projects using the cognitive architecture. Read after PROTOCOLS.md and RETROFIT.md/BOOTSTRAP.md. Covers App Router conventions; for Pages Router, adapt `pages/` vs `app/` paths accordingly.

as_of: 2026-05-22
applies_to: React 18+, Next.js 13+ (App Router)

---

## 1. Setup

```bash
# Create new project
npx create-next-app@latest my-app --typescript --tailwind --eslint --app

# Install dependencies
npm install         # or: pnpm install / yarn install

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
| Component files | `PascalCase.tsx` | `UserCard.tsx` |
| Page/route files | `page.tsx`, `layout.tsx` (Next.js reserved) | `app/dashboard/page.tsx` |
| Hook files | `use<Name>.ts` | `useAuth.ts` |
| Utility files | `camelCase.ts` | `formatDate.ts` |
| CSS modules | `<Component>.module.css` | `UserCard.module.css` |
| API route handlers | `route.ts` | `app/api/users/route.ts` |
| Server actions | `actions.ts` in feature folder | `app/dashboard/actions.ts` |
| Test files | `<Component>.test.tsx` or `*.spec.tsx` | `UserCard.test.tsx` |

---

## 3. Project structure (App Router)

```
app/
  layout.tsx         # Root layout (html, body, providers)
  page.tsx           # Home page
  globals.css
  (auth)/            # Route group — no URL segment
    login/
      page.tsx
  dashboard/
    layout.tsx       # Nested layout
    page.tsx
    actions.ts       # Server actions for this route
    loading.tsx      # Streaming loading UI
components/
  ui/                # Primitive UI (Button, Input, Card)
  <Feature>/         # Feature-specific components
lib/
  db.ts              # DB client (Prisma, Drizzle, etc.)
  auth.ts            # Auth helpers
  utils.ts           # Shared utilities
hooks/               # Custom React hooks
types/               # Shared TypeScript types
cognitive-arch/      # Architecture scaffold
public/
package.json
next.config.ts
tsconfig.json
.env.local.example
```

---

## 4. Test command

```bash
npm test                     # jest (CRA-style) or vitest
npx vitest                   # vitest (preferred for App Router)
npx vitest run               # CI mode (no watch)
npx playwright test          # E2E
```

Set in `PROJECT.md`: `test_cmd: "npm test"` (or `npx vitest run` for vitest).

---

## 5. Lint command

```bash
npm run lint                 # next lint (ESLint with Next.js ruleset)
npx tsc --noEmit             # TypeScript type check (add to CI)
```

Set in `PROJECT.md`: `lint_cmd: "npm run lint"`

---

## 6. HOT file additions for Next.js projects

Add to `INDEX.md` WARM section:

| File | Brief |
|------|-------|
| `app/layout.tsx` | Root layout; providers, fonts, global styles |
| `app/page.tsx` | Home page component |
| `next.config.ts` | Next.js config; env vars, rewrites, headers |
| `lib/db.ts` | DB client singleton |
| `.env.local.example` | Required env vars (NEXT_PUBLIC_* and server-only) |
| `types/index.ts` | Shared TypeScript type definitions |

---

## 7. Code header example (TypeScript/React)

```typescript
// PURPOSE: <what this component/module does>
// INPUTS:  <props or parameters>
// OUTPUTS: <rendered element or return value>
// DEPS:    <key libraries — SWR, Prisma, Zustand, etc.>
// SEE:     design/<relevant-doc>.md
```

---

## 8. Next.js-specific cognitive-arch notes

- `[code-only]` axioms apply to `.ts`/`.tsx` files; Q-axioms apply to architecture decisions
- Server Components vs Client Components is a design decision: document in `design/rendering-strategy.md`
- `design/api-contracts.md`: use for App Router API route specs (`GET /api/users` etc.)
- Environment variables split: `NEXT_PUBLIC_*` (client-visible) vs server-only — document both in `design/` or `phase-0/01-stack-and-tools.md`
- Block manifests that touch both `app/` routes and `components/` should be Tier M (≥3 files)

End of react-nextjs addendum.
