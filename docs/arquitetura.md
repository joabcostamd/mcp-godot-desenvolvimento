# ARQUITETURA MCP — Godot Agent v3.5.0

> **Leia este documento para ENTENDER o MCP por dentro.** Não é um tutorial de uso
> (para isso veja `GUIA_CONEXAO.md`). É o mapa do código: como as peças se encaixam,
> por que cada decisão foi tomada, e como estender o sistema sem quebrá-lo.
>
> **Público:** IAs agênticas e desenvolvedores que precisam modificar ou entender o MCP.
> **Tempo de leitura:** ~10 minutos. **Tempo para adicionar uma tool nova:** ~5 minutos.

---

## 1. VISÃO GERAL — O que o MCP faz

O MCP (Model Context Protocol) é uma ponte entre **linguagem natural** e **Godot Engine**.
Ele expoe 240 ferramentas que uma IA pode chamar para criar jogos completos —
cenas, scripts, física, UI, áudio, partículas, exportação — sem que o usuário
precise abrir o editor Godot ou escrever uma linha de código.

### Fluxo de uma chamada

```
Usuário: "cria um personagem que pula"
    ↓
IA (Copilot/DeepSeek): traduz para chamadas MCP
    ↓
server.py: recebe JSON-RPC, roteia para o handler
    ↓
tools/*.py: executa a operação (ex: add_node, attach_script)
    ↓
Godot (via TCP :9080 / WebSocket :9082 / Runtime :8790): aplica a mudança
    ↓
Resposta: volta para a IA → IA explica ao usuário
```

### Princípio fundamental

**Declarativo, nunca imperativo.** O MCP gera o artefato INTEIRO (script/cena completo)
e aplica de uma vez. É proibido montar o jogo com dezenas de comandinhos passo a passo.
Isso reduz erros, acelera a construção e mantém a coerência.

---

## 2. ARQUITETURA DE 3 CAMADAS

```
┌─────────────────────────────────────────────────┐
│  CAMADA 1 — Server Core (server.py)             │
│  ─────────────────────────────────────────────  │
│  • Inicialização do servidor MCP (JSON-RPC)     │
│  • Roteamento de chamadas (call_tool)            │
│  • Rate limiting                                 │
│  • Cache de tool definitions e handlers          │
│  • Error codes + friendly error messages         │
│  • Perfis (--profile core/dev/full)              │
│  • 5 namespaces semanticos                        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  CAMADA 2 — Tool Definitions + Handlers          │
│  ─────────────────────────────────────────────  │
│  • 240 tools com schema JSON completo            │
│  • 32 rollups (<domain>_manage)                  │
│  • 3 perfis (core=31, dev=80, full=240)          │
│  • 5 namespaces (project, assets, runtime, analysis, orchestration) │
│  • Annotations: readOnlyHint, destructiveHint    │
│  • Títulos em português (PT-BR)                  │
│  • Tags por domínio (2D, 3D, física, UI...)     │
│  • Handlers que despacham para tools/*.py        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  CAMADA 3 — Implementações (tools/*.py)          │
│  ─────────────────────────────────────────────  │
│  • 115 modulos de operacoes reais                 │
│  • Cada tool tem UMA função exportada            │
│  • Operações no sistema de arquivos (.tscn, .gd) │
│  • Comunicação TCP/WebSocket com Godot           │
│  • Sistema de backup e undo automático           │
│  • Pontes: Editor TCP :9080, Game TCP :9081,     │
│    Addon WebSocket :9082, Runtime TCP :8790,     │
│    LSP TCP :6005                                 │
└─────────────────────────────────────────────────┘
```

---

## 3. CAMADA 1 — Server Core

### 3.1 Inicialização

```python
server = Server("godot-agent")  # ← nome do servidor MCP
```

O servidor usa o protocolo JSON-RPC 2.0 sobre stdio (Standard Input/Output).
Não é HTTP REST — é um canal de comunicação contínuo entre a IA e o MCP.

### 3.2 Roteamento de chamadas

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # 1. Rate limiting (evita sobrecarga)
    # 2. Busca handler no cache _HANDLERS_CACHE
    # 3. Executa handler com os argumentos
    # 4. Se der erro, adiciona error_code + friendly message
    # 5. Retorna JSON com status + dados
