# Flocking — Comportamento de Bando (Boids)

Aplica 3 forças de steering no `CharacterBody2D` pai: separação,
alinhamento e coesão. Vizinhos detectados via grupo (`flock_group`).

## Uso

1. Instancie `flocking.tscn` como filho de um `CharacterBody2D`
2. Adicione todos os NPCs do bando ao grupo `flock_group` (padrão: "flock")
3. Ajuste os pesos (`separation_weight`, etc.) e `max_speed`

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `separation_weight` | float | 0–10 | 1.5 |
| `alignment_weight` | float | 0–10 | 1.0 |
| `cohesion_weight` | float | 0–10 | 1.0 |
| `neighbor_radius` | float | 10–1000 px | 100 |
| `max_speed` | float | 10–2000 px/s | 150 |
| `flock_group` | String | — | "flock" |

## Dependências

Nenhuma.

## Exemplo de composição

```
NPC (CharacterBody2D, grupo "flock")
  ├── Flocking (este)    ← steering de bando
  └── Sprite2D
```

## Referência

Fonte: Craig Reynolds — Boids (1986).
Padrão: *Game Development Patterns with Godot 4*.
