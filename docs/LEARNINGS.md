# LEARNINGS.md — Causas-Raiz e Anti-Padrões

**Versão:** 1.0 · **Data:** 2026-07-23 · **Onda:** 10.5

---

## R1 — Hints MCP setados no objeto errado (ONDA 2.1)

**Sintoma:** `readOnlyHint`, `destructiveHint` etc. retornavam `None` em todas as tools.
**Causa:** O SDK MCP usa Pydantic. `Tool` não tem campo `readOnlyHint` — o campo é de `ToolAnnotations`. O código setava `t.readOnlyHint = True` (campo extra no Tool, ignorado) em vez de `t.annotations.readOnlyHint = True`.
**Regra:** Sempre verificar a classe correta no SDK antes de setar atributos. Pydantic `extra="allow"` silencia erros de atribuição.

## R2 — COLISÃO de definições (ONDA 3)

**Sintoma:** `playtest_manage` aparecia 2 vezes em `tools/list`.
**Causa:** A ferramenta era definida manualmente em `core/tool_definitions.py` E como rollup builder em `tools/rollups.py`. O pós-processamento adicionava ambas.
**Regra:** Toda tool `_manage` deve ter UMA única fonte de definição. Rollup builder é a fonte canônica.

## R3 — `catalog_search` chamava tool_catalog com dict em vez de kwargs

**Sintoma:** `catalog_search("scene")` retornava erro.
**Causa:** O wrapper passava `_tc({"query": query})` (dict) mas `tool_catalog` espera `query=str` (kwargs).
**Regra:** Sempre verificar a assinatura da função chamada. Não assumir que um dict é equivalente a kwargs.

## R4 — `test_token_budget` retornava `None` (auditar.py quebrava)

**Sintoma:** `auditar.py` C5 falhava com `'NoneType' object is not iterable`.
**Causa:** `test_token_budget(lean_only=False)` não retornava nada (só dava `assert`). `run_all_tests()` esperava uma lista.
**Regra:** Funções que são usadas como utility E como teste pytest devem ser separadas. Teste pytest retorna `None`; utility retorna o valor.

## R5 — Baseline `.reorg_baseline.json` com encoding quebrado (BOM)

**Sintoma:** Gate G3 falhava com "Unexpected UTF-8 BOM".
**Causa:** PowerShell `Out-File -Encoding utf8` adiciona BOM. `json.load()` não espera BOM.
**Regra:** Usar `[IO.File]::WriteAllText` com `UTF8Encoding($false)` para JSON sem BOM no Windows.
