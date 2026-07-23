# ONDA 1 — REGISTRY

> Derivada de `docs/REORG_ROADMAP.md` §4 e `MEDICAO_R7.md`.
> Fazer `tools/list`, handlers, fases e namespaces serem **derivados** de manifesto.

---

## Fatia 1.1 — Confirmar o que registry/ já faz

**1. O que é**
Auditar `registry/` (types.py, discovery.py, invariants.py, legacy_adapter.py, annotations.py) e documentar o que cada módulo já implementa versus o que falta.

**2. Por que agora**
`registry/` existe mas `server.py` ainda declara tools manualmente. Antes de migrar, precisamos saber o estado real.

**3. Arquivos que toca**
```
journal/auditoria_registry.md  (novo)
```

**4. Fonte obrigatória de consulta**
`registry/*.py`, `REORG_ROADMAP.md` §4 ONDA 1.

**5. Como fazer**
Ler cada arquivo de `registry/`, listar classes/funções públicas, comparar com o que `server.py` espera.

**6. Armadilhas conhecidas**
- `registry/` pode ter dependência circular com `server.py`.

**7. Critérios de aceite**
- [ ] Documento lista exports de cada módulo
- [ ] Gaps documentados

**8. Como provar**
```powershell
Get-Content journal/auditoria_registry.md
```

**9. Regressão a retestar**
`python -c "import registry"` sem erro.

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`

---

## Fatia 1.2 — server.py passa a chamar registry.build_tool_defs()

**1. O que é**
Substituir `_tool_defs()` em `server.py` por chamada a `registry.build_tool_defs()`.

**2. Por que agora**
Depende de 1.1.

**3. Arquivos que toca**
```
server.py
registry/
```

**4. Fonte obrigatória de consulta**
`registry/discovery.py`, `server.py:_tool_defs()`.

**5. Como fazer**
1. `registry/` exporta `build_tool_defs()` com a mesma assinatura de `_tool_defs()`.
2. `server.py:_tool_defs()` chama `registry.build_tool_defs()`.
3. `dump_toollist.py` antes e depois — `fc` idêntico nas 6 fases.

**6. Armadilhas conhecidas**
- Rollups e aliases precisam ser preservados exatamente.

**7. Critérios de aceite**
- [ ] `fc` entre dump antes e depois idêntico

**8. Como provar**
```powershell
python scripts/dump_toollist.py > antes.txt ; # implementar ; python scripts/dump_toollist.py > depois.txt ; cmd /c "fc antes.txt depois.txt"
```

**9. Regressão a retestar**
`python auditar.py --fatia 1.2` verde.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]`

---

## Fatia 1.3 — Remover TOOLSETS/PHASE_TOOLSETS/TOOL_PROFILES/PHASE_TOOLS_CORE de server.py

**1. O que é**
Remover as declarações manuais que hoje convivem com o registry.

**2. Por que agora**
Depende de 1.2.

**3. Arquivos que toca**
```
server.py
```

**4. Fonte obrigatória de consulta**
`server.py` linhas 60, 295, 353, 530.

**5. Como fazer**
Deletar `TOOLSETS`, `PHASE_TOOLSETS`, `TOOL_PROFILES`, `PHASE_TOOLS_CORE`. Mover para `registry/legacy_data.py` se necessário.

**6. Armadilhas conhecidas**
- `_get_phase_tools()` e `auditar.py` referenciam estes símbolos.

**7. Critérios de aceite**
- [ ] `server.py` sem `TOOLSETS =`, `PHASE_TOOLSETS =`, `TOOL_PROFILES =`, `PHASE_TOOLS_CORE =`
- [ ] `python auditar.py --fatia 1.3` verde

**8. Como provar**
```powershell
findstr /N "TOOLSETS = PHASE_TOOLSETS = TOOL_PROFILES = PHASE_TOOLS_CORE =" server.py ; python auditar.py --fatia 1.3
```

**9. Regressão a retestar**
`python -m pytest tests/ -q` sem novos erros.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]`

---

## Fatia 1.4 — gen_catalog.py gera catálogo do registry

**1. O que é**
Script que lê o registry e gera documentação de catálogo.

**2. Por que agora**
Fecha a ONDA 1.

**3. Arquivos que toca**
```
scripts/gen_catalog.py  (novo)
```

**4. Fonte obrigatória de consulta**
`registry/`.

**5. Como fazer**
Ler `registry/`, gerar markdown com tools, fases, handlers.

**6. Armadilhas conhecidas**
- Catálogo precisa ser determinístico (sorted).

**7. Critérios de aceite**
- [ ] Script roda e gera saída
- [ ] Duas execuções idênticas

**8. Como provar**
```powershell
python scripts/gen_catalog.py > cat1.md ; python scripts/gen_catalog.py > cat2.md ; cmd /c "fc cat1.md cat2.md"
```

**9. Regressão a retestar**
N/A (script novo).

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]`
