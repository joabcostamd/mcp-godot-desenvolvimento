# Accordion — Painel Expansível

Control com seções clicáveis. Cada seção = Button (header) + Control (conteúdo).
Toggle visibilidade ao clicar no header.

## Quick Start

```gdscript
var acc := Accordion.new()
acc.allow_multiple = true

var label1 := Label.new(); label1.text = "Conteúdo da seção 1"
var label2 := Label.new(); label2.text = "Conteúdo da seção 2"

acc.add_section("Opções", label1)
acc.add_section("Avançado", label2, true)  # começa recolhida
add_child(acc)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `animation_duration` | float | 0–2 | 0.2 | Duração da animação (s) |
| `allow_multiple` | bool | — | `false` | Várias abertas ao mesmo tempo |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `section_toggled` | `index: int, collapsed: bool` | Seção expandida/recolhida |

## Métodos

| Método | Descrição |
|--------|-----------|
| `add_section(title, content, collapsed)` | Adiciona seção, retorna índice |
| `remove_section(index)` | Remove seção |
| `toggle_section(index)` | Alterna estado |
| `collapse_all()` | Recolhe todas |
| `expand_all()` | Expande todas |
| `is_section_collapsed(index)` | Consulta estado |

## Edge Cases

- **Índice inválido:** `toggle_section()` e `remove_section()` retornam sem erro
- **`allow_multiple = false`:** expandir uma fecha as outras
- **Conteúdo com parent:** `reparent()` automático para dentro da seção

## Fonte

Godot 4.7 ClassDB: `VBoxContainer`, `Button`, `Control.visible`, `reparent()`.
