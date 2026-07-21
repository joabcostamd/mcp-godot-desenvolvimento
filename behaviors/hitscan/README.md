# Hitscan — Tiro Instantâneo

Componente de tiro instantâneo que causa dano imediato ao primeiro alvo
na linha de fogo usando `RayCast2D`. One-shot: cada chamada a `fire()`
é um disparo único.

## Uso

1. Instancie `hitscan.tscn` como filho de uma arma ou torre
2. Conecte o sinal `fire_rate.ready` ao `hitscan.fire()` para controlar cadência
3. O tiro segue o eixo X local — rotacione o pai para mirar
4. Conecte `hit` para efeitos de impacto, `fired` para muzzle flash

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `hit` | Ao atingir um alvo (antes de fired) | `target: Node`, `damage_dealt: int` |
| `fired` | Sempre ao final de fire() | `target: Node`, `damage_dealt: int` |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `damage` | int | 1–9999 | 25 |
| `max_range` | float | 10–3000 px | 1000 |
| `flash_duration` | float | 0.01–0.5 s | 0.05 |
| `beam_color` | Color | — | Color.YELLOW |

> **Nota sobre colisão:** Por padrão, `collision_mask = 1` e
> `collide_with_areas = false`. Habilite `collide_with_areas = true`
> para detectar Hurtbox (Area2D).
>
> **Para mirar:** o tiro segue o eixo X local. Rote o nó pai.
> Use `set_enabled(false)` para desabilitar o tiro.

## Dependências

- `health` — busca Health no alvo para aplicar dano
- `fire_rate` — controla a cadência (externo ao hitscan)

## Exemplo de composição

```
Arma (Node2D, rotacionável)
  ├── FireRate (Node)       ← controla cadência
  │     ready → Hitscan.fire()
  └── Hitscan (este)        ← executa o disparo
```

## Referência

Fonte: cluttered-code Hitscan (padrão Godot 4).
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
