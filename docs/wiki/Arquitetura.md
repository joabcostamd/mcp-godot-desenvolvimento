# 🏗 Arquitetura

## Estrutura do Sistema

```
server.py          — Servidor MCP principal (AGENTE 01)
tools/
  *_ops.py         — Modulos de operacao (AGENTE 02)
  rollups.py       — Rollups de dominio (AGENTE 01)
  deprecated.py    — Zona de Sutura (congelada)
core/              — Nucleo do sistema (AGENTE 01)
tests/             — Testes automatizados
.github/           — CI/CD workflows
```

## Agentes

- **AGENTE 01** — Arquitetura & Core: `server.py`, `core/*`, `rollups.py`
- **AGENTE 02** — Extensoes & Qualidade: `tools/*_ops.py`, `.github/*`, `tests/*`

## Zona de Sutura

Arquivos congelados — mudancas requerem aprovacao:
- `tools/deprecated.py`
- `ROADMAP_UNIFICADO.md`
- `SUTURE_ISSUES.md`
