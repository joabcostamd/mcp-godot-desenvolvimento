# MCP Example — Shooter (Survivors-like)

Jogo survivors-like top-down construido com o **MCP Godot Agent**.
14 behaviors do arsenal de 249 componentes.

## Genero
Survivors-like Top-Down (Vampire Survivors / Brotato)

## Behaviors Usados (14)

| Behavior | Proposito |
|----------|-----------|
| `player_topdown` | Movimento 8 direcoes (WASD) |
| `health` | Vida do jogador |
| `auto_aim` | Mira automatica no inimigo mais proximo |
| `fire_rate` | Cadencia de tiro automatica |
| `projectile` | Projetil que causa dano |
| `enemy_chase` | Inimigos perseguem o jogador |
| `spawner_wave` | Ondas de inimigos (crescente) |
| `xp_level` | Coletar XP -> Subir nivel |
| `upgrade` | Escolher upgrade ao subir nivel |
| `object_pool` | Pool de projeteis e inimigos |
| `defeat_condition` | HP = 0 -> derrota |
| `floating_text` | Numeros de dano |
| `screen_shake` | Tremer tela em dano pesado |
| `camera_follow` | Camera segue o jogador |

## Controles

- **WASD / Setas** Mover
- **Tiro** Automatico (auto-aim)
- **ESC** Pausar / Upgrade

## Upgrades Disponiveis (8)

| Nome | Efeito |
|------|--------|
| +Dano | +25% dano por projetil |
| +Velocidade | +15% velocidade |
| +Cadencia | -20% intervalo entre tiros |
| +Projeteis | +1 projetil extra |
| +Vida | +20 HP maximo |
| +Critico | +10% chance de critico |
| Magnetico | +50% raio de coleta XP |
| Escudo | 1 hit extra |

## Estrutura

```
example_project/shooter/
  project.godot  seed.json  README.md
  scenes/        menu.tscn  game.tscn  upgrade.tscn  game_over.tscn
  scripts/       shooter_main.gd
```

## Assets

Placeholders geometricos. Para assets finais: [Kenney.nl](https://kenney.nl) (CC0).

## Licenca

MIT
