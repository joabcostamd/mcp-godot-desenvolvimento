# EnemyChase — Perseguição ao Jogador

**PT:** Node filho de CharacterBody2D que persegue o jogador (grupo `"player"`) quando dentro do `chase_range`. Desiste e para quando o jogador sai do `lose_range`. Emite `target_acquired`/`target_lost` nas transições.

**EN:** Node child of CharacterBody2D that chases the player (group `"player"`) when within `chase_range`. Gives up and stops when the player exceeds `lose_range`. Emits `target_acquired`/`target_lost` on transitions.

## Uso Rápido

```gdscript
# Enemy (CharacterBody2D)
#   ├── Health
#   ├── Hurtbox
#   └── EnemyChase

var chase := EnemyChase.new()
chase.speed = 150.0
chase.chase_range = 300.0
chase.lose_range = 500.0
add_child(chase)

# Alternativa: definir alvo manualmente
chase.set_target(some_node)
```

## ⚠️ Requisitos
- O pai DEVE ser `CharacterBody2D`.
- O jogador DEVE estar no grupo `"player"` (ou use `set_target()`).
- `lose_range` deve ser >= `chase_range` para evitar oscilação.
- O behavior modifica `velocity` do pai — não chame `move_and_slide()` dentro do behavior.
