# 🔄 PRÓXIMA SESSÃO

## Resumo
ONDA 4 iniciada. 4.A (AssetLib) concluída. Pesquisa externa nível extremo sobre toda a ONDA 4 (MUNDO) concluída: distribuição, monetização, comunidade, identidade, métricas, Steam. Ordem revisada com base na pesquisa: Nome → Shardbreaker → itch.io → Comunidade → Sponsors → Métricas.

## Estado
- Versão: v3.7.0 | Commit: 702de23 (último commitado)
- Módulos: 286 tools (+1 publish_manage), 308 handlers
- Progresso: ONDA 1 ✅ 17/17 | ONDA 2 ⏳ Agente 2 | ONDA 3 ✅ 21/21 | ONDA 4 ⏳ 1/7 (4.A ✅)

## Últimas tarefas
- 4.A — publish_manage: empacotar addons para AssetLib (concluído, 18/18 testes)
- Pesquisa ONDA 4: 7 domínios mapeados, 19 oportunidades descobertas

## Pendências (ordem revisada pela pesquisa)
- [ ] 4.D — Nome e identidade do produto [SÊNIOR] — crítica: define o nome antes de publicar
- [ ] 4.E — Publicar Shardbreaker no itch.io [SÊNIOR] — a prova mais forte de marketing
- [ ] 4.B — Pacotes e templates no itch.io [AUTO]
- [ ] 4.F — Canal de comunidade (GitHub Discussions) [AUTO]
- [ ] 4.C — GitHub Sponsors com camadas [AUTO]
- [ ] 4.G — Dashboard de métricas [SÊNIOR]

## Descobertas da pesquisa (destaques)
1. Shardbreaker é a fatia que multiplica o valor de TODAS as outras — publicar ANTES de monetizar
2. Nome `mcp-godot-desenvolvimento` é repositório, não produto. Sugestão: "Saga"
3. GitHub Discussions > Discord para início (assíncrono, indexado, baixa manutenção)
4. 19 oportunidades adicionais mapeadas (API itch.io, CI/CD, landing page, badges, changelog)
5. Concorrência na AssetLib: 6 MCPs já publicados. Nosso diferencial: PT-BR, dono do processo, 285 tools

## Arquivos-chave
- docs/PESQUISA_EXTERNA.md — Seção 7: ONDA 4 completa (~500 linhas)
- .github/instructions/fontes.instructions.md — Nova seção "Distribuição e Mundo"
- HANDOFF.md — Handoff da pesquisa ONDA 4
- tools/publish_ops.py — Ferramenta de publicação (4.A)

## Fluxo sugerido
1. Leia HANDOFF.md (seção "Pesquisa ONDA 4")
2. Leia docs/PESQUISA_EXTERNA.md seção 7
3. Continue com /plan para 4.D (Nome e identidade)

## Última tarefa
- 3.A-3.K + G1-G10: Playtest, fun_report, gates, dashboard, suite completa, polimento

## Pendências
- [ ] 4.A — Publicar na AssetLib (alta)
- [ ] 4.E — Publicar o Shardbreaker (alta)
- [ ] 4.D — Nome e identidade do produto (média)
- [ ] Atualizar Agente 2 com novo estado (média)

## Arquivos-chave
- tools/playtest_ops.py (principal, +800 linhas)
- tools/fun_report_ops.py (relatório de qualidade)
- tools/personas.py (3 personas)
- core/tool_definitions.py (285 definições)

## Fluxo sugerido
1. Leia HANDOFF.md e .roadmap_progress.json
2. Rode pytest + auditar.py --skip-c5
3. Continue com /plan para ONDA 4 (4.A)

## Decisões da sessão
- Adaptar 3.C de 'MCP chama API' para 'servidor HTTP outbound' → usou urllib.request
- Adicionar 5º sinal (densidade de eventos) ao fun_report → detecta vale de tédio
- Commits automáticos após cada /act a partir da 3.E → acelera o ciclo

## ⚠️ Atenção
- 285 tools — monitorar teto (~40/fase)
- Agente 2 branch agente2/behaviors-onda2 — pode ter conflitos se fizer merge
- --headless nao funciona no Windows 4.7 (R12)