```

### 3.3 Sistema de cache

Dois caches globais evitam recriar estruturas pesadas a cada chamada:

| Cache | O que armazena | Quando invalida |
|---|---|---|
| `_TOOL_DEFS_CACHE` | Lista das 191 definições de tools | Nunca (tools são estáticas) |
| `_HANDLERS_CACHE` | Dict `{nome_da_tool: função_handler}` | Nunca |

### 3.4 Rate Limiting

O módulo `tools/rate_limiter.py` controla quantas chamadas por segundo são permitidas.
Se excedido, retorna erro com `retry_after` (tempo de espera em segundos).

### 3.5 Error Codes

| Código | Significado |
|---|---|
| 1001 | Entrada inválida (caminho não encontrado, valor inválido) |
| 2001 | Problema com projeto/arquivo (project.godot, cena, script) |
| 3001 | Problema com Godot (compilação, timeout, template) |
| 4001 | Problema de conexão (bridge, TCP, socket) |
| 5000 | Erro interno não categorizado |

Cada erro também recebe uma mensagem amigável em português via `tools/friendly_errors.py`.

### 3.5.1 Perfis de Tools (--profile)

Para controlar quantas tools são expostas (economia de tokens):

```bash
python server.py --profile core   # 16 tools essenciais (~2K tokens)
python server.py --profile dev    # 31 tools para desenvolvimento (~5K tokens)
python server.py --profile full   # 191 tools completas (~19K tokens, default)
```

Também configurável via env var: `MCP_TOOL_PROFILE=dev`.

### 3.5.2 Toolsets (--toolsets)

Filtra tools por domínio específico:

```bash
python server.py --toolsets "core,scene_ops,script_ops"
```

10 toolsets disponíveis: `core`, `scene_ops`, `script_ops`, `test_ops`, `runtime_ops`, `git_ops`, `refs_ops`, `asset_ops`, `design_ops`, `ui_ops`.

### 3.6 Configuração (config.json)

```json
{
  "godot_path": "C:\\Godot\\Godot_v4.7-stable_win64.exe",
  "godot_console_path": "C:\\Godot\\Godot_v4.7-stable_win64_console.exe",
  "python_path": "C:\\Users\\...\\Python\\Python314\\python.exe",
  "projects_root": "C:\\...\\NUCLEO\\projetos",
  "default_project": "C:\\...\\NUCLEO\\projetos\\star-colony",
  "addon_port": 9080,
  "game_port": 9081,
  "timeouts": { "fast": 15, "compile": 60, "export": 300 },
  "vibe_coding": { "enabled": true },
  "security": { "allow_remote": false }
}
```

| Campo | Obrigatório | O que faz |
|---|---|---|
| `godot_path` | ✅ | Caminho do executável do Godot (editor gráfico) |
| `godot_console_path` | ✅ | Caminho do executável console (headless, para compilação) |
| `python_path` | ✅ | Python usado para iniciar o Godot (precisa ser 3.12+) |
| `projects_root` | ❌ | Pasta raiz onde projetos Godot são criados (default: `projetos/`) |
| `default_project` | ❌ | Projeto aberto por padrão quando nenhum é especificado |
| `addon_port` | ❌ | Porta TCP do editor bridge — default 9080 |
| `game_port` | ❌ | Porta TCP do game bridge (runtime) — default 9081 |
| `timeouts.fast` | ❌ | Timeout para operações rápidas (segundos) — default 15 |
| `timeouts.compile` | ❌ | Timeout para compilação Godot — default 60 |
| `timeouts.export` | ❌ | Timeout para exportação/build — default 300 |
| `vibe_coding.enabled` | ❌ | Ativa modo vibe coding (geração automática) — default true |
| `security.allow_remote` | ❌ | Permite conexões remotas — default false |

> **Ajuste obrigatório por máquina:** apenas `godot_path`, `godot_console_path` e
> `python_path`. O resto tem defaults que funcionam.
>
> **Override local:** Crie `config.local.json` (gitignorado) com os campos que
> quiser sobrescrever. Ex: `{"default_project": "C:\\...\\meu-outro-jogo"}`.
> Também pode usar env vars: `GODOT_MCP_*` (ex: `GODOT_MCP_DEFAULT_PROJECT`).

---

## 4. CAMADA 2 — Tool Definitions

### 4.1 Estrutura de uma tool

Cada tool é um objeto `Tool` com:

```python
Tool(
    name="create_scene",                    # nome único (snake_case)
    description="Cria uma nova cena...",    # descrição COMPLETA (quando usar, quando NÃO usar, pré-condições, exemplo, erros comuns)
    inputSchema={...},                      # JSON Schema dos argumentos
    # Annotations (adicionadas no pós-processamento):
    #   .title = "Criar Cena (.tscn)"       # título PT-BR
    #   .readOnlyHint = True/False          # só leitura?
    #   .destructiveHint = True/False       # operação destrutiva?
    #   .idempotentHint = True/False        # pode repetir sem efeito colateral?
    #   .annotations = {"tags": [...]}      # tags por domínio
)
```

### 4.2 Padrão de descrição (obrigatório)

Toda descrição de tool segue este template:

1. **O que faz** — frase curta
2. **Quando usar** — cenário típico
3. **Quando NÃO usar** — ferramenta alternativa
4. **Pré-condições** — o que precisa existir antes
5. **Exemplo de input** — JSON de exemplo
6. **Erro mais comum** — e como resolver

Isso permite que a IA **decida sozinha** qual tool usar sem perguntar ao usuário.

### 4.3 Categorias de tools

| Categoria | Tools | Arquivo |
|---|---|---|
| **Projeto** | create_project, set_active_project, inspect_project | project_ops.py |
| **Arquivos** | read_file, write_file, delete_file, move_file | file_ops.py |
| **Cenas** | create_scene, add_node, delete_node, set_node_property, load_scene_tree, reparent_node, instance_scene_as_child, connect_signal, list_signals | scene_ops.py |
| **Scripts** | generate_gdscript, attach_script, detach_script, validate_gdscript_syntax, add_script_variable, add_script_signal | script_ops.py |
| **Física** | add_collision_shape, set_collision_layer_mask, set_physics_material, create_joint_2d, add_raycast_2d, add_shapecast_2d | physics_ops.py |
| **Assets** | import_texture, import_sprite_sheet, import_audio, generate_placeholder_sprite, generate_background_gradient, generate_tileset_from_colors, generate_audio_sfx, suggest_color_palette | asset_ops.py |
| **Runtime** | run_game, stop_game, smart_restart, compile_test, execute_gdscript_runtime, inject_input_event, watch_signal | runtime_ops.py |
| **Editor** | launch_editor, close_editor, take_screenshot, read_console_output | runtime_ops.py |
| **Visão** | capture_game_screenshot, compare_screenshots, detect_empty_screen, detect_offscreen_elements | runtime_ops.py |
| **Tilemap** | create_tileset, create_tilemap_layer, paint_tilemap_cell | scene_ops.py |
| **Animação** | create_animation_player, create_animation, create_animation_tree, create_tween_animation, chain_tweens | scene_ops.py |
| **UI** | create_ui_scene, add_control_node, create_main_menu, create_hud_template, create_pause_menu, create_health_bar, create_loading_screen | devsolo_ops.py |
| **Export** | list_export_presets, validate_export_templates_installed, build_export, configure_export_preset | export_ops.py |
| **Segurança** | list_backups, restore_backup, git_commit_checkpoint, undo_last_action, get_undo_history | safety.py |
| **Input** | configure_input_action, configure_autoload | project_ops.py |
| **ClassDB** | query_classdb, list_valid_node_types | classdb.py |
| **IA Agêntica** | analyze_game_structure, suggest_next_steps, find_missing_references, validate_game_design, estimate_game_scope, search_codebase, get_project_history | analyze_ops.py |
| **DevSolo** | setup_camera_2d, setup_camera_follow, setup_camera_shake, create_save_system, define_save_data, create_state_machine, add_state_transition, create_navigation_region_2d, create_navigation_agent_2d, bake_navigation_polygon, setup_world_environment, setup_screen_flash | devsolo_ops.py |
| **Batch** | add_nodes_batch, set_properties_batch | (handlers inline) |
| **Parallax** | create_parallax_background, add_parallax_layer | (handlers inline) |
| **Partículas** | create_particles_2d, configure_particles_2d, create_particles_3d | (handlers inline) |
| **Shaders** | generate_shader_2d, apply_shader_to_node, create_shader_material | (handlers inline) |
| **Patrulha** | create_path_2d, create_patrol_route | (handlers inline) |
| **Diálogo** | create_dialogue_system, add_dialogue_node, create_dialogue_ui | (handlers inline) |
| **Inventário** | create_inventory_system, define_inventory_item, create_inventory_ui | (handlers inline) |
| **Combate** | create_bullet_template, create_gun_system | (handlers inline) |
| **Procedural** | generate_tilemap_from_noise, generate_dungeon_rooms | (handlers inline) |
| **3D** | import_3d_model, create_light_3d, create_csg_shape, configure_standard_material_3d | (handlers inline) |
| **Áudio** | configure_audio_bus, add_audio_effect | (handlers inline) |
| **Debug** | enable_debug_collisions, enable_debug_navigation, get_performance_stats | (handlers inline) |
| **i18n** | setup_localization, add_translation_string | (handlers inline) |
| **Diagnóstico** | ping, validate_godot_version, health_check, self_test | server.py |

---

## 5. CAMADA 3 — Implementações

### 5.1 Estrutura de tools/*.py

Cada arquivo em `tools/` exporta funções que são importadas por `server.py`:

```python
# Exemplo: tools/scene_ops.py
def create_scene(name: str, root_type: str, path: str) -> dict:
    """Cria arquivo .tscn com nó raiz."""
    # 1. Valida entradas
    # 2. Gera conteúdo .tscn
    # 3. Write file com backup automático
    # 4. Retorna {"status": "success", "scene_path": "..."}
