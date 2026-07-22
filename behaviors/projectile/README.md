# Projectile — Projétil Linear

Componente de projétil que se move em linha reta, causa dano ao colidir
com alvos que tenham um componente `Health`, e se autodestroi.

## Uso

1. Instancie `projectile.tscn` como filho de um spawner ou arma
2. Chame `set_direction(dir)` ou `set_target(node)` para mirar
3. Ajuste `damage`, `speed`, `lifetime`, `max_distance` no inspetor
4. Conecte o sinal `hit` para efeitos visuais/sonoros

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `hit` | Ao colidir com algo | `target: Node`, `damage_dealt: int` |
| `expired` | Tempo ou distância esgotados | — |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `speed` | float | 10–2000 px/s | 400 |
| `damage` | int | 1–9999 | 10 |
| `lifetime` | float | 0–60s (0=∞) | 5.0 |
| `max_distance` | float | 0–10000px (0=∞) | 1000 |
| `piercing` | bool | — | false |

## Dependências

- `health` — busca automaticamente por componente Health no alvo

## Exemplo de composição

```
Arma (Node2D)
  ├── ProjectileSpawner (Node)    ← behavior futuro
  │     └── Projectile (este)     ← instanciado a cada disparo
  └── Sprite2D
```

## Referência

Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
