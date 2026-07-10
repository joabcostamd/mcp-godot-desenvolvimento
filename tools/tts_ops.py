"""tts_ops.py — Text-to-Speech local com Kokoro TTS (ONNX).

Modelo open-weight Apache 2.0, 82M parametros, roda em CPU.
Fallback: edge-tts (gratuito, vozes Microsoft) se Kokoro nao instalado.
"""

import base64
import io
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Kokoro ONNX (opcional, fallback para edge-tts) — lazy load (P1-2)
_KOKORO = None
_HAS_KOKORO = False
try:
    import kokoro_onnx
    _HAS_KOKORO = True
except ImportError:
    pass

def _get_kokoro():
    """Lazy-load Kokoro model (~82M params) only on first TTS call."""
    global _KOKORO
    if _KOKORO is None and _HAS_KOKORO:
        try:
            from kokoro_onnx import Kokoro
            _KOKORO = Kokoro("kokoro-v0_19.onnx", "voices.json")
        except Exception:
            return None
    return _KOKORO

# Edge TTS (fallback gratuito)
try:
    import edge_tts
    _HAS_EDGE_TTS = True
except ImportError:
    _HAS_EDGE_TTS = False


# ══════════════════════════════════════════════════════════════
# TOOL: generate_voice
# ══════════════════════════════════════════════════════════════

def generate_voice(
    text: str,
    voice: str = "af_heart",
    speed: float = 1.0,
    language: str = "pt",
    save_path: str | None = None,
) -> dict:
    """Gera narracao/fala a partir de texto usando TTS local.

    Usa Kokoro TTS (local, offline, Apache 2.0) como primario.
    Fallback para Edge TTS (gratuito, vozes Microsoft) se Kokoro offline.

    Args:
        text: Texto para converter em fala (max 500 caracteres).
        voice: Voz a usar.
            Kokoro: af_heart, af_bella, af_nicole, af_sarah, af_sky,
                    am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis
            Edge TTS (pt-BR): pt-BR-AntonioNeural, pt-BR-FranciscaNeural
        speed: Velocidade da fala (0.5 a 2.0).
        language: Idioma (pt, en, ja, zh, kr, fr).
        save_path: Caminho relativo no projeto (auto se None).

    Returns:
        {"status": "success", "saved_to": str, "audio_base64": str,
         "engine": "kokoro"|"edge-tts", "duration": float}
    """
    from tools.project_ops import _get_active_project, _check_path_traversal

    proj = _get_active_project()

    if not save_path:
        safe_name = text[:30].replace(" ", "_").replace(".", "").replace("!", "")
        save_path = f"assets/audio/voice/{safe_name}.mp3"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    audio_bytes = None
    engine = "unknown"
    sample_rate = 24000

    # ── Tentar Kokoro primeiro ─────────────────────────────

    kokoro = _get_kokoro()
    if kokoro is not None:
        try:
            samples, sr = kokoro.create(text, voice=voice, speed=speed)
            sample_rate = sr

            import numpy as np
            samples_int16 = (samples * 32767).astype(np.int16)

            buf = io.BytesIO()
            with wave.open(buf, "w") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(samples_int16.tobytes())

            audio_bytes = buf.getvalue()
            engine = "kokoro"

        except Exception:
            pass  # fallback para edge-tts

    # ── Fallback: Edge TTS ─────────────────────────────────

    if audio_bytes is None and _HAS_EDGE_TTS:
        import asyncio
        import tempfile

        async def _edge_tts():
            edge_voice = voice
            if language == "pt":
                edge_voice = "pt-BR-AntonioNeural"
            elif language == "en":
                edge_voice = "en-US-GuyNeural"
            elif language == "ja":
                edge_voice = "ja-JP-NanamiNeural"
            elif language == "zh":
                edge_voice = "zh-CN-XiaoxiaoNeural"
            elif language == "kr":
                edge_voice = "ko-KR-SunHiNeural"
            elif language == "fr":
                edge_voice = "fr-FR-DeniseNeural"

            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            communicate = edge_tts.Communicate(text, edge_voice)
            await communicate.save(tmp.name)
            return tmp.name

        try:
            # Verifica se há event loop ativo (MCP server usa asyncio)
            import asyncio as _asyncio_mod
            try:
                loop = _asyncio_mod.get_running_loop()
            except RuntimeError:
                # Sem loop ativo — pode usar asyncio.run() diretamente
                tmp_path = _asyncio_mod.run(_edge_tts())
            else:
                # Loop ativo — usar thread separada para evitar RuntimeError
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(lambda: _asyncio_mod.run(_edge_tts()))
                    tmp_path = future.result(timeout=30)
            audio_bytes = Path(tmp_path).read_bytes()
            engine = "edge-tts"
            sample_rate = 24000
            Path(tmp_path).unlink()  # limpar
        except Exception as e:
            return {"status": "error",
                    "message": f"TTS indisponivel. Instale Kokoro: pip install kokoro-onnx soundfile. "
                               f"Ou Edge TTS: pip install edge-tts. Erro: {e}"}

    if audio_bytes is None:
        return {"status": "error",
                "message": "Nenhum engine TTS disponivel. "
                           "Instale Kokoro: pip install kokoro-onnx soundfile"}

    # Salvar arquivo
    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_bytes(audio_bytes)

    # Base64 para MCP
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    # Calcular duracao aproximada
    duration = len(audio_bytes) / (sample_rate * 2)  # 16-bit mono

    return {
        "status": "success",
        "saved_to": save_path,
        "audio_base64": audio_b64,
        "engine": engine,
        "duration": round(duration, 2),
        "mime_type": "audio/wav" if engine == "kokoro" else "audio/mpeg",
    }
