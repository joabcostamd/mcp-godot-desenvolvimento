# Guia de Migração — Vindo de outras ferramentas

> Para quem já usa Godot e quer migrar para o MCP Godot Agent.

## Vindo do Nodot

Nodot (405 ⭐) é uma biblioteca de composição de nós para Godot 4.

| Nodot | MCP Godot Agent |
|-------|-----------------|
| `Nodot3D` / `Nodot2D` | Behaviors 2D (249 componentes) |
| `Character3D` | `player_controller` + `health` |
| `Projectile3D` | `projectile` |
| `Spawner3D` | `spawner_wave` |
| `AudioManager` | `audio_manager` |
| `SaveManager` | `save_load` |
| Sem editor visual | ✅ **Editor Visual de BT** (GraphEdit) |
| 4 exemplos (FPS, RTS, Platformer, MP) | 4 exemplos + 5 templates |

**Como migrar:** Substitua nós Nodot por behaviors equivalentes. A API de sinais
é compatível (ambos usam `signal` do Godot).

## Vindo do LimboAI

LimboAI (2.9k ⭐) é um framework de Behavior Trees e State Machines em C++.

| LimboAI | MCP Godot Agent |
|---------|-----------------|
| BTTask, BTCondition, BTAction | `behavior_tree` executor + 249 behaviors |
| BTStateMachine | `state_machine` behavior |
| Blackboard | `blackboard` behavior |
| Editor visual (Gameplay > LimboAI) | ✅ **Editor Visual dock** (Project > MCP BT Editor) |
| C++ (GDExtension) | 100% GDScript |

**Como migrar:** Árvores LimboAI são compatíveis conceitualmente. Recrie a árvore
no editor visual do MCP. Behaviors equivalentes cobrem a maioria dos nós.

## Vindo do Phantom Camera

Phantom Camera (1.5k ⭐) é um addon de câmera para Godot.

| Phantom Camera | MCP Godot Agent |
|---------------|-----------------|
| `PCamGlued` | `camera_follow` |
| `PCamFramed` | `camera_framed` |
| `PCamPath` | `camera_path` |
| `PCamLookAt` | `camera_lookat` |
| `PCamShake` | `camera_shake` |

**Como migrar:** 1:1. Behaviors com nomes equivalentes, mesma API de parâmetros.

## Vindo do Dialogic

Dialogic (3.5k ⭐) é um sistema de diálogo para Godot.

| Dialogic | MCP Godot Agent |
|----------|-----------------|
| Timeline | `dialogue` behavior |
| Character portraits | `character_portrait` (visual novel template) |
| Choices | `choice_system` (visual novel template) |
| Editor visual próprio | Integrado no Scene Tree (composição) |

**Como migrar:** O MCP adota composição em vez de timeline. Cada personagem é um
nó com `dialogue` + `interactable`. Diálogos são orquestrados por sinais.

## Vindo do Beehave

Beehave (1.8k ⭐) é um addon de Behavior Trees em GDScript.

| Beehave | MCP Godot Agent |
|---------|-----------------|
| 28 nós BT (Sequence, Selector, etc.) | `behavior_tree` executor |
| Blackboard | `blackboard` behavior |
| Editor visual básico | ✅ **Editor Visual completo** (16 features) |

**Como migrar:** Direto. O executor BT do MCP suporta Sequence, Selector e ações
customizadas. Recrie a árvore no editor visual.

## Vindo do Godot puro (sem addons)

Se você usava Godot sem nenhum addon de composição:

| Godot Puro | MCP Godot Agent |
|-----------|-----------------|
| Scripts monolíticos | Composição de behaviors (nós filhos) |
| `_process()` manual | Event-driven (87% dos behaviors sem `_process`) |
| Cópia/cola entre projetos | Behaviors plugáveis com `.tres` |
| Testes manuais | GdUnit4 + 249 test_*.gd |
| Sem editor visual | ✅ Editor Visual de BT + Dock MCP |

**Como migrar:** Extraia a lógica dos seus scripts para behaviors. Ex:
```gdscript
# Antes (Godot puro)
func _process(delta):
    if health <= 0:
        die()

# Depois (MCP)
# Adicione o behavior 'health' como filho
# Conecte o sinal 'died' à sua função
$Health.died.connect(die)
```
