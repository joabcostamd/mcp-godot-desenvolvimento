# Health — Componente de Vida (Padrão-Ouro)

Componente plugável de vida para Godot 4.7. Adicione como nó filho de qualquer
entidade que precise tomar dano, curar ou morrer.

## Uso

1. Adicione `health.tscn` como filho do nó (inimigo, player, objeto destrutível)
2. Ajuste `max_hp` no inspetor
3. Conecte o sinal `died` para tocar animação de morte, soltar loot, etc.
4. Chame `take_damage(amount)` de qualquer script externo

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `died` | HP chega a 0 | — |
| `damage_taken` | Após tomar dano | `amount: int`, `remaining: int` |
| `healed` | Após receber cura | `amount: int`, `current: int` |
| `hp_changed` | Sempre que HP muda | `old_hp: int`, `new_hp: int` |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `max_hp` | int | 1–9999 | 100 |
| `current_hp` | int | 0–9999 | 100 |
| `invulnerable_time` | float | 0–10s | 0.0 |

## Invulnerabilidade

Se `invulnerable_time > 0`, após tomar dano o componente ignora novos danos
pelo tempo configurado. Útil para evitar dano por frame em colisões contínuas.

## Exemplo de composição

```
Inimigo (CharacterBody2D)
  ├── health (Health)       ← este componente
  ├── hitbox (Hitbox)       ← behavior futuro
  └── enemy_chase (EnemyChase) ← behavior futuro
```

## Referência

Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
Demo oficial: godot-demo-projects/2d/platformer.
