# EnemyPatrol — Patrulha entre Waypoints

Componente de patrulha que move o `CharacterBody2D` pai entre uma lista
de waypoints. Espera em cada ponto, faz loop ou ping-pong.

## Uso

1. Instancie `enemy_patrol.tscn` como filho de um `CharacterBody2D`
2. Adicione um `StateMachine` como irmão (opcional, para estados patrol/idle)
3. Defina `waypoints` com posições globais no inspetor
4. Ajuste `speed`, `wait_time`, `loop`, `ping_pong`

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `waypoint_reached` | Ao chegar em um waypoint | `index: int` |
| `patrol_complete` | Ao terminar a rota (sem loop/ping_pong) | — |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `waypoints` | PackedVector2Array | — | [] |
| `speed` | float | 10–2000 px/s | 100 |
| `wait_time` | float | 0–60 s | 1.0 |
| `loop` | bool | — | true |
| `ping_pong` | bool | — | false |

> **Nota:** Os waypoints são posições GLOBAIS (mundo). O pai deve ser
> `CharacterBody2D` com `move_and_slide()` no próprio `_physics_process`.
>
> **Ping-pong vs Loop:** `ping_pong=true` tem precedência — a rota vai e volta.
> Com `ping_pong=false` e `loop=true`, a rota recomeça do início ao fim.
> Com ambos `false`, a rota executa uma vez e emite `patrol_complete`.

## Dependências

- `state_machine` — opcional: se presente como sibling, sincroniza estados patrol/idle

## Exemplo de composição

```
Inimigo (CharacterBody2D)
  ├── StateMachine (Node)    ← estados patrol/idle
  ├── EnemyPatrol (este)     ← movimento da patrulha
  └── Sprite2D
```

## Referência

Fonte: Nodot (padrão de patrulha). LimboAI (FSM).
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
