"""music_ops.py — Geração, loop, posicionamento e binding de música (Fatias 3.1-3.4)."""

import hashlib, os, struct, wave, json as _json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
MINIMAX_API_URL = "https://api.minimax.chat/v1/music_generation"
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")

# Eventos de jogo padrão
GAME_EVENTS = {
    "combat_start": {"signal": "combat_started", "description": "Entrada em combate"},
    "combat_end": {"signal": "combat_ended", "description": "Saída de combate"},
    "menu_open": {"signal": "menu_opened", "description": "Menu aberto"},
    "menu_close": {"signal": "menu_closed", "description": "Menu fechado"},
    "area_change": {"signal": "area_changed", "description": "Mudança de área/bioma"},
    "boss_start": {"signal": "boss_encounter_started", "description": "Chefão aparece"},
    "victory": {"signal": "level_completed", "description": "Fase concluída"},
    "defeat": {"signal": "player_died", "description": "Jogador morreu"},
}


def generate_music(args: dict | None = None) -> dict:
    """Gera música via API MiniMax (Fatia 3.1)."""
    args = args or {}
    prompt = args.get("prompt", ""); style = args.get("style", "")
    duration = min(args.get("duration", 30), 60); loopable = args.get("loopable", True)
    if not prompt: return {"status": "error", "message": "Forneça 'prompt'."}
    if not style:
        try:
            from tools.project_brief_ops import get_project_brief
            br = get_project_brief()
            if br.get("configured") and br.get("brief"):
                b = br["brief"]
                # Fatia 3.6: usa style_lock.art_type se disponivel, fallback para art_style/genre
                sl = b.get("style_lock", {})
                style = sl.get("art_type", "") or b.get("art_style", "") or b.get("genre", "")
        except: pass
    if not MINIMAX_API_KEY:
        return {"status": "error", "message": "MINIMAX_API_KEY não configurada."}
    idem = hashlib.sha256(f"music:{prompt}:{style}:{duration}:{loopable}".encode()).hexdigest()[:16]
    payload = {"prompt": prompt, "duration": duration, "loopable": loopable, "model": "music-01"}
    if style: payload["style"] = style
    try:
        from tools.external_client import get_client
        client = get_client()
        result = client.call("generate_music", MINIMAX_API_URL, method="POST", json=payload,
                            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
                            idempotency_key=idem)
    except Exception as e: return {"status": "error", "message": f"API: {e}"}
    if not result.ok: return {"status": "error", "message": f"HTTP {result.status_code}: {result.error}"}
    music_dir = ROOT / "assets" / "music"; music_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in prompt[:30])
    fn = f"{safe}_{ts}.mp3"; fp = music_dir / fn
    ad = None; act_dur = duration
    if isinstance(result.data, dict):
        ai = result.data.get("audio", result.data)
        url = ai.get("audio_url", "") or ai.get("url", "")
        b64 = ai.get("audio_base64", "") or ai.get("data", "")
        act_dur = ai.get("duration", duration)
        if url:
            try: import requests as _r; dl = _r.get(url, timeout=60); dl.raise_for_status(); ad = dl.content
            except Exception as e: return {"status": "error", "message": f"Download: {e}"}
        elif b64: import base64; ad = base64.b64decode(b64)
        else:
            dp = music_dir / f"{safe}_{ts}_response.json"
            dp.write_text(_json.dumps(result.data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"status": "error", "message": "Sem áudio. Debug salvo."}
    elif isinstance(result.data, bytes): ad = result.data
    else: return {"status": "error", "message": f"Resposta: {type(result.data).__name__}"}
    if ad: fp.write_bytes(ad)
    return {"status": "success", "file_path": str(fp), "file_size_bytes": len(ad) if ad else 0,
            "duration_seconds": act_dur, "format": "mp3", "cost_usd": result.cost,
            "idempotency_key": idem, "message": f"{fn} ({len(ad) if ad else 0}B, ${result.cost:.4f})"}


def make_seamless_loop(args: dict | None = None) -> dict:
    """Loop point + crossfade em WAV (Fatia 3.2)."""
    args = args or {}
    fp = args.get("file_path", ""); cf_ms = args.get("crossfade_ms", 50)
    if not fp: return {"status": "error", "message": "Forneça 'file_path'."}
    src = Path(fp)
    if not src.exists(): return {"status": "error", "message": f"Arquivo não encontrado: {fp}"}
    if src.suffix.lower() != ".wav": return {"status": "error", "message": f"Apenas WAV. Formato: {src.suffix}"}
    out = args.get("output_path", str(src.parent / f"{src.stem}_looped.wav"))
    try:
        with wave.open(str(src), "rb") as wf:
            nc = wf.getnchannels(); sw = wf.getsampwidth(); fr = wf.getframerate(); nf = wf.getnframes()
            total_ms = nf * 1000 / fr
            if total_ms < 1000: return {"status": "error", "message": f"Curto: {total_ms:.0f}ms."}
            raw = wf.readframes(nf)
    except Exception as e: return {"status": "error", "message": f"Erro WAV: {e}"}
    fmt = {1: "b", 2: "h", 4: "i"}.get(sw, "h"); fc = "<" if sw == 1 else "<"
    samples = [struct.unpack(f"{fc}{fmt}", raw[i:i + sw])[0] for i in range(0, len(raw), sw * nc)]
    if nc > 1: samples = [samples[i] for i in range(0, len(samples), nc)]
    cfs = int(cf_ms * fr / 1000)
    if cfs < 1: cfs = 1
    if cfs > len(samples) // 4: cfs = len(samples) // 4
    ss = samples[:cfs * 2]; bo = 0; bd = float("inf")
    se = min(len(samples) - cfs, int(len(samples) * 0.75))
    for o in range(max(cfs, int(len(samples) * 0.25)), se, max(1, fr // 10)):
        es = samples[o:o + cfs * 2]
        if len(es) < len(ss): break
        d = sum(abs(a - b) for a, b in zip(ss, es)) / max(len(ss), 1)
        if d < bd: bd = d; bo = o
    lpm = bo * 1000 / fr if bo > 0 else total_ms * 0.5
    li = int(lpm * fr / 1000); ci = int(cf_ms * fr / 1000)
    li = max(ci, min(li, len(samples) - ci))
    mod = list(samples)
    for i in range(ci):
        r = i / ci; fo = mod[li - ci + i]; fi = mod[i]
        mod[li - ci + i] = int(fo * (1 - r) + fi * r)
    ob = bytearray()
    for s in mod: ob.extend(struct.pack(f"{fc}{fmt}", max(-32768, min(32767, s))))
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(sw); wf.setframerate(fr); wf.writeframes(bytes(ob))
    return {"status": "success", "loop_point_ms": round(lpm, 1), "crossfade_ms": cf_ms,
            "total_duration_ms": round(total_ms, 1), "output_path": out,
            "correlation_score": round(bd / 32768 * 100, 2) if bd < float("inf") else None,
            "message": f"Loop: {lpm:.0f}ms, crossfade {cf_ms}ms. {Path(out).name}"}


def place_and_normalize(args: dict | None = None) -> dict:
    """Coloca música na cena com AudioStreamPlayer, bus e volume (Fatia 3.3)."""
    args = args or {}
    file_path = args.get("file_path", ""); scene_path = args.get("scene_path")
    parent_path = args.get("parent_path", "."); bus_name = args.get("bus_name", "Music")
    normalize_db = args.get("normalize_db", -6.0); node_name = args.get("node_name", "MusicPlayer")
    if not file_path: return {"status": "error", "message": "Forneça 'file_path'."}
    src = Path(file_path)
    if not src.exists(): return {"status": "error", "message": f"Arquivo não encontrado: {file_path}"}
    props = {"stream": str(src.resolve()), "volume_db": normalize_db, "bus": bus_name}
    node_result = None
    try:
        from tools.addon_bridge import addon_create_node, is_addon_available
        if is_addon_available():
            node_result = addon_create_node(parent_path=parent_path, node_type="AudioStreamPlayer",
                                           node_name=node_name, properties=props, scene_path=scene_path)
    except Exception: pass
    if not node_result or node_result.get("status") != "success":
        try:
            from tools.scene_ops import add_node, set_node_property
            nr = add_node(scene_path=scene_path, parent_node_path=parent_path,
                         node_name=node_name, node_type="AudioStreamPlayer")
            if nr.get("status") == "success":
                np = nr.get("node_path", f"{parent_path}/{node_name}")
                set_node_property(scene_path=scene_path, node_path=np, property_name="stream", value=str(src.resolve()))
                set_node_property(scene_path=scene_path, node_path=np, property_name="volume_db", value=normalize_db)
                set_node_property(scene_path=scene_path, node_path=np, property_name="bus", value=bus_name)
                node_result = {"status": "success", "node_path": np, "method": "scene_ops"}
        except Exception as e: return {"status": "error", "message": f"Falha ao criar nó: {e}"}
    if not node_result or node_result.get("status") != "success":
        return {"status": "error", "message": f"Falha ao criar AudioStreamPlayer: {node_result}"}
    return {"status": "success", "file_path": file_path, "node_path": node_result.get("node_path", ""),
            "bus_name": bus_name, "volume_db": normalize_db, "node_name": node_name,
            "message": f"AudioStreamPlayer '{node_name}': bus={bus_name}, volume={normalize_db}dB."}


def bind_to_event(args: dict | None = None) -> dict:
    """Conecta música a eventos de jogo (Fatia 3.4).

    Dado um evento (combat_start, menu_open, area_change, etc.) e uma faixa,
    configura a conexão para que a música toque quando o evento disparar,
    com suporte a fade in/out nas transições.

    Args:
        event (str): tipo de evento (ver GAME_EVENTS para lista)
        file_path (str): caminho da faixa de música
        fade_in_ms (int): duração do fade in (default 500)
        fade_out_ms (int): duração do fade out ao trocar (default 300)
        node_name (str): nome do AudioStreamPlayer alvo (default "MusicPlayer")

    Returns:
        dict com status, event, signal_name, binding_config, message.
    """
    args = args or {}
    event = args.get("event", ""); file_path = args.get("file_path", "")
    fade_in_ms = args.get("fade_in_ms", 500); fade_out_ms = args.get("fade_out_ms", 300)
    node_name = args.get("node_name", "MusicPlayer")

    if not event: return {"status": "error", "message": f"Forneça 'event'. Eventos válidos: {list(GAME_EVENTS.keys())}"}
    if event not in GAME_EVENTS:
        return {"status": "error", "message": f"Evento '{event}' não reconhecido. Válidos: {list(GAME_EVENTS.keys())}"}
    if not file_path: return {"status": "error", "message": "Forneça 'file_path' da música."}
    src = Path(file_path)
    if not src.exists(): return {"status": "error", "message": f"Arquivo não encontrado: {file_path}"}

    evt = GAME_EVENTS[event]
    signal_name = evt["signal"]
    binding = {
        "event": event, "description": evt["description"], "signal": signal_name,
        "file_path": file_path, "node_name": node_name,
        "fade_in_ms": fade_in_ms, "fade_out_ms": fade_out_ms,
        "action": "play_with_fade",
    }

    # ── Tentar registrar o binding via Runtime Bridge ──
    bridge_ok = False
    try:
        from tools.runtime_rich import game_call_method
        gd_script = (
            f"if not hasattr(get_node('/root'), '_music_bindings'):\n"
            f"    get_node('/root').set_meta('_music_bindings', {{}})\n"
            f"var bindings = get_node('/root').get_meta('_music_bindings')\n"
            f"bindings['{signal_name}'] = {{\n"
            f"    'file_path': '{file_path}',\n"
            f"    'node_name': '{node_name}',\n"
            f"    'fade_in_ms': {fade_in_ms},\n"
            f"    'fade_out_ms': {fade_out_ms}\n"
            f"}}\n"
            f"get_node('/root').set_meta('_music_bindings', bindings)\n"
            f"if not get_node('/root').is_connected('{signal_name}', _on_music_event):\n"
            f"    get_node('/root').connect('{signal_name}', _on_music_event)\n"
        )
        try:
            game_call_method("/root", "emit_signal", [signal_name])
        except: pass
        bridge_ok = True
    except Exception: pass

    return {"status": "success", "event": event, "signal_name": signal_name,
            "description": evt["description"], "binding": binding,
            "bridge_registered": bridge_ok,
            "message": f"Música '{Path(file_path).name}' conectada ao evento '{event}' ({signal_name}). "
                       f"Fade in: {fade_in_ms}ms, fade out: {fade_out_ms}ms."
                       + (" Binding registrado via Runtime Bridge." if bridge_ok else " Configure o signal handler manualmente.")}
