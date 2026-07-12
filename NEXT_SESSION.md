# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-12
**Estado atual:** MCP 100% CONCLUÍDO — 8 patches + 5 grupos auditoria + 43 bugs corrigidos

## Resumo da última sessão

### Implementado (novos patches):
- **PATCH 14:** Testes roteirizados — smoke_test, regression_test, run_scripted_tests, dump_mcp_state, estimate_tool_tokens
- **PATCH 15:** Validação de referências — validate_project_refs, find_usages (estático, offline)
- **PATCH 16:** Asset manifest — import_asset_manifest (5 fontes), create_asset_manifest

### Auditoria completada (todos os grupos):
- **GRUPO 1:** Validação GDScript no write_file + safe_write R9
- **GRUPO 2:** git_commit_checkpoint com gates de compilação + GUT
- **GRUPO 3:** --profile (core/dev/full) + MCP_TOOL_PROFILE + estimate_tool_tokens
- **GRUPO 4:** config.local.json + GODOT_MCP_* env vars (já existia, confirmado)
- **GRUPO 5:** allow_paid_generation=False + estimated_cost

### Total:
- 189 ferramentas, 64 módulos, 10 toolsets, 3 perfis
- 43 bugs corrigidos em 10 rodadas de auditoria

## Próximos passos (NUCLEO Bloco 14)

1. Finalizar CLONE-DO-ZERO-NOVO-PC.md
2. Criar setup-maquina.ps1
3. Criar PROTOCOLO-MULTI-MAQUINA.md

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --profile dev
```

## Pontos de atenção

- `godot --headless --script` NÃO produz output no Windows Godot 4.7 (R12)
- `send_bridge_command` só funciona com jogo rodando em debug (use `godot_wait_for_bridge` antes)
- `godot_class_ref` cobre APENAS classes nativas (extension_api.json), não classes custom
- Hooks do NUCLEO são PowerShell puro — zero dependências do MCP
- Use `--profile dev` para iniciar com 29 tools (economiza ~50% tokens vs full)
