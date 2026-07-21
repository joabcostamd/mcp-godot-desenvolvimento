# PROXIMA SESSAO

## Resumo
Sessao de 2026-07-21: ONDA 1 avancou de 15/17 para 16/17.
Fatia concluida: 1.P (telemetria opt-in do MCP).
Novo modulo: tools/mcp_telemetry_ops.py (574 linhas, zero dependencias).
Hook track_mcp_event em call_tool (fail-open). Pesquisa externa em docs/PESQUISA_EXTERNA.md secao 6.

## Estado
- Versao: 3.5.1 | ONDA 1: 16/17 | Commit: 19da07d

## Ultima tarefa
- 1.P: Telemetria opt-in do MCP. Rollup mcp_telemetry_manage, consentimento desligado por padrao, JSONL local, zero envio externo, zero PII.

## Pendencias
- [ ] 1.Q — Historico de versoes jogaveis [SENIOR] (alta — ULTIMA da ONDA 1)
- [ ] ONDA 2 — 30 behaviors, 3 blueprints, 3 seeds (futuro)

## Arquivos-chave
- server.py, tools/mcp_telemetry_ops.py, core/tool_definitions.py, CONTRACT_SNAPSHOT.json

## Fluxo sugerido
1. Leia .session/NEXT_SESSION.md
2. Rode auditar.py
3. Continue de 1.Q (ultima fatia da ONDA 1)

## Decisoes da sessao
- Telemetria 100%% local — zero envio externo, export manual
- Formato JSONL (append-only) + summary agregado
- Padrao identico ao budget_ops (hook fail-open, threading.Lock, estado por projeto)
- Consentimento DESLIGADO por padrao (.mcp_telemetry_consent.json)

## Atencao
- C5 (orcamento) e pre-existente — 8 fases overflow, responsabilidade da Fatia 0.7
- Agente 2 ativo em agente2/behaviors-onda2 (10 behaviors)
- 1.Q e [SENIOR] — ultima fatia antes da ONDA 2
