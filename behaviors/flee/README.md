# Flee — Fuga Condicional

Componente que faz o `CharacterBody2D` pai fugir de uma ameaça quando
a condição é atendida: vida baixa, ao tomar dano, ou sempre.

## Uso

1. Instancie `flee.tscn` como filho de um `CharacterBody2D`
2. Adicione `Health` e `StateMachine` como siblings (opcional)
3. O alvo é detectado automaticamente (grupo "player") ou defina com `set_threat()`
4. Ajuste `flee_condition`, `flee_speed`, `safe_distance`

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `fleeing` | Começa a fugir | — |
| `safe` | Distância segura atingida | — |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `flee_speed` | float | 10–2000 px/s | 200 |
| `safe_distance` | float | 50–5000 px | 400 |
| `flee_condition` | String | — | "health_below_30%" |
| `health_threshold_pct` | float | 0.0–1.0 | 0.3 |

## Condições de fuga

| Valor | Comportamento |
|-------|--------------|
| `"always"` | Foge sempre |
| `"health_below_30%"` | Foge quando HP < threshold% do máximo |
| `"on_damage"` | Foge ao tomar qualquer dano |

## Dependências

- `health` — para condições baseadas em vida
- `state_machine` — opcional: sincroniza estados flee/safe

## Exemplo de composição

```
Inimigo (CharacterBody2D)
  ├── Health (Node)          ← vida
  ├── StateMachine (Node)    ← estados flee/safe/idle
  ├── Flee (este)            ← fuga condicional
  └── Sprite2D
```

## Referência

Fonte: Padrão IA de fuga (flee steering).
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
