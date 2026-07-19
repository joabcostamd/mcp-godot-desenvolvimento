"""audio_ops.py — Fachada unificada de áudio para o MCP Godot Agent.

Centraliza todas as operações de áudio dispersas em múltiplos arquivos:
  - devsolo_ops.py   → configure_audio_bus, add_audio_effect, route_audio_bus,
                        create_spatial_audio_player, scan_scene_for_sfx_events,
                        generate_sfx_batch
  - placeholder_ops.py → generate_audio_sfx
  - music_ops.py       → generate_music, make_seamless_loop, place_and_normalize,
                          bind_to_event
  - tts_ops.py         → generate_voice
  - asset_ops.py       → import_audio
  - runtime_bridge_client.py → play_audio, set_volume, stop_audio (runtime)

Também serve como ponto único de importação para ferramentas que precisam
de áudio, simplificando a detecção de dependências.

Uso:
    from tools.audio_ops import generate_audio_sfx, generate_music, play_audio
"""

# ── SFX (placeholder_ops) ────────────────────────────────────────
from tools.placeholder_ops import generate_audio_sfx

# ── Música (music_ops) ───────────────────────────────────────────
from tools.music_ops import (
    generate_music,
    make_seamless_loop,
    place_and_normalize,
    bind_to_event,
)

# ── Voz/TTS (tts_ops) ────────────────────────────────────────────
from tools.tts_ops import generate_voice

# ── Import de asset (asset_ops) ──────────────────────────────────
from tools.asset_ops import import_audio

# ── Configuração de Bus (devsolo_ops) ────────────────────────────
from tools.devsolo_ops import (
    configure_audio_bus,
    add_audio_effect,
    route_audio_bus,
    create_spatial_audio_player,
    scan_scene_for_sfx_events,
    generate_sfx_batch,
)

# ── Runtime Bridge (controle em tempo real) ──────────────────────
from runtime_bridge_client import play_audio, set_volume, stop_audio

__all__ = [
    # SFX
    "generate_audio_sfx",
    # Música
    "generate_music",
    "make_seamless_loop",
    "place_and_normalize",
    "bind_to_event",
    # Voz
    "generate_voice",
    # Import
    "import_audio",
    # Bus
    "configure_audio_bus",
    "add_audio_effect",
    "route_audio_bus",
    "create_spatial_audio_player",
    "scan_scene_for_sfx_events",
    "generate_sfx_batch",
    # Runtime
    "play_audio",
    "set_volume",
    "stop_audio",
]
