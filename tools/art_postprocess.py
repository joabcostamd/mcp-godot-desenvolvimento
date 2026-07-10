"""art_postprocess.py — Pos-processamento de arte para jogos.

Operacoes:
    - Remover fundo (rembg/birefnet)
    - Comprimir PNG (oxipng lossless)
    - Criar sprite sheet a partir de frames
"""

import base64
import subprocess
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False

try:
    from rembg import remove, new_session
    _HAS_REMBG = True
    _REMBG_SESSION = None  # lazy init
except ImportError:
    _HAS_REMBG = False

ROOT = Path(__file__).resolve().parent.parent


def _get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None and _HAS_REMBG:
        try:
            _REMBG_SESSION = new_session("birefnet-general")
        except Exception:
            _REMBG_SESSION = new_session()  # fallback para modelo padrao
    return _REMBG_SESSION


# ══════════════════════════════════════════════════════════════
# TOOL 1: remove_background
# ══════════════════════════════════════════════════════════════

def remove_background(
    image_path: str,
    output_path: str | None = None,
) -> dict:
    """Remove o fundo de uma imagem usando IA (rembg/birefnet).

    Args:
        image_path: Caminho da imagem com fundo (relativo ao projeto ou absoluto)
        output_path: Caminho de saida (auto se None: mesmo nome + _nobg)

    Returns:
        {"status": "success", "output_path": str, "image_base64": str}
    """
    if not _HAS_REMBG:
        return {"status": "error", "message": "rembg nao instalado. Execute: pip install rembg[cpu]"}

    from tools.project_ops import _get_active_project, _check_path_traversal

    proj = _get_active_project()
    input_full = Path(image_path) if Path(image_path).is_absolute() else proj / image_path

    if not input_full.exists():
        return {"status": "error", "message": f"Imagem nao encontrada: {image_path}"}

    if not output_path:
        output_path = str(input_full.parent / f"{input_full.stem}_nobg{input_full.suffix}")

    output_full = proj / output_path if not Path(output_path).is_absolute() else Path(output_path)

    violation = _check_path_traversal(str(output_full.relative_to(proj)), proj)
    if violation:
        return {"status": "error", "message": violation}

    try:
        img = Image.open(input_full)
        session = _get_rembg_session()
        result = remove(img, session=session)
        output_full.parent.mkdir(parents=True, exist_ok=True)
        result.save(output_full, "PNG")

        buf = BytesIO()
        result.save(buf, "PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        return {
            "status": "success",
            "output_path": str(output_full.relative_to(proj)),
            "image_base64": b64,
            "message": f"Fundo removido: {input_full.name} -> {output_full.name}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao remover fundo: {e}"}


# ══════════════════════════════════════════════════════════════
# TOOL 2: optimize_sprite
# ══════════════════════════════════════════════════════════════

def optimize_sprite(
    image_path: str,
    lossless: bool = True,
) -> dict:
    """Otimiza/compacta sprite PNG para producao.

    Usa oxipng (lossless, 10-30% reducao) como padrao.

    Args:
        image_path: Caminho da imagem PNG
        lossless: True = compressao sem perda (oxipng), False = tenta pngquant

    Returns:
        {"status": "success", "original_size": int, "optimized_size": int,
         "reduction_percent": float}
    """
    from tools.project_ops import _get_active_project

    proj = _get_active_project()
    img_full = Path(image_path) if Path(image_path).is_absolute() else proj / image_path

    if not img_full.exists():
        return {"status": "error", "message": f"Imagem nao encontrada: {image_path}"}

    original_size = img_full.stat().st_size

    try:
        if lossless:
            result = subprocess.run(
                ["oxipng", "-o", "3", "--strip", "safe", str(img_full)],
                capture_output=True, text=True, timeout=30,
            )
        else:
            # pngquant para compressao lossy (qualidade 80-95)
            result = subprocess.run(
                ["pngquant", "--quality=80-95", "--ext", ".png", "--force", str(img_full)],
                capture_output=True, text=True, timeout=30,
            )

        optimized_size = img_full.stat().st_size
        reduction = round((1 - optimized_size / original_size) * 100, 1)

        return {
            "status": "success",
            "original_size": original_size,
            "optimized_size": optimized_size,
            "reduction_percent": reduction,
            "message": f"Reducao de {reduction}% ({original_size} -> {optimized_size} bytes)",
        }
    except FileNotFoundError:
        return {"status": "error",
                "message": "oxipng nao encontrado. Instale: https://github.com/shi-yan/oxipng/releases"}
    except Exception as e:
        return {"status": "error", "message": f"Erro na otimizacao: {e}"}


# ══════════════════════════════════════════════════════════════
# TOOL 3: create_spritesheet
# ══════════════════════════════════════════════════════════════

def create_spritesheet(
    frame_paths: list[str],
    output_path: str,
    frame_width: int = 64,
    frame_height: int = 64,
    columns: int = 4,
    gap: int = 0,
) -> dict:
    """Cria sprite sheet a partir de frames individuais.

    Args:
        frame_paths: Lista de caminhos das imagens de cada frame
        output_path: Caminho de saida para a sprite sheet
        frame_width: Largura de cada frame
        frame_height: Altura de cada frame
        columns: Numero de colunas na sprite sheet
        gap: Espaco entre frames em pixels

    Returns:
        {"status": "success", "saved_to": str, "total_frames": int,
         "grid": [cols, rows], "image_base64": str}
    """
    if not _HAS_PILLOW:
        return {"status": "error", "message": "Pillow nao instalado"}

    from tools.project_ops import _get_active_project, _check_path_traversal

    proj = _get_active_project()

    violation = _check_path_traversal(output_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    frames = []
    for fp in frame_paths:
        img_full = Path(fp) if Path(fp).is_absolute() else proj / fp
        if not img_full.exists():
            return {"status": "error", "message": f"Frame nao encontrado: {fp}"}
        img = Image.open(img_full).convert("RGBA")
        img = img.resize((frame_width, frame_height), Image.LANCZOS)
        frames.append(img)

    rows = (len(frames) + columns - 1) // columns
    sheet_w = columns * frame_width + (columns - 1) * gap
    sheet_h = rows * frame_height + (rows - 1) * gap

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * (frame_width + gap)
        y = row * (frame_height + gap)
        sheet.paste(frame, (x, y))

    full_out = proj / output_path
    full_out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(full_out, "PNG")

    buf = BytesIO()
    sheet.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return {
        "status": "success",
        "saved_to": output_path,
        "total_frames": len(frames),
        "grid": [columns, rows],
        "image_base64": b64,
    }
