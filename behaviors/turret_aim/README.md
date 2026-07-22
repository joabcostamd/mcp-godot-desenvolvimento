# TurretAim — Torre que Mira e Atira

Node2D que rotaciona suavemente para seguir um alvo (grupo "player")
e dispara projéteis via `FireRate` + `Projectile`. Base para torres.

## Uso

1. Instancie `turret_aim.tscn` como filho de uma torre ou estrutura
2. Adicione `FireRate` como sibling para controlar cadência
3. O alvo é detectado automaticamente (grupo "player") ou use `set_target()`
4. Ajuste `rotation_speed`, `detection_range`, `aim_tolerance_deg`

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `target_locked` | Mira estabilizada no alvo | `target: Node2D` |
| `target_lost` | Alvo saiu do alcance | — |
| `fired` | Disparou projétil | `projectile: Node2D` |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `rotation_speed` | float | 0.1–20 rad/s | 3.0 |
| `detection_range` | float | 50–3000 px | 400 |
| `predict_movement` | bool | — | false |
| `aim_tolerance_deg` | float | 0.5–45° | 5.0 |

## Dependências

- `fire_rate` — controla cadência de disparo
- `projectile` — projétil disparado

## Exemplo de composição

```
Torre (Node2D)
  ├── TurretAim (este, Node2D)  ← rotaciona e mira
  ├── FireRate (Node)           ← cadência
  └── Sprite2D
```

## Referência

Fonte: Tower defense pattern.
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
