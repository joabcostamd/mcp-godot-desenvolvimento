# LIMPEZA_DOCS.md — Plano de Limpeza de Documentos

**Data:** 2026-07-23
**Escopo:** Documentação solta na raiz e em docs/ — NÃO toca em código (.py, .gd, .tscn), behaviors/, .github/instructions/, .github/skills/, .github/roadmap/

---

## CATEGORIA A — MANTER NA RAIZ (15 arquivos)

| Arquivo | Motivo |
|---|---|
| AGENTS.md | Lido pelo Copilot automaticamente |
| README.md | Documento principal do projeto |
| README.en.md | Versão em inglês |
| HANDOFF.md | Passagem de bastão entre sessões |
| CHANGELOG.md | Histórico de versões |
| CHECKPOINT.md | Checkpoint de segurança |
| SUTURE_ISSUES.md | Canal de conflitos entre agentes |
| ROADMAP_DEFINITIVO.md | Ponteiro canônico para REORG_ROADMAP.md |
| LICENSE | Licença MIT |
| SECURITY.md | Política de segurança |
| CODE_OF_CONDUCT.md | Código de conduta |
| CONTRIBUTING.md | Guia de contribuição |
| MEDICAO_R7.md | Medição R7 — ferramentas por fase |
| INVENTARIO_DOCS.md | Inventário gerado nesta sessão |
| llms.txt | Índice para IAs (padrão llmstxt.org) |

---

## CATEGORIA B — ARQUIVAR (11 arquivos → journal/arquivo-morto/2026-07-23/)

| # | Arquivo | KB | Versionado? | Motivo |
|---|---|---|---|---|
| 1 | docs/MASTER_IMPLEMENTATION_ROADMAP.md | 86.1 | SIM (git mv) | Substituído por REORG_ROADMAP.md (declarado no cabeçalho) |
| 2 | RECON_MCP.md | 496.2 | NÃO | Artefato de reconhecimento — já cumpriu o papel, virou REORG_ROADMAP.md |
| 3 | RECON_SLIM.md | 297.3 | NÃO | Artefato de reconhecimento — já cumpriu o papel |
| 4 | ROADMAP.md (raiz) | 12.0 | NÃO (gitignored) | Auto-gerado por community_manage, gitignored, não referenciado por comandos |
| 5 | fases.txt | 0.4 | NÃO | Debug dump — sem referência ativa |
| 6 | medir.txt | 1.5 | NÃO | Artefato de medição — sem referência ativa |
| 7 | simbolos.txt | 1.0 | NÃO | Debug dump — sem referência ativa |
| 8 | saida_instalador.txt | 6.3 | NÃO | Output de instalador — regenerável, sem referência ativa |
| 9 | _m2.txt | 11.3 | NÃO | Desconhecido — sem referência ativa |
| 10 | prova_R1.txt | 40.8 | NÃO | Prova de fatia R1 — valor histórico, já registrada no commit |
| 11 | prova_regressao_R1.txt | 0.6 | NÃO | Prova de regressão R1 — valor histórico |

---

## CATEGORIA C — DELETAR (7 arquivos)

| # | Arquivo | KB | Versionado? | Motivo | Prova de regenerabilidade |
|---|---|---|---|---|---|
| 1 | audit_out.txt | 9.1 | SIM (git rm) | Saída de auditar.py | `python auditar.py --fatia F5 > audit_out.txt` |
| 2 | audit_out_f2.txt | 8.0 | SIM (git rm) | Saída de auditar.py | `python auditar.py --fatia F2 > audit_out_f2.txt` |
| 3 | audit_out_f5.txt | 1.2 | SIM (git rm) | Saída de auditar.py | `python auditar.py --fatia F5 > audit_out_f5.txt` |
| 4 | audit_result.json | 1.0 | NÃO | Saída de auditar.py | `python auditar.py --fatia F5 --output audit_result.json` |
| 5 | .roadmap_progress.json.backup-20260723-092102 | 76.1 | NÃO | Backup antigo (mantidos 2 mais recentes) | N/A — backup redundante |
| 6 | .roadmap_progress.json.backup-r2-20260723-112621 | 77.2 | NÃO | Backup antigo | N/A — backup redundante |
| 7 | .roadmap_progress.json.backup-r2-20260723-112728 | 77.2 | NÃO | Backup antigo | N/A — backup redundante |

**Backups mantidos (2 mais recentes):**
- .roadmap_progress.json.backup-r2-20260723-112752 (77.2 KB)
- .roadmap_progress.json.backup-r2-20260723-112802 (77.2 KB)
