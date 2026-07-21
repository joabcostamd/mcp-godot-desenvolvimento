# 🚀 PROMPT MESTRE — Próxima Sessão

> **Copie e cole este bloco inteiro no chat da próxima sessão.**
> **Data:** 2026-07-21 | **Commit:** 3f109f2 | **Branch:** main

---

Continue o desenvolvimento do **mcp-godot-desenvolvimento**.

## Estado atual
- **Branch:** main (Agente 1 — Núcleo)
- **Commit:** 3f109f2 (push OK para origin/main)
- **F5:** 5 domínios migrados (physics ✅, ui ✅, shader ✅, camera ✅, navigation ✅)
- **Estabilização:** CONCLUÍDA (E1-E6, J1-J4, K1-K3, L1-L4, M1-M3)
- **Testes:** 176/176 passam (8 xfailed)
- **Auditoria:** AUDITORIA F5: APROVADA
- **SEM_HANDLER=0, SEM_DEF=0, NS_FANTASMA=0, PHASE_FANTASMA=0**
- **defs_total=269, handlers_total=268**

## ⚠️ F5.2 ui: JÁ CORRIGIDO — não refazer

## Instruções

1. **LEIA antes de qualquer ação:**
   - `HANDOFF.md`
   - `MASTER_IMPLEMENTATION_ROADMAP.md` §FASE 5
   - `.reorg_progress.json` (métricas atuais)
   - `.github/instructions/aprendizados.instructions.md`

2. **VALIDAR baseline:**
   ```
   .venv\Scripts\python.exe scripts/audit_fase.py --fase F5
   .venv\Scripts\python.exe -m pytest tests/ domains/ -q
   ```
   Deve retornar: AUDITORIA F5: APROVADA, 176 passed.

3. **PRÓXIMO PASSO: /plan para F5.6**
   Escolher entre domínios restantes (~8): render, skeleton, debug, lsp, godot, network, particles, lights.
   Prioridade: os que já têm rollup _manage funcional (todos os 6 acima).

4. **NUNCA:**
   - Refazer estabilização (E1-E6, J1-J4, K1-K3, L1-L4, M1-M3)
   - Remover ALIAS_MAP antes de F6
   - Reverter filtro DEPRECATED_TOOLS em _tool_defs()
   - Criar tool de topo nova (use rollup)
   - Usar re-exports em handlers de domínio
   - Commitar sem rodar audit_fase.py
   - Pular leitura do MASTER_IMPLEMENTATION_ROADMAP

5. **SEMPRE:**
   - Rodar `audit_fase.py --fase F5` após cada fatia
   - Rodar `pytest tests/ domains/ -q` após cada fatia
   - Atualizar `.roadmap_progress.json`
   - Atualizar `HANDOFF.md`
   - Commitar e dar push
   - Executar protocolo de encerramento completo ao final

## Comando rápido para iniciar
```
/plan
```

