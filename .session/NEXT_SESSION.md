# 🔄 PRÓXIMA SESSÃO

## Resumo
F5 concluído: 5 domínios migrados (physics, ui, shader, camera, navigation),
15 atômicas removidas. Padrão KW-only handlers. 146/148 testes passam.

## Estado
- Versão: v3.8.0 | Commit: a82c8ef | Branch: main
- 5 domínios + 37 rollups | 272 raw tools

## Pendências
- [ ] Corrigir F5.2 ui: handlers.py com re-exports → KW-only (ALTA)
- [ ] F5.6: Migrar domínio audio (MÉDIA)
- [ ] F6: Transporte invisível (BAIXA)

## Arquivos-chave
- core/tool_definitions.py — 272 raw tools
- tools/rollups.py — 37 builders
- domains/*/ — 5 domínios (manifest.py + handlers.py)

## Fluxo sugerido
1. Leia .session/NEXT_SESSION.md e /memories/repo/status.md
2. Rode pytest para baseline
3. Corrija F5.2 ui handlers
4. /plan para F5.6

## Decisões da sessão
- KW-only handlers como padrão obrigatório
- Aliases no manifest para rollups
- Commit automático pós-/act

## ⚠️ Atenção
- test_remix: 2 falhas pré-existentes (diretórios sujos)
- Rollups já existem — não recriar
