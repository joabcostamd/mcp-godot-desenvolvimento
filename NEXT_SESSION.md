# NEXT_SESSION.md — MCP Godot Agent

**Sessao:** 2026-07-19 (S12) | **48 tools, 30 rollups**

## Progresso

| Camada | Status |
|---|---|
| C1 (Exp Dev) | ✅ 16/16 |
| C2 (Testes) | 6/7 (2.5 escalada) |
| C3 (Criacao) | 4/16 (3.1-3.4 escaladas) |

## music_manage (4 ops)
- `generate` — API MiniMax
- `make_seamless_loop` — WAV loop
- `place_and_normalize` — cena + bus + volume
- `bind_to_event` — 8 eventos de jogo

## ⚠️ PROBLEMA CRÍTICO: OneDrive reverte arquivos

O projeto está em `OneDrive\Documentos\...`. O OneDrive sincroniza com a nuvem
e RESTAURA versões antigas dos arquivos .py, .json e .md após cada edição.

**Solução:** Mover o projeto para `C:\Users\joabc\Dev\projetos\mcp-godot-desenvolvimento`
( fora do OneDrive). Isso elimina 100% das reversões.

## Comandos
```powershell
.\\.venv\\Scripts\\Activate.ps1
python auditar.py --fatia <N> --skip-c5
```
```
- `CONTEXTO_PROJETO_MCP_GODOT.md` — visão geral completa
- `SESSION_SUMMARY_2026-07-17.md` — resumo histórico da sessão anterior

### Comandos Disponíveis

| Comando | Função |
|---|---|
| `/plan` | Planejar próxima fatia (lê roadmap, verifica suposições, monta plano) |
| `/act` | Implementar fatia (executa plano, audita C1-C6, grava progresso) |

## ⚡ RESUMO DO ESTADO ATUAL

| O quê | Status |
|-------|--------|
| Fase 1 (Features 1-10) | ✅ Completa e validada |
| Teste end-to-end (Breakout) | ✅ 0% correção manual |
| Critério de parada (~15-20%) | ✅ Atingido (0%) |
| Pendências conhecidas | Nenhuma |
| Perfil padrão | `full` (Opção C: CORE 27 + fase, max 92 tools) |

## 🔧 MUDANÇAS NÃO COMMITADAS (7 arquivos)

```
CONTEXTO_PROJETO_MCP_GODOT.md — documento de contexto completo
server.py                     — Opção C + B + Features 9/10 + logging + schema
tools/balance_ops.py          — wave_generate: normalização list[str] -> list[dict]
tools/export_ops.py           — MIN_SCORE 6->7
tools/orchestrator.py         — create_entity/entities: assinaturas args:dict
tools/phase_ops.py            — get_next_step() (Feature 10)
tools/test_ops.py             — sys.modules.get (evita deadlock)
```

## 🎯 DECISÃO PENDENTE

Fase 1 completa. Fase 2 é expansão (C#/.NET, i18n, CI/CD, etc.) — não há nada quebrado.
