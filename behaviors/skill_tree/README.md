# SkillTree — Arvore de Habilidades

Sistema de nos conectados com custo e prerequisitos. Integra CharacterStats.

## Quick Start

```gdscript
var tree := SkillTree.new()
tree.available_points = 5
tree.add_node("str1", "Forca I", 1, [], {"strength": 5})
tree.add_node("str2", "Forca II", 2, ["str1"], {"strength": 10})
tree.unlock_node("str1")
tree.unlock_node("str2")
```

## Metodos

| Metodo | Descricao |
|--------|-----------|
| `add_node(id, name, cost, connections, bonuses)` | Adiciona no |
| `unlock_node(id)` | Desbloqueia (gasta pontos) |
| `can_unlock(id)` | Verifica se pode desbloquear |
| `reset_tree()` | Reseta tudo (devolve pontos) |
| `add_points(n)` | Adiciona pontos |
| `get_total_spent()` | Total gasto |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `node_unlocked` | `node_id: String` | No desbloqueado |
| `tree_reset` | — | Arvore resetada |
| `points_changed` | `available: int` | Pontos alterados |
