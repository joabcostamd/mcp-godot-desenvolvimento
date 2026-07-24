"""
Skills — Recursos MCP para descoberta guiada de ferramentas.

Inspirado no GitHub MCP Server PR #2382 (Progressive Discovery).
Cada skill é um recurso skill:// que, quando lido, retorna:
1. Descrição do fluxo de trabalho
2. Lista de tools relevantes (3-5)
3. Exemplo de uso

Formato: skill://<nome>
"""
import json
from pathlib import Path

SKILLS_DIR = Path(__file__).parent

SKILLS: dict[str, dict] = {
    "criar-cena": {
        "title": "Criar Cena",
        "description": "Criar uma cena Godot (.tscn) do zero, com nós, scripts e configuração.",
        "tools": ["scene_manage", "node_manage", "file_manage"],
        "workflow": """
1. Use `scene_manage` com `op: "create"` para criar a cena base
2. Use `node_manage` com `op: "create"` para adicionar nós
3. Use `node_manage` com `op: "set_property"` para configurar propriedades
4. Use `file_manage` com `op: "inspect"` para verificar o resultado
""",
        "example": 'scene_manage(op="create", params={"scene_name": "game", "scene_type": "Node2D"})',
    },
    "criar-script": {
        "title": "Criar Script",
        "description": "Criar e anexar scripts GDScript a nós da cena.",
        "tools": ["script_manage", "lsp_manage", "safe_write_gdscript"],
        "workflow": """
1. Use `script_manage` com `op: "generate"` para gerar o código GDScript
2. Use `script_manage` com `op: "attach"` para anexar a um nó
3. Use `safe_write_gdscript` para escrever scripts com validação de sintaxe
4. Use `lsp_manage` para verificar diagnósticos do LSP
""",
        "example": 'script_manage(op="generate", params={"class_name": "Player", "extends": "CharacterBody2D"})',
    },
    "debuggar": {
        "title": "Depurar Jogo",
        "description": "Depurar o jogo em execução: breakpoints, console, screenshots.",
        "tools": ["debug_manage", "runtime_manage", "screenshot_manage"],
        "workflow": """
1. Use `runtime_manage` com `op: "run"` para iniciar o jogo
2. Use `debug_manage` para configurar breakpoints e inspecionar estado
3. Use `screenshot_manage` para capturar frames para análise visual
4. Use `debug_manage` com `op: "get_stats"` para métricas de performance
""",
        "example": 'debug_manage(op="set_breakpoint", params={"script": "player.gd", "line": 42})',
    },
    "exportar-jogo": {
        "title": "Exportar Jogo",
        "description": "Exportar o jogo para distribuição: presets, build, checklist.",
        "tools": ["export_manage", "build_csharp", "release_checklist"],
        "workflow": """
1. Use `export_manage` com `op: "list_presets"` para ver presets disponíveis
2. Use `configure_export_preset` para configurar o preset alvo
3. Use `export_manage` com `op: "build"` para gerar o executável
4. Use `release_checklist` para verificar itens pré-lançamento
""",
        "example": 'export_manage(op="build", params={"preset": "Windows Desktop", "output": "game.exe"})',
    },
    "criar-ui": {
        "title": "Criar Interface (UI)",
        "description": "Criar menus, HUD, widgets e elementos de interface.",
        "tools": ["ui_manage", "scene_manage", "node_manage"],
        "workflow": """
1. Use `ui_manage` com `op: "create_root"` para criar a base da UI
2. Use `ui_manage` com `op: "add_control"` para adicionar botões, labels, etc.
3. Use `ui_manage` com `op: "set_anchor"` para configurar âncoras responsivas
4. Use `scene_manage` para carregar a UI na cena principal
""",
        "example": 'ui_manage(op="create_root", params={"name": "MainMenu", "fullscreen": True})',
    },
    "fisica": {
        "title": "Física e Colisões",
        "description": "Configurar física: colisões, raycasts, joints, materiais.",
        "tools": ["physics_manage", "raycast_manage", "d3_manage"],
        "workflow": """
1. Use `physics_manage` com `op: "add_collision"` para adicionar colisores
2. Use `physics_manage` com `op: "set_layers"` para configurar layers/masks
3. Use `raycast_manage` para raycasts 2D/3D
4. Use `physics_manage` com `op: "set_material"` para propriedades físicas
""",
        "example": 'physics_manage(op="add_collision", params={"node": "Player", "shape": "capsule"})',
    },
    "animacao": {
        "title": "Animação",
        "description": "Criar animações: sprites, tweens, câmera, esqueleto.",
        "tools": ["anim_manage", "skeleton_manage", "camera_manage"],
        "workflow": """
1. Use `anim_manage` com `op: "create_player"` para criar AnimationPlayer
2. Use `anim_manage` com `op: "create_clip"` para definir clipes de animação
3. Use `anim_manage` com `op: "create_tween"` para animações programáticas
4. Use `skeleton_manage` para animação de esqueleto 3D
5. Use `camera_manage` para animações de câmera
""",
        "example": 'anim_manage(op="create_clip", params={"name": "walk", "length": 1.0, "loop": True})',
    },
    "audio": {
        "title": "Áudio e Música",
        "description": "Gerenciar áudio: buses, efeitos, música, SFX espacial.",
        "tools": ["audio_manage", "music_manage", "vfx_manage"],
        "workflow": """
1. Use `audio_manage` com `op: "config_bus"` para configurar barramentos
2. Use `audio_manage` com `op: "add_effect"` para efeitos (reverb, EQ)
3. Use `audio_manage` com `op: "scan_sfx_events"` para mapear sons da cena
4. Use `music_manage` para gerar música procedural ou importar
""",
        "example": 'audio_manage(op="config_bus", params={"bus": "SFX", "volume_db": -6})',
    },
    "dialogo": {
        "title": "Diálogo e Narrativa",
        "description": "Criar sistema de diálogo, NPCs e inventário narrativo.",
        "tools": ["dialogue_manage", "inventory_manage", "gamestate_manage"],
        "workflow": """
1. Use `dialogue_manage` com `op: "create_system"` para criar o DialogueManager
2. Use `dialogue_manage` com `op: "add_node"` para adicionar nós de diálogo
3. Use `inventory_manage` para itens que afetam diálogos
4. Use `gamestate_manage` para flags que controlam ramificações
""",
        "example": 'dialogue_manage(op="create_system", params={"npc_name": "Mago", "tree": [...]})',
    },
    "importar-assets": {
        "title": "Importar Assets",
        "description": "Importar texturas, spritesheets, áudio, modelos 3D e shaders.",
        "tools": ["asset_manage", "audio_manage", "shader_manage"],
        "workflow": """
1. Use `asset_manage` com `op: "import_texture"` para texturas
2. Use `asset_manage` com `op: "import_spritesheet"` para spritesheets
3. Use `asset_manage` com `op: "import_audio"` para áudio
4. Use `shader_manage` para materiais visuais avançados
5. Use `asset_manage` com `op: "license_audit"` para verificar licenças
""",
        "example": 'asset_manage(op="import_texture", params={"path": "res://art/player.png"})',
    },
    "navegacao": {
        "title": "Navegação e Tilemap",
        "description": "Criar mapas com tilemap e navegação (pathfinding).",
        "tools": ["navigation_manage", "tilemap_manage", "d3_manage"],
        "workflow": """
1. Use `tilemap_manage` com `op: "create_tileset"` para criar tileset
2. Use `tilemap_manage` com `op: "create_layer"` para camadas do mapa
3. Use `tilemap_manage` com `op: "paint_cell"` para pintar o mapa
4. Use `navigation_manage` para configurar navmesh e pathfinding
""",
        "example": 'tilemap_manage(op="create_tileset", params={"name": "forest", "tile_size": 16})',
    },
    "balancear": {
        "title": "Balanceamento",
        "description": "Balancear o jogo: config, gamestate, playtest automatizado.",
        "tools": ["config_manage", "gamestate_manage", "playtest_manage"],
        "workflow": """
1. Use `config_manage` para ajustar parâmetros globais do jogo
2. Use `gamestate_manage` para verificar saves e progressão
3. Use `playtest_manage` com `op: "self_play"` para teste automatizado
4. Use `playtest_manage` com `op: "difficulty_curve"` para analisar curva
""",
        "example": 'playtest_manage(op="difficulty_curve", params={"level_range": [1, 10]})',
    },
    "network": {
        "title": "Rede e Multiplayer",
        "description": "Configurar multiplayer: autoridade, sincronização, bridge.",
        "tools": ["network_manage", "game_bridge_manage", "runtime_manage"],
        "workflow": """
1. Use `network_manage` para configurar multiplayer (peer, spawn, RPC)
2. Use `game_bridge_manage` para comunicação MCP ↔ jogo
3. Use `runtime_manage` para testar em múltiplas instâncias
4. Use `network_manage` com `op: "setup"` para configuração inicial
""",
        "example": 'network_manage(op="setup", params={"mode": "enet", "port": 9090})',
    },
    "pipelines": {
        "title": "Segurança e Workflow",
        "description": "Gerenciar segurança, auditoria e fluxo de trabalho.",
        "tools": ["safety_manage", "audit_manage", "workflow_manage"],
        "workflow": """
1. Use `safety_manage` para configurar políticas de segurança
2. Use `audit_manage` com `op: "log"` para histórico de ações
3. Use `workflow_manage` com `op: "snapshot"` para salvar estado
4. Use `workflow_manage` com `op: "handoff"` para preparar próxima sessão
""",
        "example": 'workflow_manage(op="snapshot", params={"description": "Antes de refatorar"})',
    },
}


def get_skill(name: str) -> dict | None:
    """Retorna uma skill pelo nome ou None."""
    return SKILLS.get(name)


def list_skills() -> list[dict]:
    """Lista todas as skills disponíveis."""
    return [
        {"name": name, "title": data["title"], "description": data["description"]}
        for name, data in sorted(SKILLS.items())
    ]


def skill_to_prompt(name: str) -> str | None:
    """Converte uma skill em um prompt utilizável pela IA."""
    skill = get_skill(name)
    if not skill:
        return None
    
    tools_str = ", ".join(f"`{t}`" for t in skill["tools"])
    return f"""# {skill["title"]}

{skill["description"]}

## Ferramentas relevantes
{tools_str}

## Fluxo de trabalho
{skill["workflow"].strip()}

## Exemplo
```
{skill["example"]}
```

**Instrução:** Use `catalog_search` para descobrir mais opções de cada ferramenta.
Use `describe_tool` para ver o schema completo antes de invocar.
"""
