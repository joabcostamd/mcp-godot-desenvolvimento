# Quarentena — Critério de Saída

**Versão:** 1.0 · **Data:** 2026-07-23 · **Onda:** 9.2

## Regra

Uma tool ou domínio sai da quarentena (`experimental/`) quando:

1. **Um jogo real precisou da capacidade.** Não basta teste unitário ou用例 sintético.
   Evidência: commit em repositório de jogo (star-colony, shardbreaker, etc.)
   que usa a tool com sucesso.

2. **A tool passou 30 dias sem bug report.** Desde a entrada na quarentena,
   zero issues abertas com a tag da tool.

3. **Cobertura de testes ≥ 80%.** Medido por `pytest --cov` no módulo da tool.

## Processo

```
Nova tool → experimental/ (status: quarentena)
    ↓ 30 dias + jogo real usou + testes ≥ 80%
Tool promovida → domains/ ou tools/ (status: stable)
```

## Estado atual

- `experimental/` existe e está vazio (ou contém apenas testes).
- Nenhuma tool está em quarentena ativa.
- Critério aplica-se a novas tools adicionadas após ONDA 9.
