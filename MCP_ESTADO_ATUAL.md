# MCP ESTADO ATUAL — Godot Agent v3.2.1

> **Última atualização:** 2026-07-12 (sessão de auditoria e hardening)
> **Auto-contido:** este arquivo contém TUDO necessário para retomar o desenvolvimento

---

## 🔢 NÚMEROS

| Métrica | Valor |
|----------|-------|
| Tools definidas | **190** |
| Handlers implementados | **190** (100% match) |
| Módulos Python | **64** |
| Toolsets | **10** (core, 2d, 3d, physics, ui, audio, art, debug, pipeline, advanced) |
| Perfis | **3** (core=31, dev=80, full=190) |
| Patches | **18** (PATCH 1-18) |
| Grupos de auditoria | **5** (todos concluídos) |
| Bugs corrigidos | **43+** (desde v3.0) |
| Portas bridge | **5** (9080 LSP, 9081 GameBridge, 9082 AddonBridge, 8790 RuntimeBridge, 6005 DAP) |
| Classes Godot catalogadas | **1074** (extension_api.json) |

---

## 📦 ARQUITETURA DE ARQUIVOS

```
mcp-godot-desenvolvimento/
├── server.py              # ~7300 linhas, 190 tools + 190 handlers
├── config.json.example    # Template de configuração
├── config.json            # NÃO versionado (local)
├── config.local.json      # Overrides locais (opcional)
├── pyproject.toml         # v3.2.1, python>=3.12
├── requirements.txt       # godot_parser>=0.1.7
├── install.py             # Instalador do ambiente
├── launch.py              # Launcher do servidor
├── validate_gdscript.py   # Validador standalone
├── _meta_tool.py          # Definições de meta-tools
│
├── tools/                 # 64 módulos
│   ├── safety_policy.py   # Política de segurança (24 classes + 25 padrões)
│   ├── gdscript_sandbox.py # Sandbox regex (validate_gdscript_code)
│   ├── validate_write.py  # safe_write_gdscript (validação dupla)
│   ├── file_ops.py        # write_file (agora valida .gd)
│   ├── orchestator.py     # Pipeline Executor
│   ├── bridge.py          # Bridge genérica
│   ├── editor_bridge.py   # Bridge Editor (9081)
│   ├── addon_bridge.py    # Bridge Addon (9082)
│   ├── game_bridge.py     # Bridge Jogo
│   ├── runtime_ops.py     # Runtime Bridge (8790)
│   ├── runtime_rich.py    # Comandos runtime avançados
│   ├── runtime_ui.py      # UI runtime
│   ├── debugger_ops.py    # DAP Debugger (6005)
│   ├── lsp_ops.py         # LSP (6005)
│   ├── script_ops.py      # Operações de script
│   ├── scene_ops.py       # Operações de cena
│   ├── project_ops.py     # Operações de projeto
│   ├── project_state.py   # Estado do projeto
│   ├── project_map.py     # Mapeamento do projeto
│   ├── config_loader.py   # Carregador de config
│   ├── classdb.py         # ClassDB (extension_api.json)
│   ├── test_ops.py        # Testes roteirizados
│   ├── gut_ops.py         # GUT (Godot Unit Test)
│   ├── refs_ops.py        # Validação de referências
│   ├── asset_ops.py       # Asset operations
│   ├── asset_manifest.py  # Asset manifest
│   ├── art_ops.py         # Geração de arte
│   ├── art_postprocess.py # Pós-processamento de arte
│   ├── flux_ops.py        # FLUX AI
│   ├── shader_ops.py      # Shaders
│   ├── threed_gen.py      # Geração 3D
│   ├── world_gen.py       # Geração de mundo
│   ├── physics_ops.py     # Física
│   ├── behavior_ops.py    # Comportamentos
│   ├── juice_ops.py       # Juice/feedback
│   ├── balance_ops.py     # Balanceamento
│   ├── audio_ops.py       # Áudio (via TTS)
│   ├── tts_ops.py         # Text-to-Speech
│   ├── ui_ops.py          # UI
│   ├── vibe_ops.py        # Vibe coding
│   ├── devsolo_ops.py     # DevSolo
│   ├── pipeline_ops.py    # Pipeline
│   ├── batch_ops.py       # Batch operations
│   ├── export_ops.py      # Exportação
│   ├── deploy_ops.py      # Deploy
│   ├── networking_ops.py  # Networking
│   ├── security_ops.py    # Segurança
│   ├── perf_ops.py        # Performance
│   ├── recording_ops.py   # Gravação
│   ├── playmode_ops.py    # Play mode
│   ├── playtest_ops.py    # Playtest
│   ├── file_watcher.py    # File watcher
│   ├── live_stream.py     # Live stream
│   ├── bootstrap_ops.py   # Bootstrap
│   ├── infra_ops.py       # Infraestrutura
│   ├── workflow_ops.py    # Workflow
│   ├── marketplace_ops.py # Marketplace
│   ├── placeholder_ops.py # Placeholders
│   ├── analyzer_ops.py    # Análise
│   ├── decision_engine.py # Engine de decisão
│   ├── dynamic_groups.py  # Grupos dinâmicos
│   ├── editor_config.py   # Config do editor
│   ├── vscode_config.py   # Config VS Code
│   ├── cache_utils.py     # Cache
│   ├── rate_limiter.py    # Rate limiter
│   ├── friendly_errors.py # Erros amigáveis
│   └── rollups.py         # Rollups
│
├── resources/
│   ├── game_patterns.py   # 17 gêneros de jogos
│   └── prompts.py         # 11 MCP Prompts
│
├── templates/             # Templates GDScript (Jinja2)
│   ├── player_2d_controller.gd
│   ├── enemy_chase_basic.gd
│   ├── paddle.gd
│   ├── bouncing_ball.gd
│   └── game_manager_singleton.gd
│
├── addons/
│   ├── mcp_addon/         # Plugin Godot (WebSocket 9082)
│   │   ├── plugin.cfg     # v3.2.1
│   │   └── mcp_addon.gd   # VERSION "3.2.1"
│   └── mcp_runtime_bridge/ # Runtime Bridge (TCP 8790)
│       └── runtime_bridge.gd  # Autoload MCPRuntimeBridge
│
├── classdb_cache/
│   └── extension_api.json # API Godot 4.7 (1074 classes)
│
├── art_cache/flux/        # Cache de arte FLUX
├── recordings/            # Gravações de playtest
├── temp_art/              # Arte temporária
├── workflow_logs/         # Logs de workflow
│
└── Documentação:
    ├── README.md           # Visão geral + instalação
    ├── ARQUITETURA_MCP.md  # Arquitetura detalhada
    ├── GUIA_CONEXAO.md     # Como conectar Godot
    ├── GUIA_INSTALACAO.md  # Instalação passo a passo
    ├── CHANGELOG.md        # Histórico de versões
    ├── LEARNINGS.md        # 16 regras anti-padrão (R1-R16)
    ├── NEXT_SESSION.md     # Retomada de sessão
    ├── MCP_ESTADO_ATUAL.md # Este arquivo
    └── AUDITORIA-PENDENCIAS-RESPOSTAS.md  # Respostas da auditoria
```

