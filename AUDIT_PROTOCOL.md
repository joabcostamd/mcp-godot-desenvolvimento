# AUDIT_PROTOCOL.md — Protocolo de Auditoria do MCP Godot Agent

> **Versão:** 1.0 | **Data:** 2026-07-14 | **MCP:** godot-mcp-agent v3.3.0

Documento de referência para o protocolo de auditoria estática de projetos Godot via MCP. Descreve cadência, escopo e regras de segurança das ferramentas de detecção de wiring.

---

## 1. Cadência de Auditoria

As 5 ferramentas de auditoria são classificadas em 3 tiers de custo/risco:

### Tier 1 — Barata (regex/parse simples, ~ms)

Dispara automaticamente a cada `git_commit_checkpoint` como **warning não-bloqueante**.

| Ferramenta | Gatilho | Arquivo | Bloqueia commit? |
|-----------|---------|---------|-----------------|
| `audit_input_map` | `git_commit_checkpoint` | `tools/safety.py` | ❌ Não |
| `audit_autoloads` | `git_commit_checkpoint` | `tools/safety.py` | ❌ Não |
| `audit_uid_consistency` | `git_commit_checkpoint` | `tools/safety.py` | ❌ Não (destaque ALTO para duplicados) |

### Tier 2 — Média (parse de múltiplos arquivos, ~100ms-1s)

Dispara automaticamente no encerramento da sessão e como etapa opcional de pipeline.

| Ferramenta | Gatilho | Arquivo | Bloqueia? |
|-----------|---------|---------|-----------|
| `audit_scene_reachability` | `hook_stop.py` (encerramento) | `tools/hook_stop.py` | ❌ Não |
| `audit_scene_reachability` | `run_verification_pipeline` (etapa 5, `include_reachability_audit=True`) | `tools/verification_ops.py` | ❌ Não |

### Tier 3 — Sob demanda (análise específica)

Disponível como tool MCP, disparada manualmente ou via `analyze_game_structure`.

| Ferramenta | Gatilho | Arquivo |
|-----------|---------|---------|
| `audit_save_compatibility` | `analyze_game_structure` (campo `wiring_status`) | `tools/analyze_ops.py` |
| `audit_uid_consistency` | `analyze_game_structure` (campo `wiring_status`) | `tools/analyze_ops.py` |

**Visibilidade automática:** `suggest_next_steps` exibe resumo agregado de todas as auditorias no campo `wiring_status`, sem exigir chamada manual.

---

## 2. Escopo

### Coberto (análise estática, sem Godot rodando)

| Domínio | Ferramenta | O que detecta |
|---------|-----------|---------------|
| Input Map | `audit_input_map` | Ações declaradas nunca usadas, ações referenciadas mas não declaradas |
| Autoloads | `audit_autoloads` | Singletons registrados sem referência direta no código |
| Cenas | `audit_scene_reachability` | Cenas `.tscn` que existem mas não são alcançáveis a partir da cena raiz (BFS de `PackedScene` + `load`/`preload` + `change_scene_to_file`) |
| UID | `audit_uid_consistency` | UID declarado vs real (`.uid` file), UIDs duplicados entre arquivos |
| Save | `audit_save_compatibility` | Divergência escrita/leitura, ausência de lógica de migração por versão |

### NÃO Coberto (requer Godot rodando ou análise mais profunda)

- Comportamento em runtime (coberto parcialmente por `run_verification_pipeline`: compile, headless run, screenshot, GUT)
- Testes de integração end-to-end
- Performance profiling
- Lógica de negócio do jogo (ex: "o upgrade X realmente funciona?")
- Cenas carregadas via `change_scene_to_packed()` com variável dinâmica não resolvida estaticamente
- Uso de input via tecla direta (`Input.is_key_pressed`) sem Input Map
- Validação de que a lógica de migração de save funciona corretamente em runtime

---

## 3. Regra de Deleção Segura

> **NENHUMA ferramenta de auditoria neste MCP deleta, modifica ou reescreve qualquer arquivo do projeto.** Todas são SOMENTE LEITURA.

### Protocolo antes de deletar algo com base em um achado de auditoria:

1. **Confirmar que não é falso positivo conhecido:**
   - `possibly_unused_autoloads`: verificar se o singleton é acessado via `get_node("/root/Nome")` ou `grupo` (audit_autoloads só detecta `Nome.` como prefixo de chamada direta)
   - `unreachable_scenes`: verificar se a cena é carregada via `change_scene_to_packed()` com variável dinâmica (listado em `dynamic_scene_refs_unresolved`)
   - `missing_uid_file`: em projetos `config_version <= 5`, ausência de `.uid` files é **esperada** — não são erros
   - `unresolved` (uid_cache.bin): o formato binário pode não ser parseável em versões mais novas do Godot

2. **Verificar com ferramenta complementar:**
   - Antes de remover um autoload: rodar `find_usages(target="NomeDoAutoload")` para busca exaustiva
   - Antes de remover uma cena: rodar `search_codebase(query="nome_da_cena")` para buscar menções em strings e comentários

3. **Decisão manual obrigatória:** Toda correção (deletar cena, remover autoload, corrigir UID) é decisão humana. As ferramentas apenas **reportam** — nunca corrigem automaticamente.

4. **Checkpoint antes de deletar:** Fazer `git_commit_checkpoint` antes de qualquer remoção baseada em auditoria, para ter rollback garantido.

---

## 4. Ferramentas de Apoio (não-auditoria, já existentes no MCP)

Estas ferramentas complementam o protocolo de auditoria mas pertencem a outros módulos:

| Ferramenta | Módulo | Uso no protocolo |
|-----------|--------|-----------------|
| `find_usages` | `tools/refs_ops.py` | Confirmar se um autoload/arquivo é realmente não referenciado |
| `search_codebase` | `tools/analyze_ops.py` | Busca full-text por menções em strings/comentários |
| `validate_project_refs` | `tools/refs_ops.py` | Validar referências cruzadas (ext_resource, preload, etc.) |
| `find_unused_resources` | `tools/find_unused_resources.py` | Assets órfãos (png/wav/glb — complementar a cenas) |
| `run_verification_pipeline` | `tools/verification_ops.py` | Pipeline completo (compile + headless + screenshot + GUT) |
| `regression_test` | `tools/test_ops.py` | Validar que novas alterações não quebraram contratos |

---

## 5. Histórico de Versão

| Versão | Data | Alteração |
|--------|------|-----------|
| 1.0 | 2026-07-14 | Documento inicial. Cobre Bloco 1 (audit_input_map, audit_autoloads, audit_scene_reachability) + Bloco 2 (audit_uid_consistency, audit_save_compatibility). |
