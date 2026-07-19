"""cutscene_ops.py — Sequenciador de Cutscene/Cinemática (Fatia 5.3).

Ferramentas para criar cutscenes com controle de câmera:
  - Linha do tempo de eventos (camera, diálogo, animação, áudio)
  - Shots de câmera com transições
  - Integração com AnimationPlayer do Godot
"""

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

_CAMERA_TRANSITIONS = ["cut", "fade", "dissolve", "zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"]


def cutscene_create_timeline(args: dict | None = None) -> dict:
    """Cria uma linha do tempo de cutscene com eventos sequenciais.

    Gera um script GDScript que orquestra eventos de cutscene:
      - Shots de câmera (posição, zoom, transição)
      - Eventos de diálogo
      - Eventos de áudio/SFX
      - Eventos de animação
      - Esperas (wait)

    Args:
        cutscene_name: Nome da cutscene.
        events: Lista de eventos [{type, time_sec, params}].
        apply_to_project: Se True, salva script no projeto.

    Returns:
        dict com script_code, events, e total_duration.
    """
    args = args or {}
    cutscene_name = args.get("cutscene_name", "cutscene_intro")
    events = args.get("events", [])
    apply_to_project = args.get("apply_to_project", False)

    if not events:
        events = [
            {"type": "camera_shot", "time_sec": 0.0, "params": {"target": "Player", "transition": "fade", "duration": 1.0}},
            {"type": "dialogue", "time_sec": 1.5, "params": {"speaker": "Narrador", "text": "Em um mundo distante..."}},
            {"type": "wait", "time_sec": 4.0, "params": {"duration": 2.0}},
            {"type": "camera_shot", "time_sec": 4.0, "params": {"target": "Castle", "transition": "pan_right", "duration": 2.0}},
            {"type": "audio", "time_sec": 0.0, "params": {"action": "play_music", "track": "intro_theme"}},
        ]

    total_duration = max(e.get("time_sec", 0) + e.get("params", {}).get("duration", 2.0) for e in events) if events else 10.0

    script_code = f'''extends Node
## Cutscene: {cutscene_name} — gerado por MCP Godot Agent

class_name Cutscene{cutscene_name.replace(" ", "").capitalize()}

signal cutscene_finished
signal cutscene_event(event_type: String, event_params: Dictionary)

var _events: Array[Dictionary] = []
var _camera: Camera2D
var _timer: float = 0.0
var _current_event: int = 0
var _playing: bool = false

func _ready():
    _camera = get_viewport().get_camera_2d()
    _load_events()

func _load_events():
    _events = {repr(events)}

func play():
    _playing = true
    _current_event = 0
    _timer = 0.0

func _process(delta: float):
    if not _playing: return
    _timer += delta
    while _current_event < _events.size():
        var ev = _events[_current_event]
        if _timer >= ev.get("time_sec", 0.0):
            _execute_event(ev)
            _current_event += 1
        else:
            break
    if _current_event >= _events.size():
        _finish()

func _execute_event(ev: Dictionary):
    var ev_type: String = ev.get("type", "")
    var params: Dictionary = ev.get("params", {{}})
    cutscene_event.emit(ev_type, params)
    match ev_type:
        "camera_shot":
            var target = params.get("target", "")
            var transition = params.get("transition", "cut")
            var duration = params.get("duration", 1.0)
            _do_camera_shot(target, transition, duration)
        "dialogue":
            var speaker = params.get("speaker", "")
            var text = params.get("text", "")
            _show_dialogue(speaker, text)
        "audio":
            var action = params.get("action", "")
            var track = params.get("track", "")
            _do_audio(action, track)
        "wait":
            pass  # Natural — o timer ja cuida

func _do_camera_shot(target: String, transition: String, duration: float):
    if not _camera: return
    var target_node = get_node_or_null(target) if target != "" else null
    if not target_node:
        return
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_SINE)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.tween_property(_camera, "global_position", target_node.global_position, duration)

func _show_dialogue(speaker: String, text: String):
    pass  # Conectar ao sistema de diálogo do jogo

func _do_audio(action: String, track: String):
    pass  # Conectar ao sistema de áudio do jogo

func skip():
    _finish()

func _finish():
    _playing = false
    cutscene_finished.emit()
'''

    return {
        "status": "success",
        "cutscene_name": cutscene_name,
        "total_events": len(events),
        "total_duration_sec": round(total_duration, 1),
        "events": events,
        "script_code": script_code,
        "supported_event_types": ["camera_shot", "dialogue", "audio", "animation", "wait", "vfx", "shake"],
        "message": f"Cutscene '{cutscene_name}' com {len(events)} eventos ({total_duration:.1f}s).",
    }


def cutscene_add_camera_shot(args: dict | None = None) -> dict:
    """Define um shot de câmera para cutscene.

    Configura posição, zoom, transição e duração de um plano
    de câmera individual para uso em cutscene.

    Args:
        target: Nó alvo para a câmera focar.
        transition: Tipo de transição (cut, fade, dissolve, zoom, pan).
        duration_sec: Duração do shot em segundos.
        zoom: Nível de zoom (1.0 = normal).
        shake_intensity: Intensidade de camera shake (0 = sem shake).

    Returns:
        dict com configuração do shot.
    """
    args = args or {}
    target = args.get("target", "")
    transition = args.get("transition", "cut")
    duration_sec = args.get("duration_sec", 2.0)
    zoom = args.get("zoom", 1.0)
    shake_intensity = args.get("shake_intensity", 0.0)

    if transition not in _CAMERA_TRANSITIONS:
        return {"status": "error", "message": f"Transicao invalida: {transition}. Opcoes: {_CAMERA_TRANSITIONS}"}
    if duration_sec < 0:
        return {"status": "error", "message": "duration_sec deve ser >= 0."}
    if zoom <= 0:
        return {"status": "error", "message": "zoom deve ser > 0."}

    shot = {
        "type": "camera_shot",
        "target": target,
        "transition": transition,
        "duration_sec": duration_sec,
        "zoom": zoom,
        "shake_intensity": shake_intensity,
        "params": {"target": target, "transition": transition, "duration": duration_sec},
        "time_sec": 0.0,  # Será definido pelo timeline
    }

    return {
        "status": "success",
        "shot": shot,
        "message": f"Shot de camera: {transition} para '{target or 'posicao atual'}' ({duration_sec}s).",
    }


def cutscene_add_dialogue_event(args: dict | None = None) -> dict:
    """Adiciona um evento de diálogo à cutscene.

    Args:
        speaker: Nome do falante.
        text: Texto do diálogo.
        duration_sec: Duração em tela.
        emotion: Emoção/expressão do personagem.

    Returns:
        dict com evento de diálogo configurado.
    """
    args = args or {}
    speaker = args.get("speaker", "Narrador")
    text = args.get("text", "")
    duration_sec = args.get("duration_sec", 3.0)
    emotion = args.get("emotion", "neutral")

    if not text:
        return {"status": "error", "message": "text é obrigatório."}

    return {
        "status": "success",
        "event": {
            "type": "dialogue",
            "speaker": speaker,
            "text": text,
            "duration_sec": duration_sec,
            "emotion": emotion,
            "params": {"speaker": speaker, "text": text},
        },
        "message": f"Evento de dialogo: '{speaker}: {text[:50]}...'",
    }