---

## 🔌 PORTAS E CONEXÕES

| Porta | Serviço | Tipo | Requer Godot? | Status |
|-------|---------|------|---------------|--------|
| 9080 | LSP | WebSocket | Sim (editor aberto) | ✅ |
| 9081 | GameBridge | WebSocket | Sim (jogo em debug) | ✅ |
| 9082 | AddonBridge | WebSocket | Sim (plugin ativo) | ✅ |
| 8790 | RuntimeBridge | TCP | Sim (jogo rodando) | ✅ |
| 6005 | DAP Debugger | WebSocket | Sim (jogo em debug) | ✅ |

---

## 🛡️ SEGURANÇA (SANDBOX)

### Status atual
- **Sandbox regex** (`gdscript_sandbox.py`) — filtro de texto, NÃO sandbox de execução isolada
- **Normalizador:** remove comentários, colapsa whitespace, resolve concatenação literal
- **24 classes bloqueadas** + **25 padrões bloqueados**
- **36/36 padrões** confirmados bloqueados (18 `write_file` + 18 `safe_write_gdscript`)

### Bypasses resolvidos
- ✅ BYPASS-2 (quebra de linha) — fechado via normalização de whitespace
- ✅ BYPASS-3 (comentários) — fechado via remoção de comentários
- ✅ BYPASS-4 (espaço antes do ponto) — fechado via normalização
- ✅ BYPASS-6 (concatenação literal) — fechado via resolução de concatenação

