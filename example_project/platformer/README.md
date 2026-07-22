# MCP Example — Platformer 2D

Jogo de plataforma 2D side-scrolling construido com o **MCP Godot Agent**.
15 behaviors do arsenal de 249 componentes.

## Genero
Plataforma 2D (Mario-like)

## Behaviors Usados (15)

| Behavior | Proposito |
|----------|-----------|
| `player_controller` | Movimento horizontal, pulo, gravidade |
| `health` | 3 vidas, dano, invencibilidade temporaria |
| `enemy_patrol` | Inimigo anda entre waypoints |
| `enemy_chase` | Inimigo persegue ao detectar jogador |
| `collectable` | Moedas e power-ups coletaveis |
| `checkpoint` | Ponto de respawn (bandeira) |
| `victory_condition` | Chegar ao fim da fase |
| `defeat_condition` | Todas as vidas perdidas |
| `camera_follow` | Camera segue jogador com damping |
| `score` | Pontuacao por moedas e inimigos |
| `health_bar` | HUD de vida (coracoes) |
| `damage_over_time` | Espinhos causam dano continuo |
| `moving_platform` | Plataformas que se movem |
| `screen_shake` | Tremer tela ao tomar dano |
| `audio_manager` | SFX de pulo, moeda, dano |

## Controles

- **← →** Mover
- **Espaco** Pular
- **ESC** Pausar
- **Gamepad:** D-Pad mover, A pular

## Estrutura

```
example_project/platformer/
  project.godot
  seed.json
  README.md
  scenes/
    menu.tscn        — Menu inicial
    game.tscn        — Fase principal
    victory.tscn     — Tela de vitoria
    game_over.tscn   — Tela de derrota
  scripts/
    platformer_main.gd — Script principal (conecta behaviors)
```

## Como usar

1. Abra esta pasta no Godot 4.7 como um projeto
2. Pressione F5 para jogar
3. Ou use o MCP para clonar: "Quero um jogo de plataforma 2D..."

## Assets

Placeholders geometricos coloridos. Para assets finais, use:
- [Kenney.nl Platformer Pack](https://kenney.nl/assets/platformer-pack-redux) (CC0)

## Licenca

MIT — veja `LICENSE` na raiz do projeto.
