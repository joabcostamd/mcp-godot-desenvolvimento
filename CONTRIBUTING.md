# Contribuindo — MCP Godot Agent

Obrigado por contribuir! Este documento explica como.

## Regras de ouro

1. **Uma fatia por vez.** Nunca comece N+1 antes de N estar aprovada.
2. **Prova, nunca alegação.** `git diff` com `@@`, código colado, teste rodado.
3. **Nunca commite sozinho.** Proponha o commit e espere aprovação.

Leia [`AGENTS.md`](AGENTS.md) para entender como as IAs trabalham neste repositório.

## Como contribuir

1. Leia [`ROADMAP_DEFINITIVO.md`](ROADMAP_DEFINITIVO.md) — o plano mestre
2. Escolha uma fatia marcada `[AUTO]` ou discuta uma `[SÊNIOR]`
3. Rode `/plan` no Copilot para planejar
4. Após aprovação, rode `/act` para implementar
5. Rode `python auditar.py` — o portão precisa passar
6. Proponha o commit e aguarde revisão

## Padrão de commit

```
<tipo>(<escopo>): <descrição curta>
```

Tipos: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`

## Como rodar os testes

```bash
python auditar.py --fatia X.Y
python -c "from tools.registry_validation import validate_tool_registry_consistency; print(validate_tool_registry_consistency())"
```

## Código de Conduta

Veja [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
