"""onboarding_ops.py — Tutorial e primeira experiência do jogador (Fatia 5.7).

Ferramentas para criar onboarding interativo:
  - Sequência de passos de tutorial
  - Tour guiado pela UI
  - Checagem de primeira experiência (first-time user experience)
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def onboarding_create_tutorial_step(args: dict | None = None) -> dict:
    """Cria um passo de tutorial interativo (highlight + texto).

    Gera código GDScript para um sistema de tutorial passo a passo:
    destaca um nó da UI, mostra texto explicativo, aguarda ação
    do jogador, avança para o próximo passo.

    Args:
        steps: Lista de passos [{target_node, instruction, required_action, highlight}].
        tutorial_name: Nome do tutorial (ex: "primeira_partida").
        apply_to_project: Se True, salva script no projeto.

    Returns:
        dict com script_code, steps, e instruções de integração.
    """
    args = args or {}
    steps = args.get("steps", [])
    tutorial_name = args.get("tutorial_name", "tutorial")

    if not steps:
        steps = [
            {"target_node": "HUD/Joystick", "instruction": "Use o joystick para mover", "required_action": "move", "highlight": True},
            {"target_node": "HUD/AttackButton", "instruction": "Pressione para atacar", "required_action": "click", "highlight": True},
            {"target_node": "HUD/HealthBar", "instruction": "Esta e sua barra de vida", "required_action": "wait", "highlight": False},
        ]

    script_code = f'''extends CanvasLayer
## Tutorial: {tutorial_name} — gerado por MCP Godot Agent

class_name Tutorial{tutorial_name.replace(" ", "").capitalize()}

signal tutorial_completed
signal tutorial_step_advanced(step: int, total: int)

var _steps: Array[Dictionary] = []
var _current_step: int = 0
var _highlight: ColorRect
var _label: RichTextLabel
var _is_active: bool = false

func _ready():
    _setup_ui()
    _load_steps()

func _setup_ui():
    # Highlight (borda/overlay)
    _highlight = ColorRect.new()
    _highlight.color = Color(1, 1, 0, 0.3)
    _highlight.visible = false
    add_child(_highlight)

    # Instruction label
    _label = RichTextLabel.new()
    _label.bbcode_enabled = true
    _label.fit_content = true
    _label.add_theme_font_size_override("normal_font_size", 18)
    _label.position = Vector2(20, 20)
    add_child(_label)

func _load_steps():
    _steps = {repr(steps)}
    if _steps.size() > 0:
        start()

func start():
    _is_active = true
    _current_step = 0
    _show_step()

func _show_step():
    if _current_step >= _steps.size():
        _complete()
        return
    var step = _steps[_current_step]
    _label.text = "[center][b]" + step.get("instruction", "") + "[/b][/center]"
    if step.get("highlight", true):
        _highlight_control(step.get("target_node", ""))

func _highlight_control(node_path: String):
    var target = get_node_or_null(node_path)
    if target and target is Control:
        _highlight.position = target.global_position
        _highlight.size = target.size
        _highlight.visible = true
    else:
        _highlight.visible = false

func advance():
    if not _is_active: return
    _current_step += 1
    tutorial_step_advanced.emit(_current_step, _steps.size())
    _show_step()

func skip():
    _complete()

func _complete():
    _is_active = false
    _highlight.visible = false
    _label.visible = false
    tutorial_completed.emit()
'''

    return {
        "status": "success",
        "tutorial_name": tutorial_name,
        "total_steps": len(steps),
        "steps": steps,
        "script_code": script_code,
        "integration_guide": [
            "1. Adicione Tutorial como autoload ou nó filho da cena principal",
            "2. Conecte sinais de input a advance() no passo correto",
            "3. Chame skip() se o jogador pular o tutorial",
            "4. Salve progresso do tutorial no user:// para não repetir",
        ],
        "message": f"Tutorial '{tutorial_name}' com {len(steps)} passos gerado.",
    }


def onboarding_create_guided_tour(args: dict | None = None) -> dict:
    """Cria um tour guiado pela interface do jogo.

    Similar ao tutorial, mas focado em apresentar a UI
    (menus, HUD, inventário) em vez de mecânicas.

    Args:
        ui_elements: Lista de elementos [{name, node_path, description}].
        tour_name: Nome do tour.

    Returns:
        dict com configuração do tour guiado.
    """
    args = args or {}
    ui_elements = args.get("ui_elements", [])
    tour_name = args.get("tour_name", "ui_tour")

    if not ui_elements:
        ui_elements = [
            {"name": "Barra de Vida", "node_path": "HUD/HealthBar", "description": "Mostra sua vida atual. Quando chegar a zero, voce morre."},
            {"name": "Inventário", "node_path": "HUD/Inventory", "description": "Aqui ficam seus itens coletados. Pressione I para abrir/fechar."},
            {"name": "Minimapa", "node_path": "HUD/Minimap", "description": "Mostra sua posição e pontos de interesse próximos."},
        ]

    return {
        "status": "success",
        "tour_name": tour_name,
        "total_elements": len(ui_elements),
        "elements": ui_elements,
        "script_code": onboarding_create_tutorial_step({
            "steps": [{"target_node": e["node_path"], "instruction": e["description"], "required_action": "wait", "highlight": True} for e in ui_elements],
            "tutorial_name": tour_name,
        }).get("script_code", ""),
        "message": f"Tour guiado '{tour_name}' com {len(ui_elements)} elementos.",
    }


def onboarding_check_first_experience(args: dict | None = None) -> dict:
    """Verifica a primeira experiência do jogador (FTUE).

    Checklist de boas práticas para onboarding:
      - O jogo é jogável em < 30 segundos?
      - O primeiro desafio é fácil demais?
      - As instruções são visuais ou só texto?
      - O jogador sabe o que fazer se morrer?

    Args:
        game_type: Tipo de jogo para recomendações específicas.

    Returns:
        dict com checklist e recomendações.
    """
    args = args or {}
    game_type = args.get("game_type", "action")

    checklist = [
        {"check": "jogavel_30s", "question": "O jogador consegue jogar em < 30 segundos do launch?", "severity": "critical", "suggestion": "Remova logos longas, va direto ao menu principal."},
        {"check": "primeiro_desafio", "question": "O primeiro desafio e facil e gratificante?", "severity": "high", "suggestion": "Primeiro inimigo deve ser derrotado em 1-2 hits."},
        {"check": "instrucoes_visuais", "question": "As instrucoes usam elementos visuais alem de texto?", "severity": "medium", "suggestion": "Use setas animadas, highlights, e icones."},
        {"check": "feedback_imediato", "question": "Toda acao do jogador tem feedback imediato (som, particula, animacao)?", "severity": "high", "suggestion": "Adicione SFX e VFX para cada interacao."},
        {"check": "morte_clara", "question": "Ao morrer, o jogador entende por que e o que fazer?", "severity": "high", "suggestion": "Mostre tela de morte com dica e botao de restart claro."},
        {"check": "objetivo_claro", "question": "O objetivo esta claro nos primeiros 10 segundos?", "severity": "critical", "suggestion": "Use seta/indicador visual para o objetivo principal."},
        {"check": "skip_tutorial", "question": "O tutorial pode ser pulado?", "severity": "medium", "suggestion": "Adicione botao 'Pular tutorial' visivel."},
        {"check": "menus_intuitivos", "question": "Os menus sao navegaveis em < 3 cliques?", "severity": "medium", "suggestion": "Simplifique hierarquia de menus."},
    ]

    critical = [c for c in checklist if c["severity"] == "critical"]
    high = [c for c in checklist if c["severity"] == "high"]

    return {
        "status": "success",
        "game_type": game_type,
        "total_checks": len(checklist),
        "critical_checks": len(critical),
        "high_checks": len(high),
        "checklist": checklist,
        "message": f"FTUE checklist: {len(checklist)} itens ({len(critical)} criticos, {len(high)} alta prioridade).",
    }
