# PROXIMA SESSAO

## Resumo
Sessao de 2026-07-20: ONDA 1 avancou de 11/17 para 15/17.
Fatias concluidas: 1.K (remix), 1.L (vitrine 32 generos), 1.M (skills/modo guiado), 1.N (llms.txt + README bilingue), 1.O (offline).
32 game patterns, _SYNONYMS 120+, fallback GAME_PATTERNS, init.py com copy_prompts_to_project e check_internet.

## Estado
- Versao: 3.5.0 | ON DA 1: 15/17 | Commit: 156ed74

## Ultima tarefa
- 1.O: Degradacao elegante sem internet (check_internet + friendly_errors socket)

## Pendencias
- [ ] 1.P — Telemetria opt-in [SENIOR] (alta)
- [ ] 1.Q — Historico de versoes [SENIOR] (media)
- [ ] ONDA 2 — 30 behaviors, 3 blueprints, 3 seeds (futuro)

## Arquivos-chave
- server.py, init.py, tools/quickstart_ops.py, resources/game_patterns.py

## Fluxo sugerido
1. Leia .session/NEXT_SESSION.md
2. Rode auditar.py
3. Continue de 1.P ou va para ONDA 2

## Decisoes da sessao
- 32 generos (nao 17) — cobertura ~100%% dos generos 2D viaveis
- .prompt.md no .github/prompts/ do projeto, nao %%APPDATA%%
- Fallback GAME_PATTERNS no _match_blueprint quando blueprints nao cobrem

## Atencao
- Apenas 3 blueprints para 32 generos — gap conhecido, Onda 2 resolve
- Agente 2 ativo em agente2/behaviors-onda2 (10 behaviors)
