# BeamLaser — Raio Contínuo Instantâneo

Componente de raio laser que causa dano por segundo enquanto atinge um alvo.
Usa `RayCast2D` para detecção instantânea e `Line2D` para o visual do raio.

## Uso

1. Instancie `beam_laser.tscn` como filho de uma arma, torre ou inimigo
2. O raio aponta na direção X local do nó (rotacione o pai para mirar)
3. Ajuste `damage_per_second`, `beam_width`, `max_range` no inspetor
4. Conecte o sinal `hitting` para efeitos visuais/sonoros

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `hitting` | A cada frame enquanto atinge | `target: Node`, `dps: float` |
| `stopped` | Quando para de atingir | — |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `damage_per_second` | float | 1–9999 dps | 30 |
| `beam_width` | float | 1–50 px | 4 |
| `max_range` | float | 10–2000 px | 500 |
| `beam_color` | Color | — | Color.RED |

> **Nota sobre colisão:** Por padrão, `collision_mask = 1` (layer 1) e
> `collide_with_areas = false`. Para detectar Hurtbox (Area2D), habilite
> `collide_with_areas = true` no inspetor. Para detectar `CharacterBody2D`
> ou `StaticBody2D`, mantenha `collide_with_bodies = true` (padrão).
>
> **Para mirar:** o raio segue o eixo X local. Rote o nó pai para mirar em
> qualquer direção. Use `set_enabled(false)` para ligar/desligar o raio.

## Dependências

- `health` — busca automaticamente por componente Health no alvo

## Exemplo de composição

```
Torre (Node2D, rotacionável)
  └── BeamLaser (este)      ← raio na direção da torre
```

## Referência

Fonte: Nodot Laser3D (adaptado para 2D com RayCast2D).
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
