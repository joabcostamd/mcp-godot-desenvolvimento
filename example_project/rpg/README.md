# MCP Example — RPG Top-Down 2D

RPG de acao top-down construido com o **MCP Godot Agent**.
20 behaviors do arsenal de 249 componentes.

## Genero
RPG Top-Down 2D (Zelda-like)

## Behaviors Usados (20)

| Behavior | Proposito |
|----------|-----------|
| `player_topdown` | Movimento 8 direcoes (WASD) |
| `health` | Vida do jogador e inimigos |
| `hitbox` | Area de ataque da espada |
| `hurtbox` | Area que recebe dano |
| `enemy_chase` | Slime persegue ao detectar |
| `enemy_patrol` | Guarda patrulha area |
| `xp_level` | Ganhar XP e subir de nivel |
| `character_stats` | Forca, Defesa, Velocidade |
| `inventory` | Mochila com itens |
| `currency` | Moedas de ouro |
| `shop` | Loja para comprar pocoes |
| `dialogue` | Conversas com NPCs |
| `quest` | Missoes com objetivos |
| `interactable` | Objetos e NPCs interagiveis |
| `save_load` | Salvar e carregar progresso |
| `camera_follow` | Camera segue o jogador |
| `health_bar` | Barra de vida sobre inimigos |
| `floating_text` | Numeros de dano flutuantes |
| `screen_shake` | Tremer tela em hits criticos |
| `day_night_cycle` | Ciclo dia/noite visual |

## Controles

- **WASD / Setas** Mover
- **Espaco** Atacar
- **E** Interagir
- **I** Inventario
- **ESC** Pausar

## Missoes Exemplo

1. **Slime Exterminator** — Mate 5 slimes. Recompensa: 50 ouro + 100 XP.
2. **Pocao do Ferreiro** — Entregue 3 ervas ao ferreiro. Recompensa: Espada +1.

## Estrutura

```
example_project/rpg/
  project.godot  seed.json  README.md
  scenes/        menu.tscn  game.tscn  dialogue.tscn  inventory.tscn  game_over.tscn
  scripts/       rpg_main.gd
```

## Assets

Placeholders geometricos. Para assets finais: [Kenney.nl Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) (CC0).

## Licenca

MIT
