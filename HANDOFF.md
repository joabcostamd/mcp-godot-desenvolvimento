# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## Último Handoff
- **Data:** 2026-07-19
- **De:** AGENTE 01
- **Etapa concluída:** A0 — Limpeza Imediata (Sprint 0.5)

### O que foi feito
- 3 bridges quebradas movidas para `backups/`
- `_DEPRECATED` + `_DEPRECATED_H` unificados em `tools/deprecated.py`
- 55 funções marcadas com `# INTERNAL: usado por <rollup>`
- Imports residuais limpos em `server.py`
- `validate_tool_registry_consistency()` → 0 `tools_sem_handler` ✅
- 23 arquivos redundantes deletados
- Sistema de automação criado (`.github/`, `ROADMAP_UNIFICADO.md`, agentes, prompts, hooks)

### O que NÃO foi feito
- Commits pendentes (aguardando aprovação do Joab)

### Decisões tomadas
- Sistema de 2 agentes Copilot com Zona de Sutura congelada
- Estratégia "Meet in the Middle": AGENTE 01 do core → fora, AGENTE 02 das extensões → dentro
- Pipeline autônomo via `/seguir-roadmap`

### ⚠️ Pontos de atenção para o AGENTE 02
- `tools/deprecated.py` é Zona de Sutura — NÃO EDITAR
- Funções com `# INTERNAL:` NÃO REMOVER
- `tools/devsolo_ops.py` tem 19 anotações INTERNAL — cuidado ao modificar
- ~7 sessões de trabalho NÃO commitadas (fatias 3.10-4.1) — prioridade URGENTE

---

## Histórico
*(handoffs anteriores serão appendados aqui)*
