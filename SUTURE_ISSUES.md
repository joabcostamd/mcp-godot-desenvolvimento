# 🔒 SUTURE ISSUES — Canal de Conflitos entre Agentes

> **Regra:** Quando um agente encontrar um conflito ou precisar mudar algo
> na Zona de Sutura, registre AQUI. NÃO modifique o arquivo diretamente.
> O humano (Joab) avalia e decide.

## Issues Pendentes

### [AGENTE 01] — Import circular server.py ↔ tools/dynamic_groups.py
- **Data:** 2026-07-19
- **Severidade:** 🟡 Baixa — funcional atualmente, mas frágil
- **Descrição:** `dynamic_groups.py` importa `from server import _tool_defs`. `server.py` (via handlers) importa `from tools.dynamic_groups import tool_catalog, tool_groups`. Funciona porque `server.py` é o entry point, mas quebraria se `dynamic_groups.py` fosse importado primeiro.
- **Solução ideal:** Inverter dependência — `dynamic_groups.py` receber `_tool_defs` como parâmetro, ou criar módulo compartilhado `core/tool_index.py`.
- **Ação:** Refatoração futura (Etapa A5 — Refatorações Estruturais).

---

## Issues Resolvidas

### ✅ [AGENTE 01] — SyntaxError em tools/code_quality_ops.py (AGENTE 02 — B3)
- **Data:** 2026-07-19
- **Resolvido por:** AGENTE 02 (sessão 2026-07-19)
- **Diagnóstico:** O erro original (f-string com escape `\"`) já havia sido corrigido em sessão anterior. A linha 620-621 agora extrai a variável antes do f-string: `unformatted = fmt_result.get("unformatted_count", 0)`. Pylance confirma 0 erros de sintaxe. `import server` funciona. 19/19 testes passam.

---

## Template para Novo Conflito
```
### [AGENTE 0X] — [Título]
- **Data:** YYYY-MM-DD
- **Arquivo em conflito:** [caminho]
- **Motivo:** [por que precisa mudar]
- **Impacto no outro agente:** [como afeta]
- **Solução proposta:** [o que sugere]
- **Decisão do Joab:** [aprovar/rejeitar/outra]
```
