"""live_stream.py — Live Preview com polling de screenshots.

GAP #1 — Live Stream:
Usa o comando screenshot existente do game_bridge em loop via thread
Python. Captura frames a cada N ms (~10fps default) e armazena o
frame mais recente como base64 para consulta.

Sem WebSocket — usa o protocolo TCP existente, apenas em polling.

Uso:
    from tools.live_stream import start_live_preview, stop_live_preview, get_latest_frame
    start_live_preview(interval_ms=100)  # 10fps
    ...
    frame = get_latest_frame()  # {"status": "success", "image_base64": "...", ...}
    stop_live_preview()
"""

import base64
import threading
import time
from pathlib import Path


# ── Estado ───────────────────────────────────────────────────────────

_streaming: bool = False
_stream_thread: threading.Thread | None = None
_latest_frame: dict = {"status": "error", "message": "Nenhum frame capturado."}
_frame_lock = threading.Lock()
_frame_count: int = 0
_interval_ms: int = 100


# ── API Pública ──────────────────────────────────────────────────────

def start_live_preview(interval_ms: int = 100, quality: int = 50) -> dict:
    """Inicia captura contínua de screenshots do jogo rodando.

    Usa polling do game_bridge.screenshot() em thread separada.
    Frames são armazenados e podem ser consultados com get_latest_frame().

    Args:
        interval_ms: Intervalo entre capturas em ms (default 100 = 10fps).
        quality: Qualidade JPEG 1-100 (default 50). Menor = mais rápido.

    Returns:
        {"status": "success", "fps": float, "interval_ms": int}
        ou {"status": "error", "message": str}
    """
    global _streaming, _stream_thread, _interval_ms, _frame_count

    if _streaming:
        return {"status": "success", "fps": 1000.0 / _interval_ms,
                "note": "Live preview já está rodando."}

    # Verifica se game bridge está conectado
    try:
        from tools.bridge import is_game_connected
        if not is_game_connected():
            return {"status": "error",
                    "message": "Game bridge não conectado. Rode o jogo primeiro (run_game)."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao verificar bridge: {e}"}

    _interval_ms = max(50, min(interval_ms, 5000))  # Entre 50ms e 5s
    _frame_count = 0
    _streaming = True

    _stream_thread = threading.Thread(target=_capture_loop, args=(quality,), daemon=True)
    _stream_thread.start()

    fps = 1000.0 / _interval_ms
    return {"status": "success", "fps": round(fps, 1), "interval_ms": _interval_ms}


def stop_live_preview() -> dict:
    """Para a captura contínua de screenshots.

    Returns:
        {"status": "success", "frames_captured": int}
    """
    global _streaming, _stream_thread, _frame_count

    _streaming = False
    if _stream_thread:
        _stream_thread.join(timeout=3.0)
        _stream_thread = None

    count = _frame_count
    _frame_count = 0

    with _frame_lock:
        _latest_frame = {"status": "error", "message": "Nenhum frame capturado."}

    return {"status": "success", "frames_captured": count}


def get_latest_frame() -> dict:
    """Retorna o frame mais recente capturado pelo live preview.

    Returns:
        {"status": "success", "image_base64": str, "image_size_bytes": int,
         "frame_number": int, "timestamp": float, "fps": float}
        ou {"status": "error", "message": str}
    """
    global _frame_count
    with _frame_lock:
        frame = dict(_latest_frame)
        frame["frame_number"] = _frame_count
        if _streaming and _frame_count > 0:
            frame["fps"] = round(1000.0 / _interval_ms, 1)
    return frame


def is_streaming() -> bool:
    """Verifica se o live preview está ativo."""
    return _streaming


# ── Loop Interno ─────────────────────────────────────────────────────

def _capture_loop(quality: int) -> None:
    """Thread que captura screenshots em loop."""
    global _latest_frame, _frame_count, _streaming

    while _streaming:
        start = time.time()

        try:
            from tools.bridge import is_game_connected, _send_game

            if not is_game_connected():
                with _frame_lock:
                    _latest_frame = {"status": "error",
                                     "message": "Game bridge desconectado."}
                time.sleep(1.0)
                continue

            # Captura screenshot via comando existente
            result = _send_game("screenshot", {
                "filename": f"live_{_frame_count}.png"
            }, timeout_override=3)

            if result.get("status") == "success":
                # Lê o PNG do disco e converte para base64
                from tools.runtime_ops import _get_active_project
                proj = _get_active_project()
                import os
                appdata = os.environ.get("APPDATA", "")
                user_dir = Path(appdata) / "Godot" / "app_userdata" / proj.name
                filename = f"live_{_frame_count}.png"
                png_path = user_dir / filename

                if png_path.exists():
                    img_data = png_path.read_bytes()
                    b64 = base64.b64encode(img_data).decode("ascii")

                    with _frame_lock:
                        _latest_frame = {
                            "status": "success",
                            "image_base64": b64,
                            "image_size_bytes": len(img_data),
                            "timestamp": time.time(),
                        }
                else:
                    # Fallback: tenta no próprio resultado
                    with _frame_lock:
                        _latest_frame = {
                            "status": "success",
                            "image_base64": "",
                            "note": "Frame capturado (ver user://)",
                            "timestamp": time.time(),
                        }
            else:
                with _frame_lock:
                    _latest_frame = {"status": "error",
                                     "message": result.get("message", "Falha na captura.")}

            _frame_count += 1

        except Exception as e:
            with _frame_lock:
                _latest_frame = {"status": "error", "message": str(e)}
            time.sleep(0.5)
            continue

        # Mantém o intervalo
        elapsed = (time.time() - start) * 1000
        remaining = _interval_ms - elapsed
        if remaining > 10:
            time.sleep(remaining / 1000.0)
