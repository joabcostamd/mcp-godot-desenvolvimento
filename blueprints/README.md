# Blueprints — Receitas de Gênero

Definições declarativas de gêneros de jogo. Cada blueprint descreve o loop
principal, os sistemas necessários e os critérios de pronto — a IA não gera
do zero, ela instancia e parametriza um blueprint verificado.

## Estrutura de um blueprint

```
blueprints/<genero>.json
  genre              — nome do gênero
  description        — descrição em PT
  core_loop          — ciclo principal do jogo (ex: "mover → atirar → coletar")
  systems[]          — behaviors obrigatórios
  victory_condition  — como se vence
  defeat_condition   — como se perde
  progression        — como o jogo evolui
  recommended_behaviors[] — behaviors recomendados (opcionais)
  example_games[]    — jogos de referência
```

## Blueprints planejados (3 iniciais)

- `platformer.json` — Plataforma 2D (estilo Mario, Celeste)
- `topdown_shooter.json` — Tiro top-down (estilo Vampire Survivors, Enter the Gungeon)
- `puzzle.json` — Puzzle 2D (estilo Tetris, Sokoban)

## Regras

- Blueprint referencia behaviors, não os duplica.
- Gênero com menos de 3 behaviors obrigatórios é "mini-game", não gênero.
- Todo blueprint cita pelo menos 1 jogo de referência real.
