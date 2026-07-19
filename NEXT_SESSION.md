# 🔄 PRÓXIMA SESSÃO — MCP Godot Agent

## 📋 Onde paramos
- Projeto: mcp-godot-desenvolvimento | Tipo: python
- Versão: v3.4.0 | Nota QG: A
- Último documento: pendenciasMCP.md v2.1.0 (19/07/2026)
- Status: Documento mestre de backlog consolidado — 22 itens, 14 gaps, 8 KPIs

## 🎯 Próximo passo
- **Sprint 0.5 — Limpeza Imediata (~1h)**
- Objetivo: Remover 3 bridges quebradas, unificar _DEPRECATED, marcar funções internas
- Ações (6 passos):
  1. Criar diretórios backups/ e tools/
  2. Mover editor_bridge.py, bridge.py, ws_bridge.py para backup
  3. Limpar imports residuais em server.py
  4. Unificar _DEPRECATED + _DEPRECATED_H em tools/deprecated.py
  5. Marcar 69 funções com # INTERNAL: usado por <rollup>
  6. Rodar validate_tool_registry_consistency()
- Arquivos prováveis: server.py, tools/deprecated.py (novo), editor_bridge.py (remover), bridge.py (remover), ws_bridge.py (remover)

## 📂 Arquivos-chave
- `server.py` (~6500 linhas) — servidor MCP principal
- `tools/` — 74 módulos
- `pendenciasMCP.md` — 📋 documento mestre de backlog (LEIA PRIMEIRO)
- `MCP_ESTADO_ATUAL.md` — documento canônico de referência
- `README.md` — visão geral do projeto

## ⚠️ Pendências
- 3 bridges quebradas para remover (editor_bridge.py, bridge.py, ws_bridge.py)
- 69 tools depreciadas para marcar com comentários INTERNAL
- _DEPRECATED e _DEPRECATED_H duplicados — unificar
- ~15 imports de código morto para limpar
- 22 itens de backlog (B-001 a B-022) — começar pelos críticos (B-001 a B-004)

## 📝 Resumo da última sessão
- Criado pendenciasMCP.md v2.1.0 após 3 auditorias completas
- Documento consolidado com 14 gaps, 22 itens de backlog, 6 quick wins, 7 riscos, 8 KPIs, 7 anti-padrões
- Alinhado com MCP Specification 2025-11-25
- Atualizado README.md (193 tools, 74 módulos, referência ao pendenciasMCP.md)
- Publicado no GitHub: joabcostamd/mcp-godot-desenvolvimento

## 🔧 Regras do projeto
- NUNCA remover funções marcadas como # INTERNAL — são usadas pelos rollups
- Sempre usar addon_bridge.py (:9082) ou runtime_bridge_client.py (:8790)
- Nunca importar editor_bridge.py, bridge.py, ou ws_bridge.py
- Sempre rodar validate_tool_registry_consistency() após mudanças em tools
- Commits seguem formato: tipo(escopo): descrição em português

## 🎮 Para o HUMANO
- Abra o VS Code na pasta: C:\Users\joabc\Documents\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento
- Certifique-se que o MCP está rodando (settings.json: chat.mcp.autoStart: true)
- Leia pendenciasMCP.md para ver o backlog completo
- Comece pelos Quick Wins (seção 6 do documento)