```

**Toda tool retorna um dict com pelo menos `{"status": "success"}` ou `{"status": "error", "message": "..."}`.**

### 5.2 Operações no sistema de arquivos

O MCP manipula diretamente arquivos `.tscn` (cenas Godot em formato texto) e `.gd`
(GDScript). Não depende do editor Godot estar aberto para a maioria das operações —
apenas para runtime (run_game, take_screenshot) e editor (launch_editor).

### 5.3 Comunicação com Godot (5 pontes)

```
Servidor Python                          Godot
     │                                     │
     │── TCP :9080 (editor) ──────────────→│ Editor Bridge
     │   comandos de edição                │ (recebe e aplica no editor)
     │                                     │
     │── WebSocket :9082 (addon) ─────────→│ mcp_addon (Dock UI)
     │   comandos JSON-RPC 2.0             │ (3 tabs: Status/Log/Tools)
     │                                     │
     │←── TCP :9081 (runtime) ────────────│ Game Bridge
     │   estado do jogo em execução        │ (envia posição, HP, colisões)
     │                                     │
     │←── TCP :8790 (runtime bridge) ─────│ mcp_runtime_bridge
     │   screenshot, FPS, input injection  │ (autoload, só debug builds)
     │                                     │
     │── TCP :6005 (LSP) ─────────────────│ Godot LSP built-in
     │   referências, definição, hover     │ (análise semântica)
