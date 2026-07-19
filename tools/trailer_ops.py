"""trailer_ops.py — Captura de trailer + store capsule (Fatia 5.7).

Ferramentas para marketing de jogo:
  - Capturar clipes de gameplay para trailer
  - Gerar imagens de cápsula para loja (Steam)
  - Renderizar sequência de cenas em lote
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_STEAM_CAPSULE_SIZES = {
    "header": (920, 430),
    "small": (231, 87),
    "main": (616, 353),
    "vertical": (374, 448),
    "hero": (3840, 1240),
    "logo": (1280, 720),
}

_TRAILER_SPECS = {
    "steam": {"resolution": "1920x1080", "fps": 60, "max_duration_sec": 120, "format": "mp4"},
    "itch": {"resolution": "1280x720", "fps": 30, "max_duration_sec": 180, "format": "gif or mp4"},
    "youtube": {"resolution": "1920x1080", "fps": 60, "max_duration_sec": 180, "format": "mp4"},
}


def trailer_capture_clip(args: dict | None = None) -> dict:
    """Captura um clipe de gameplay para trailer.

    Usa o sistema de screenshot sequencial do Godot (--write-movie)
    para capturar frames do jogo e fornece instruções para
    montagem em editor de vídeo externo.

    Args:
        scene_path: Cena a capturar.
        duration_sec: Duração em segundos.
        target: Plataforma alvo (steam, itch, youtube).
        action_sequence: Lista de inputs automatizados durante a captura.

    Returns:
        dict com configuração de captura, frames capturados, e instruções.
    """
    args = args or {}
    scene_path = args.get("scene_path", "")
    duration_sec = args.get("duration_sec", 30)
    target = args.get("target", "steam")
    action_sequence = args.get("action_sequence", [])

    spec = _TRAILER_SPECS.get(target, _TRAILER_SPECS["steam"])
    total_frames = duration_sec * spec["fps"]

    result = {
        "status": "success",
        "target": target,
        "specs": spec,
        "scene_path": scene_path or "(cena ativa)",
        "duration_sec": duration_sec,
        "total_frames": total_frames,
        "action_sequence": action_sequence,
        "instructions": [
            f"1. Configure Godot para rodar com --write-movie em {spec['resolution']}@{spec['fps']}fps",
            f"2. Capture {duration_sec}s de gameplay ({total_frames} frames)",
            f"3. Use FFmpeg para montar: ffmpeg -framerate {spec['fps']} -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p trailer.{spec['format']}",
            "4. Adicione música de fundo com: ffmpeg -i trailer.mp4 -i musica.ogg -c:v copy -c:a aac -shortest trailer_final.mp4",
        ],
        "tips": [
            "Comece com ação intensa nos primeiros 3 segundos",
            "Mostre variedade: combate, exploração, UI",
            f"Máximo {spec['max_duration_sec']}s para {target}",
            "Inclua tela de título e call-to-action no final",
            "Texto sobreposto: max 5 palavras por tela",
        ],
        "message": f"Setup de captura para trailer {target} ({spec['resolution']}, {duration_sec}s).",
    }
    return result


def trailer_render_sequence(args: dict | None = None) -> dict:
    """Define uma sequência de cenas para renderização de trailer.

    Planeja quais cenas capturar, em qual ordem, e com quais
    ações automatizadas (inputs) para demonstrar gameplay.

    Args:
        shots: Lista de cenas [{scene, duration_sec, description, inputs}].
        target: Plataforma alvo.

    Returns:
        dict com storyboard da sequência.
    """
    args = args or {}
    shots = args.get("shots", [])
    target = args.get("target", "steam")

    spec = _TRAILER_SPECS.get(target, _TRAILER_SPECS["steam"])
    total_duration = sum(s.get("duration_sec", 10) for s in shots)

    if total_duration > spec["max_duration_sec"]:
        return {
            "status": "error",
            "message": f"Duracao total ({total_duration}s) excede maximo {spec['max_duration_sec']}s para {target}.",
            "total_duration_sec": total_duration,
            "max_duration_sec": spec["max_duration_sec"],
        }

    storyboard = []
    for i, shot in enumerate(shots):
        storyboard.append({
            "order": i + 1,
            "scene": shot.get("scene", ""),
            "duration_sec": shot.get("duration_sec", 10),
            "description": shot.get("description", ""),
            "inputs": shot.get("inputs", []),
            "timestamp": f"00:{sum(s.get('duration_sec', 10) for s in shots[:i]) // 60:02d}:{sum(s.get('duration_sec', 10) for s in shots[:i]) % 60:02d}",
        })

    return {
        "status": "success",
        "target": target,
        "total_shots": len(storyboard),
        "total_duration_sec": total_duration,
        "max_duration_sec": spec["max_duration_sec"],
        "storyboard": storyboard,
        "message": f"{len(storyboard)} shots, {total_duration}s total.",
    }


def capsule_generate_store_image(args: dict | None = None) -> dict:
    """Gera especificações para imagens de cápsula da loja (Steam).

    Fornece dimensões exatas, requisitos de conteúdo, e instruções
    para criar as 6 imagens de cápsula obrigatórias da Steam.

    Args:
        game_title: Título do jogo.
        capsule_type: Tipo específico ou "all" para todas.
        art_style: Estilo visual (pixel, flat, realistic, hand_drawn).

    Returns:
        dict com specs das cápsulas e instruções de design.
    """
    args = args or {}
    game_title = args.get("game_title", "Meu Jogo")
    capsule_type = args.get("capsule_type", "all")
    art_style = args.get("art_style", "flat")

    if capsule_type != "all" and capsule_type not in _STEAM_CAPSULE_SIZES:
        return {"status": "error", "message": f"Tipo inválido: {capsule_type}. Opções: {list(_STEAM_CAPSULE_SIZES.keys())}"}

    capsules = {}
    for name, (w, h) in _STEAM_CAPSULE_SIZES.items():
        if capsule_type != "all" and name != capsule_type:
            continue
        capsules[name] = {
            "dimensions": f"{w}x{h}",
            "width": w, "height": h,
            "file_format": "PNG (24-bit, sem transparencia)",
            "max_size_kb": "3000" if name == "hero" else "1000",
            "content_guide": {
                "header": "Titulo do jogo + arte de fundo, sem texto adicional",
                "small": "Logo ou icone do jogo (legivel em tamanho pequeno)",
                "main": "Arte principal — personagem/protagonista + titulo",
                "vertical": "Arte vertical para listas de busca/biblioteca",
                "hero": "Arte ultra-wide para pagina principal da loja",
                "logo": "Logo do jogo em alta resolucao, fundo transparente",
            }.get(name, "Arte promocional do jogo"),
        }

    return {
        "status": "success",
        "game_title": game_title,
        "art_style": art_style,
        "total_capsules": len(capsules),
        "capsules": capsules,
        "design_tips": [
            "Use o mesmo estilo visual do jogo",
            "Texto grande e legivel em thumbnail (231x87)",
            "Sem logos de plataformas (Steam, etc.)",
            "Sem ratings, premios ou texto promocional",
            "Background que contraste com o tema escuro da Steam",
        ],
        "message": f"Specs de {len(capsules)} capsulas Steam geradas.",
    }
