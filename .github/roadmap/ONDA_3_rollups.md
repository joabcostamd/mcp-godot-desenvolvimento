# ONDA 3 — UNIFICAR ROLLUPS

> Derivada de `docs/REORG_ROADMAP.md` §4.

---

## Fatia 3.1 — budget_manage

**1. O que é**
Auditar `budget_manage` (core/tool_definitions.py l.30): migrar, quarentena ou deletar.

**2. Por que agora**
13 `_manage` manuais não seguem o padrão de fábrica `create_manage_tool()`.

**3. Arquivos que toca**
```
core/tool_definitions.py
tools/rollups.py
```

**4. Fonte obrigatória de consulta**
`_meta_tool.py:create_manage_tool()`, `tools/rollups.py:_ROLLUP_BUILDERS`.

**5. Como fazer**
Classificar: migrar para rollup / quarentena / deletar. Provar uso com `findstr`.

**6. Armadilhas conhecidas**
- `playtest_manage` tem COLISÃO: definido em `_raw_tool_defs()` E em `rollups.py`.

**7. Critérios de aceite**
- [ ] Tool não está mais em `core/tool_definitions.py` como definição manual OU está justificada

**8. Como provar**
```powershell
findstr /N "budget_manage" core/tool_definitions.py
```

**9. Regressão a retestar**
`python auditar.py --fatia 3.1`

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`
