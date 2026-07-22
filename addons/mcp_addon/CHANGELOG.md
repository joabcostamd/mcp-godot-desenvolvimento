# Changelog — MCP Godot Agent (addon)

Todas as mudancas notaveis do addon estao documentadas aqui.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e o versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

## [3.2.1] — 2026-07-21

### Adicionado
- Editor Visual de Behavior Trees (`mcp_bt_editor/`) — 16 features, 100% GDScript
- Paleta com 249 behaviors arrastaveis
- Debugger ao vivo via WebSocket 9082
- Exportacao GDScript a partir do grafo visual

### Melhorado
- plugin.cfg com metadados completos para AssetLib
- README.md bilingue (PT/EN) com instrucoes e exemplos

## [3.2.0] — 2026-07-20

### Adicionado
- Dock MCP no editor Godot (`mcp_dock/`) — 3 zonas: progresso, diagnosticos, botoes
- Protocolo JSON-RPC 2.0 sobre WebSocket (porta 9082)
- UndoRedo nativo do editor integrado
- 249 behaviors no arsenal com behavior.json, .tres, testes GdUnit4

## [3.0.0] — 2026-07-18

### Adicionado
- WebSocket bridge inicial para o servidor MCP Python
- Operacoes no editor com UndoRedo nativo
- Lancamento inicial do addon