```

### 5.4 Sistema de backup

Toda operação destrutiva (write_file, delete_file, add_node, etc.) cria um backup
automático em `.mcp_backups/` antes de modificar. O backup inclui timestamp e
identificação da operação.

O sistema de undo (`undo_last_action`) restaura o estado anterior usando esses backups.
Histórico das últimas 20 ações é mantido.

### 5.5 Addons Godot (o lado Godot da equação)

O MCP tem 2 addons que rodam DENTRO do Godot, escritos em GDScript:

#### mcp_addon (`addons/mcp_addon/`)

```
EditorPlugin (@tool)
├── WebSocket Server em localhost:9082
├── Protocolo: JSON-RPC 2.0 sobre WebSocket
├── Recebe comandos do server.py e aplica no editor
├── Dock "MCP Addon" no painel direito do Godot (3 tabs)
│   ├── Tab Status: indicador de conexão + porta + clientes
│   ├── Tab Log: últimas 200 operações (coloridas)
│   └── Tab Tools: lista de 9 operações disponíveis
└── Undo/Redo via EditorUndoRedoManager nativo
```

**Plugin CFG:** nome "MCP Addon", versão 3.0.1, registrado como `EditorPlugin`.

#### mcp_runtime_bridge (`addons/mcp_runtime_bridge/`)

```
Autoload (singleton global)
├── TCP Server em localhost:8790
├── Protocolo: JSON line-delimited
├── SÓ ativo em debug build (OS.is_debug_build())
├── Comandos nativos: screenshot (PNG base64), runtime_info (FPS/memória),
│   input_event (mouse/key injection), wait_frames
└── Comandos custom registráveis (3 built-in: save_current_scene,
    add_test_marker, replace_with_runtime_scene)
