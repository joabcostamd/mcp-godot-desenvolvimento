# ONDA 9 — QUARENTENA
> experimental/ ja existe (B26=True). Mover verticais nunca exercitadas.

## Fatia 9.1 — Mover verticais para experimental/
1. O que e: Identificar e mover tools nunca usadas em jogo real.
8. Como provar: Get-ChildItem experimental/ | Measure-Object
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia 9.2 — Criterio de saida da quarentena
1. O que e: Documentar que um jogo real precisou da capacidade para sair.
8. Como provar: Test-Path docs/QUARENTENA_CRITERIO_SAIDA.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]

# ONDA 10 — CONGELAR
> CI + freio de entrada + docs.

## Fatia 10.1 — CI com invariantes
1. O que e: CI rodando as invariantes em todo push.
8. Como provar: Test-Path .github/workflows/ci.yml
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia 10.2 — Freio de entrada
1. O que e: Tool nova exige justificativa escrita.
8. Como provar: python auditar.py --fatia 10.2
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 10.3 — ARQUITETURA_MCP.md do registry real
1. O que e: Documento de arquitetura gerado do codigo real.
8. Como provar: Test-Path docs/ARQUITETURA_MCP.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 10.4 — Zero contagem manual em .md
1. O que e: Substituir numeros hardcoded por referecia a MEDICAO_R7.md.
8. Como provar: findstr /S /N "236 tools 249 behaviors" *.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 10.5 — LEARNINGS.md com causas-raiz
1. O que e: Documentar licoes aprendidas.
8. Como provar: Test-Path docs/LEARNINGS.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]