### Bypasses NÃO resolvidos (documentados)
- ⚠️ BYPASS-1 (concatenação via variáveis) — impossível com regex
- ⚠️ BYPASS-5 (aliasing — `var f = FileAccess`) — impossível com regex

---

## 🐛 BUGS CONHECIDOS

| ID | Descrição | Severidade | Status |
|----|-----------|-----------|--------|
| B1 | `_parse_tscn_node_refs` regex `\d+` não captura IDs alfanuméricos | Baixa | Documentado |
| B2 | `run_scripted_tests` não suportava runtime tools | Média | ✅ Corrigido |
| B3 | `dump_mcp_state` faltava `"status": "success"` | Baixa | ✅ Corrigido |
| R12 | `godot --headless --script` e `--check-only` não funcionam no Windows 4.7 | 🔴 Crítica | Documentado + workaround |

---

## 🧠 REGRAS (LEARNINGS.md)

16 regras anti-padrão documentadas:
- **R1-R2:** GDScript (var duplicada, `:=` com Dictionary)
- **R3-R4:** Game Bridge (parse errors, código simples primeiro)
- **R5-R8:** Infra (porta 9081, cenas, `--headless --quit`, `seed()`)
- **R9:** Método inexistente em classe nativa
- **R10:** Ciclo declarativo
- **R11:** Ordem de import dos handlers
- **R12:** `--headless` quebrado no Windows (AMPLIADO)
- **R13-R16:** Bridge, processos, hooks, sockets

---

## 🔗 NUCLEO

### Hooks ativos
| Hook | Tipo | Arquivo |
|------|------|---------|
| block-dangerous | PreToolUse | `.github/hooks/scripts/block-dangerous.ps1` |
| block-uncommitted | PreToolUse | `.github/hooks/scripts/block-uncommitted.ps1` |
| check-gdscript-syntax | PostToolUse | `.github/hooks/scripts/check-gdscript-syntax.ps1` |
| check-gate-failed | **Stop** | `.github/hooks/scripts/check-gate-failed.ps1` |
| pre-commit | Git | `.github/hooks/scripts/pre-commit.ps1` |

### MCP no NUCLEO
- **Local:** `c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\`
- **NÃO** está mais em `sistema/mcp-godot/` (removido)
- **NÃO** tem `refinamento-mcp/` (removido)
- **21 arquivos** no NUCLEO ainda referenciam `sistema/mcp-godot/servidor/` (docs desatualizados)

---

## 📋 PENDÊNCIAS

| Pendência | Prioridade | Bloco |
|-----------|-----------|-------|
| Sandbox: BYPASS-1 e BYPASS-5 | Média | MCP |
| NUCLEO: CLONE-DO-ZERO-NOVO-PC.md | Baixa | NUCLEO 14 |
| NUCLEO: setup-maquina.ps1 | Baixa | NUCLEO 14 |
| NUCLEO: PROTOCOLO-MULTI-MAQUINA.md | Baixa | NUCLEO 14 |
| NUCLEO: 21 arquivos com path antigo | Baixa | NUCLEO |

---

## 🚀 PARA RETOMAR

```powershell
# 1. Ativar ambiente
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1

# 2. Iniciar servidor (perfil dev = 80 tools)
python server.py --profile dev

# 3. Se precisar do Godot:
Start-Process "C:\Godot\Godot_v4.7-stable_win64.exe" -ArgumentList '--path "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\star-colony" --editor'
```

---

## ⚠️ PONTOS CRÍTICOS

1. **`godot --headless` NÃO funciona no Windows** (R12) — não use `--check-only` nem `--headless --script`
2. **`tentar_checagem_godot=false`** (padrão) — se precisar de checagem, use `validate_gdscript.py` standalone
3. **`config.json` NÃO é versionado** — use `config.json.example` como template
4. **`send_bridge_command`** só funciona com jogo rodando em debug
5. **Sandbox é regex**, não execução isolada — documentar claramente ao usuário
6. **Hooks NUCLEO são PowerShell puro** — zero dependências do MCP