```

**Segurança:** O runtime bridge NUNCA roda em builds exportadas (standalone).
Só funciona no editor ou via `run_game --path`.

#### Fluxo completo de uma chamada

```
server.py              mcp_addon (Godot:9082)    runtime_bridge (Godot:8790)
    │                        │                          │
    │── WS connect :9082 ──→│                          │
    │   {"method":"add_node",│                          │
    │    "params":{...}}     │                          │
    │                        │── add_child + set_owner │
    │←── {"status":"ok"} ──│                          │
    │                        │                          │
    │── run_game ──────────────────────────────────────→│ (Godot inicia)
    │                        │                          │
    │── TCP connect :8790 ────────────────────────────→│
    │   {"cmd":"runtime_info"}│                          │
    │                        │                          │── coleta FPS/mem
    │←── {"fps":60,...} ──────────────────────────────│
```

> **Para debugar conexão:** verifique as portas com `netstat -ano | findstr "9080 9081 9082 8790 6005"`.
> Cada porta tem um propósito: 9080=editor TCP, 9081=game TCP, 9082=addon WebSocket,
> 8790=runtime bridge, 6005=LSP.

### 5.6 Sistema de Templates (Jinja2)

O MCP gera código GDScript a partir de templates Jinja2 em `templates/`.

**Templates disponíveis:**

| Template | O que gera | Variáveis |
|---|---|---|
| `player_2d_controller.gd` | Personagem 2D com setas + pulo | `speed`, `jump_velocity`, `gravity` |
| `enemy_chase_basic.gd` | Inimigo que persegue o player | `speed`, `target_path` |
| `bouncing_ball.gd` | Bola que quica (Pong/Breakout) | `speed`, `color` |
| `paddle.gd` | Raquete controlável (Pong) | `speed`, `up_key`, `down_key` |
| `game_manager_singleton.gd` | Singleton de estado global | `game_name` |

**Como funciona:**

```python
# server.py chama generate_gdscript(template, variables, save_path)
# → tools/script_ops.py carrega o template Jinja2
# → renderiza com as variáveis
# → salva o .gd no projeto
# → valida sintaxe com validate_gdscript_syntax
```

**Exemplo de template Jinja2 (`player_2d_controller.gd`):**
```gdscript
extends CharacterBody2D

@export var speed: float = {{ speed | default(300) }}
@export var jump_velocity: float = {{ jump_velocity | default(-400) }}
var gravity: float = {{ gravity | default(980) }}

func _physics_process(delta):
    velocity.x = Input.get_axis("move_left", "move_right") * speed
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
    velocity.y += gravity * delta
    move_and_slide()
```

> **Para criar um template novo:** adicione um arquivo `.gd` em `templates/` usando
> sintaxe Jinja2 (`{{ variavel }}`). Registre no `generate_gdscript` handler.

---

## 6. COMO ADICIONAR UMA TOOL NOVA (receita)

### Passo 1: Criar a função em tools/

```python
# tools/seu_arquivo.py
def minha_tool_nova(param1: str, param2: int = 42) -> dict:
    """Faz algo útil no Godot."""
    try:
        # 1. Validar entradas
        if not param1:
            return {"status": "error", "message": "param1 é obrigatório"}
        # 2. Executar operação
        resultado = fazer_algo(param1, param2)
        # 3. Retornar sucesso
        return {"status": "success", "resultado": resultado}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Passo 2: Registrar a tool em server.py

Adicione o import no topo de `server.py`:
```python
from tools.seu_arquivo import minha_tool_nova
```

Adicione a definição em `_tool_defs()`:
```python
Tool(
    name="minha_tool_nova",
    description=(
        "Descrição completa: o que faz, quando usar, quando NÃO usar, "
        "pré-condições, exemplo de input, erro mais comum."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Descrição do parâmetro."},
            "param2": {"type": "integer", "description": "Opcional, default 42."},
        },
        "required": ["param1"],
    },
),
```

Adicione o handler em `_build_handlers()`:
```python
"minha_tool_nova": _handle_minha_tool_nova,
```

Crie o handler:
```python
def _handle_minha_tool_nova(args: dict) -> dict:
    return minha_tool_nova(
        param1=args["param1"],
        param2=args.get("param2", 42),
    )
```

