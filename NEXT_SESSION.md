# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-12 (sessão de auditoria e hardening)
**Estado atual:** v3.2.1 — 190 tools, 190 handlers, 64 módulos, 18 patches, 5 grupos

## Resumo da sessão

### Correções de segurança (sandbox)
- Sandbox conectado a write_file/safe_write_gdscript (36/36 padrões bloqueados)
- Normalizador de código (comentários, whitespace, concatenação literal)
- 4/6 bypasses fechados (2 restantes documentados como limitação)
- Godot check desligado por padrão (`tentar_checagem_godot=false`)

### Correções de bugs
- B1 documentado (IDs alfanuméricos), B2 corrigido (runtime tools), B3 corrigido (status)
- Handler órfão estimate_tool_tokens corrigido
- PATCH 12 auditado (_cmd_custom, _reply)
- safe_write_gdscript path relativo + godot_console_path corrigidos

### Infraestrutura
- Hook Stop NUCLEO: check-gate-failed.ps1
- pre-commit versionado em .github/hooks/scripts/
- config.json untracked do Git
- MCPs duplicados removidos

### Documentação
- Todos os 6 docs atualizados para v3.2
- LEARNINGS.md R12 ampliado
- MCP ESTADO ATUAL externo sincronizado

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --profile dev
```

## Pontos de atenção

- `godot --headless --script` E `--check-only` NÃO funcionam no Windows Godot 4.7 (R12 ampliado)
- Godot check desligado por padrão — para religar: `"tentar_checagem_godot": true` no config.json
- `send_bridge_command` só funciona com jogo rodando em debug (use `godot_wait_for_bridge` antes)
- `godot_class_ref` cobre APENAS classes nativas (extension_api.json), não classes custom
- Hooks do NUCLEO são PowerShell puro — zero dependências do MCP
- Use `--profile dev` para iniciar com 31 tools (economiza ~75% tokens vs full)
- **config.json NÃO é mais versionado** — use `config.json.example` como template, `config.local.json` para overrides

## Pendências conhecidas

| Pendência | Prioridade |
|-----------|-----------|
| Sandbox: BYPASS-1 (concat via variáveis) e BYPASS-5 (aliasing) não bloqueados | Média |
| B1: regex `\d+` não captura IDs alfanuméricos (ex: `1_sh`) | Baixa |
| NUCLEO Bloco 14: CLONE-DO-ZERO-NOVO-PC.md, setup-maquina.ps1, PROTOCOLO-MULTI-MAQUINA.md | Baixa |
| 21 arquivos no NUCLEO ainda referenciam `sistema/mcp-godot/servidor/` (docs desatualizados) | Baixa |
