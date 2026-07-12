# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-12
**Estado atual:** Patches 12, 12.1, 13, 17, 18 implementados e validados

## Resumo da última sessão

### Implementado:
- **PATCH 12:** Runtime Bridge — servidor TCP GDScript (porta 8790) + cliente Python + 4 tools MCP
- **PATCH 12.1:** Process Lifecycle — godot_run_project, godot_stop_project (save-before-kill), godot_wait_for_bridge
- **PATCH 13:** ClassDB introspecção — godot_class_ref via extension_api.json
- **PATCH 17:** Curadoria de toolset — `--toolsets` com 10 grupos
- **PATCH 18:** Marcador `.mcp_gate_failed`

### Corrigido:
- Handlers do PATCH 12 não estavam definidos (NameError) → implementados
- godot_stop_project: proteção contra PID reaproveitado (taskkill cego → verificação de nome)
- save-before-kill: 4 cenários validados (rastreado, órfão, suspenso, runtime)
- Hook PostToolUse: migrado de Python/venv para PowerShell puro (regex)

### Documentação:
- `MCP ESTADO ATUAL 12-07-2026.md` na Área de Trabalho (referência completa para IAs)

## Próximos passos (ordem recomendada)

1. **PATCH 14:** Testes roteirizados com input sintético e dump de estado
2. **PATCH 15:** Validação de referências (validate_project_refs + find_usages)
3. **PATCH 16:** Asset manifest (import automatizado via asset_manifest.json)

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --toolsets runtime_ops,design_ops
```

## Pontos de atenção

- `godot --headless --script` NÃO produz output no Windows Godot 4.7 (R12)
- `send_bridge_command` só funciona com jogo rodando em debug (use `godot_wait_for_bridge` antes)
- `godot_class_ref` cobre APENAS classes nativas (extension_api.json), não classes custom de projetos
- Hooks do NUCLEO são PowerShell puro — zero dependências do MCP
