# Tooltip — Dica Flutuante

Control que exibe um tooltip ao passar o mouse sobre o parent. Conecta
`mouse_entered`/`mouse_exited` automaticamente. Cria PanelContainer + Label internos.

## Quick Start

```gdscript
# No _ready() do seu Button ou Control:
var tip := Tooltip.new()
tip.tooltip_text = "Clique para iniciar o jogo"
tip.show_delay = 0.3
add_child(tip)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `tooltip_text` | String | — | `""` | Texto exibido |
| `show_delay` | float | 0–5 | 0.5 | Atraso antes de mostrar (s) |
| `position_offset` | Vector2 | — | `(0,-40)` | Deslocamento |
| `follow_mouse` | bool | — | `true` | Segue ou não o mouse |

## Sinais

| Nome | Quando |
|------|--------|
| `tooltip_shown` | Tooltip aparece |
| `tooltip_hidden` | Tooltip desaparece |

## Edge Cases

- **Texto vazio:** não mostra tooltip
- **Sem parent Control:** não conecta sinais, mas `show_tooltip()` manual funciona
- **`show_delay = 0`:** tooltip aparece imediatamente
- **`follow_mouse = false`:** posição fixa relativa ao parent

## Fonte

Godot 4.7 ClassDB: `Control`, `PanelContainer`, `Label`, `Timer`, `mouse_entered`/`mouse_exited`.