### Passo 3: Classificar a tool

Adicione aos conjuntos apropriados (se aplicável):
```python
_READONLY.add("minha_tool_nova")      # se for só leitura
_DESTRUCTIVE.add("minha_tool_nova")   # se for destrutiva
_IDEMPOTENT.add("minha_tool_nova")    # se for idempotente
```

Adicione título PT-BR:
```python
_TITLES["minha_tool_nova"] = "Minha Tool Nova — Faz Algo Útil"
```

Adicione tags:
```python
_TAGS["minha_tool_nova"] = ["categoria", "subcategoria"]
```

---

## 7. DECISÕES DE DESIGN (o porquê das coisas)

### 7.0 Por que scoring manual em vez de BM25 no tool_catalog?

BM25 (Okapi) foi testado e removido. Problemas encontrados:
- Tokenização por underscore não quebrava nomes compostos (`create_scene` = 1 token)
- Peso do nome (3x repetição) beneficiava ferramentas com termos coincidentes
- "no" como substring matchava em "animation", "node", "another" — ubíquo
- Queries em português tinham ranking imprevisível

**Solução:** scoring direto por camada (nome +3, ops +2, descrição +1, rollup bônus +1)
com token matching exato. Mais previsível, mais fácil de depurar, sem dependência externa.

### 7.0b Por que PHASE_TOOLSETS é dinâmico e não estático?

As fases do projeto mudam em tempo real via `advance_phase()` (Feature 1). Um filtro
estático (`--phase IDEIA`) exigiria reiniciar o servidor MCP a cada avanço — quebrando
o fluxo de desenvolvimento. O filtro dinâmico lê `.mcp_phase_state.json` do disco a
cada `_tool_defs()`, e o cache é invalidado via callback quando a fase avança.

### 7.0c Por que _build_handlers() NÃO é filtrado por fase?

PHASE_TOOLSETS é um mecanismo de **curadoria/visibilidade**, não de segurança.
Se a IA insistir em chamar uma tool "escondida" (ex: `deploy_itch` na fase IDEIA),
o handler executa normalmente. O bloqueio de progressão entre fases é responsabilidade
exclusiva da Feature 1 (`advance_phase`), que verifica critérios objetivos.

### 7.1 Por que 191 tools e não 50?

Cada tool faz UMA coisa bem definida. Isso permite que a IA componha operações complexas
a partir de tools simples. É o princípio UNIX: "faça uma coisa e faça bem".

Para controlar o volume de tools expostas, use perfis:
- `--profile core`: 16 tools essenciais (~2K tokens)
- `--profile dev`: 31 tools para desenvolvimento (~5K tokens)
- `--profile full`: 191 tools completas (default)

### 7.2 Por que JSON-RPC sobre stdio e não HTTP REST?

- **stdio** não precisa de porta, firewall, ou configuração de rede
- **JSON-RPC** é o protocolo nativo do MCP (Model Context Protocol)
- Funciona em qualquer ambiente (local, Codespace, servidor)

### 7.3 Por que manipular .tscn como texto e não via API do Godot?

- Não depende do editor Godot estar aberto
- Operações são mais rápidas (arquivo vs. round-trip TCP)
- Permite batch operations (add_nodes_batch)
- Backups são arquivos simples

### 7.4 Por que backups automáticos em vez de depender de git?

- Git requer commit consciente; backups são transparentes
- Undo é instantâneo (restaura arquivo do backup)
- Funciona mesmo sem git inicializado

### 7.5 Por que o sistema é declarativo (artefato inteiro de uma vez)?

- Reduz erros de consistência (meia cena aplicada)
- Mais rápido (1 chamada vs. 20)
- A IA pode validar o artefato completo antes de aplicar

---

## 8. EXTENSÃO E MANUTENÇÃO

### 8.1 Quando adicionar uma tool nova

- Quando uma operação do Godot não tem tool correspondente
- Quando uma combinação frequente de tools justifica uma tool composta
- Quando um novo tipo de jogo exige ferramentas específicas (ex: ferramentas de RPG)

### 8.2 Quando NÃO adicionar

- Se já existe tool que faz a mesma coisa (use a existente)
- Se a operação é muito específica de um jogo (pertence ao script do jogo, não ao MCP)
- Se pode ser composta com tools existentes

