# ONDA 2 — CONFORMIDADE MCP

> Derivada de `docs/REORG_ROADMAP.md` §4 e `MEDICAO_R7.md`.

---

## Fatia 2.1 — Corrigir server.py:1715 (_TAGS que apaga hints)

**1. O que é**
`server.py:1715` faz `t.annotations = {"tags": ...}` — substitui o dict inteiro e apaga os 4 hints MCP (readOnlyHint, destructiveHint, idempotentHint, openWorldHint).

**2. Por que agora**
Bug ativo que corrompe anotações MCP em toda tool.

**3. Arquivos que toca**
```
server.py
```

**4. Fonte obrigatória de consulta**
`server.py` l.1700-1720, `mcp.types.ToolAnnotations`.

**5. Como fazer**
Em vez de `t.annotations = {"tags": ...}`, fazer merge preservando os hints existentes.

**6. Armadilhas conhecidas**
- ToolAnnotations.model_config = `extra: allow` — SDK não rejeita campo fora da spec.

**7. Critérios de aceite**
- [ ] Hints preservados após `_apply_hints()`

**8. Como provar**
```powershell
python -c "from server import _tool_defs; t=_tool_defs()[0]; print(t.annotations)" | findstr "readOnlyHint destructiveHint idempotentHint"
```

**9. Regressão a retestar**
`python auditar.py --fatia 2.1`

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]`

---

## Fatia 2.2 — registry/annotations.py valida campos

**1. O que é**
Adicionar validação que rejeita campo fora da spec MCP (o SDK permite `extra: allow`).

**2. Por que agora**
Defesa em profundidade contra o bug 2.1.

**3. Arquivos que toca**
```
registry/annotations.py
tests/test_annotations.py
```

**4. Fonte obrigatória de consulta**
`mcp.types.ToolAnnotations`, `registry/annotations.py`.

**5. Como fazer**
Wrapper que valida campos contra `ToolAnnotations.model_fields`.

**6. Armadilhas conhecidas**
- Não quebrar ferramentas existentes que usam campos extras.

**7. Critérios de aceite**
- [ ] Campo extra → warning ou erro
- [ ] Campo válido → passa

**8. Como provar**
```powershell
python -m pytest tests/test_annotations.py -v
```

**9. Regressão a retestar**
`python auditar.py --fatia 2.2`

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`

---

## Fatia 2.3 — Congelar _HINT_RULES em dados revisados

**1. O que é**
Mover `_HINT_RULES` para `registry/legacy_annotations.py` como dados estáticos.

**2. Por que agora**
Remove lógica de `server.py`.

**3. Arquivos que toca**
```
server.py
registry/legacy_annotations.py
```

**4. Fonte obrigatória de consulta**
`server.py` l.1323-1360.

**5. Como fazer**
Copiar `_HINT_RULES` para `registry/legacy_annotations.py`. `server.py` importa de lá.

**6. Armadilhas conhecidas**
- Dados, não lógica — sem regressão funcional.

**7. Critérios de aceite**
- [ ] `_HINT_RULES` fora de `server.py`

**8. Como provar**
```powershell
findstr /N "_HINT_RULES" server.py; python -c "from registry.legacy_annotations import _HINT_RULES; print(len(_HINT_RULES))"
```

**9. Regressão a retestar**
`python auditar.py --fatia 2.3`

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`

---

## Fatia 2.4 — Deletar símbolos obsoletos

**1. O que é**
Deletar `_apply_hints`, `_READONLY`, `_DESTRUCTIVE`, `_IDEMPOTENT`, `_TITLES`, `_TAGS` de `server.py`.

**2. Por que agora**
Depende de 2.3.

**3. Arquivos que toca**
```
server.py
```

**4. Fonte obrigatória de consulta**
`server.py` l.1363, 1491, 1566, 1607.

**5. Como fazer**
Remover funções e constantes. Ajustar chamadas.

**6. Armadilhas conhecidas**
- `_TAGS` é usado em l.1715 (já corrigido em 2.1).

**7. Critérios de aceite**
- [ ] Zero ocorrências em `server.py`

**8. Como provar**
```powershell
findstr /N "_apply_hints _READONLY _DESTRUCTIVE _IDEMPOTENT _TITLES _TAGS" server.py
```

**9. Regressão a retestar**
`python -m pytest tests/ -q`

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]`

---

## Fatia 2.5 — rollback em toda op destrutiva

**1. O que é**
Preencher campo `rollback` em toda operação `_manage` com opção destrutiva.

**2. Por que agora**
Fecha a ONDA 2 com conformidade MCP completa.

**3. Arquivos que toca**
```
tools/rollups.py
```

**4. Fonte obrigatória de consulta**
`tools/rollups.py`.

**5. Como fazer**
Para cada op `delete`, `remove`, `clear`: adicionar descrição de rollback.

**6. Armadilhas conhecidas**
- Rollback pode ser impossível em algumas ops — documentar.

**7. Critérios de aceite**
- [ ] Toda op destrutiva tem `rollback` não-vazio

**8. Como provar**
```powershell
python -c "from tools.rollups import _ROLLUP_BUILDERS; ops=[(k,v) for k,v in _ROLLUP_BUILDERS.items() if 'delete' in str(v).lower()]; print(len(ops))"
```

**9. Regressão a retestar**
`python auditar.py --fatia 2.5`

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`
