# Seeds — Jogos-Semente

Jogos mínimos completos, clonáveis e comentados. Cada seed é um ponto de
partida funcional que o usuário pode clonar com um comando (modo remix,
Fatia 1.K).

## Estrutura de uma seed

```
seeds/<nome>.json
  name                — nome do jogo
  genre               — gênero (referencia um blueprint)
  blueprint_ref       — caminho para o blueprint usado
  description         — descrição em PT
  scenes[]            — cenas que compõem o jogo
  behaviors_used[]    — behaviors instanciados
  assets[]            — assets com caminho e licença
  estimated_playtime  — tempo estimado de jogo (minutos)
  difficulty          — fácil | médio | difícil
```

## Seeds planejadas (1 inicial + 3 na ONDA 2)

- `breakout.json` — Breakout completo (já implementado e testado)

## Regras

- Toda seed referencia um blueprint existente.
- Assets de seed precisam de licença explícita (ver Fatia 2.AL, 2.AM).
- Seed é ponto de partida, não produto final — o usuário modifica depois.