### 8.3 Testando uma tool nova

```powershell
cd sistema\mcp-godot\servidor
.venv\Scripts\python -c "from tools.seu_arquivo import minha_tool_nova; print(minha_tool_nova('teste'))"
```

---

## 9. DEPENDÊNCIAS

| Pacote | Versão | Por que |
|---|---|---|
| `mcp` | 1.28.1 | Servidor MCP (JSON-RPC sobre stdio) |
| `godot_parser` | 0.1.7 | Parse de arquivos .tscn e .gd |
| `jinja2` | 3.1.6 | Templates GDScript |
| `Pillow` | 12.3.0 | Geração de assets procedurais (sprites, backgrounds) |
| `httpx` | 0.28.1 | Comunicação HTTP (fallback) |
| `uvicorn` | 0.51.0 | Servidor ASGI (se modo HTTP for usado) |
| `pydantic` | 2.13.4 | Validação de dados |
| `pyinstaller` | 6.21.0 | Empacotamento (distribuição) |

---

## 10. ARQUIVOS DO PROJETO

```
mcp-godot-desenvolvimento/
├── server.py              ← CORAÇÃO: ~7400 linhas, 191 tools, roteamento
├── tools/                 ← Implementações (64 módulos)
│   ├── scene_ops.py       ← Cenas, nós, tilemap, animação, UI
│   ├── script_ops.py      ← GDScript (gerar, anexar, validar)
│   ├── project_ops.py     ← Projeto (criar, configs, input, autoload)
│   ├── file_ops.py        ← Arquivos (ler, escrever, deletar, mover)
│   ├── runtime_ops.py     ← Runtime + Editor + Visão
│   ├── physics_ops.py     ← Colisões, física, raycast
│   ├── asset_ops.py       ← Import/export de assets
│   ├── asset_manifest.py  ← Manifest de assets (5 fontes)
│   ├── export_ops.py      ← Exportação (build)
│   ├── classdb.py         ← Consulta à ClassDB do Godot
│   ├── safety.py          ← Backups, undo, git checkpoint
│   ├── analyze_ops.py     ← IA agêntica (análise, sugestões)
│   ├── devsolo_ops.py     ← DevSolo (câmera, menu, HUD, save, FSM)
│   ├── refs_ops.py        ← Validação de referências + find_usages
│   ├── test_ops.py        ← Testes roteirizados (smoke, regression)
│   ├── rollups.py         ← 27 rollups (<domain>_manage)
│   ├── orchestrator.py    ← Saga + Circuit Breaker + Decision Engine
│   ├── editor_bridge.py   ← Ponte TCP com editor Godot
│   ├── game_bridge.py     ← Ponte TCP com jogo em execução
│   ├── addon_bridge.py    ← Ponte WebSocket com addon (:9082)
│   ├── bridge.py          ← Protocolo de comunicação TCP
│   ├── rate_limiter.py    ← Controle de taxa de chamadas
│   ├── friendly_errors.py ← Tradução de erros para PT-BR
│   ├── file_watcher.py    ← Monitoramento de arquivos
│   ├── gdscript_sandbox.py← Sandbox para execução segura
│   ├── live_stream.py     ← Streaming ao vivo
│   └── placeholder_ops.py ← Assets procedurais
├── templates/             ← Templates GDScript (Jinja2)
├── resources/             ← Game patterns (18 gêneros) + prompts
├── classdb_cache/         ← Cache da API do Godot 4.7 (1074 classes)
├── addons/                ← Plugins Godot (mcp_addon + mcp_runtime_bridge)
├── config.json            ← Caminhos do Godot + projeto padrão
├── config.json.example    ← Template para novas máquinas
├── config.local.json      ← Overrides locais (gitignorado)
├── requirements.txt       ← Dependências Python
├── pyproject.toml         ← Metadata do projeto
├── GUIA_CONEXAO.md        ← Como usar — passo a passo do zero
├── GUIA_INSTALACAO.md     ← Setup completo para IA agêntica
├── LEARNINGS.md           ← Anti-padrões e regras de prevenção
└── ARQUITETURA_MCP.md     ← Este documento
```

---

**Última atualização:** 2026-07-12 | **MCP versão:** 3.2 | **Tools:** 189 | **Módulos:** 64 | **Código:** ~24.000 linhas
