# Arquitetura Cognitiva — Raiz do projeto

## Comportamento de saudação (OBRIGATÓRIO)

Quando o usuário enviar uma saudação (`ola`, `olá`, `hello`, `hi`, `oi`, `hey`), **nunca** responda com "como posso ajudar?" ou equivalente.

Execute imediatamente, sem perguntar:
1. `python cognitive-arch/sdk/session_start.py --arch-root cognitive-arch/`
   - Se falhar, leia manualmente os arquivos abaixo
2. Leia `cognitive-arch/STATE.md`
3. Leia `cognitive-arch/NEXT.md`
4. Reporte: status atual, fase/bloco ativo, próxima ação, health score (se disponível)

Protocolo completo de entrada: `cognitive-arch/CLAUDE.md`
