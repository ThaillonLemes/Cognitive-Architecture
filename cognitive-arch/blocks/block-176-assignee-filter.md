---
id: block-176
manifest: manifests/block-176-adicionar-filtro-de-issues-por-assignee.md
status: wip
wip_stage_reached: quality
tok_actual: 800
actual_duration_hours: 1.2
---

# Block 176 — Filtro de Issues por Assignee

## 1. Summary

Implementado FilterAssignee component em ce/components/issues/filters/assignee.tsx.
Segue o padrao exato do FilterIssueTypes existente: observer MobX, Props tipadas com
snake_case para campos que vem da API Django (applied_filters, filtered_members),
PascalCase no componente, named imports. Integrado com useProjectMembers hook existente.
