"""pipeline_ops.py — Pipeline Executor: workflows multi-subsistema (Onda 7)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def create_entity(name: str, entity_type: str = "enemy", description: str = "",
                  behavior: str = "patrol", generate_art: bool | None = None,
                  generate_audio: bool | None = None, art_style: str = "scifi",
                  save_path: str | None = None) -> dict:
    """Cria uma entidade COMPLETA: cena + collider + script + sprite + audio. TUDO automatico."""
    from tools.project_ops import _get_active_project, _check_path_traversal
    from tools.project_state import get_state, refresh_state, on_file_written
    from tools.decision_engine import decide_art, decide_audio, suggest_next

    proj = _get_active_project()
    refresh_state(proj)

    if not save_path:
        safe_name = name.lower().replace(' ', '_')
        save_path = f"scenes/{entity_type}s/{safe_name}.tscn"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    node_types = {"enemy": "CharacterBody2D", "player": "CharacterBody2D",
                  "tower": "StaticBody2D", "npc": "CharacterBody2D",
                  "item": "Area2D", "projectile": "Area2D"}
    godot_type = node_types.get(entity_type, "Node2D")

    steps, warnings, artifacts = [], [], []

    # 1. Criar cena
    try:
        from tools.scene_ops import create_scene, add_node, set_node_property
        r = create_scene(name, godot_type, save_path)
        if r.get("status") != "success":
            return {"status": "error", "step": "create_scene", "message": r.get("message", "Erro")}
        steps.append({"step": "scene", "status": "ok", "path": save_path})
        artifacts.append(save_path)
        on_file_written(save_path)
    except Exception as e:
        return {"status": "error", "step": "create_scene", "message": str(e)}

    # 2. CollisionShape2D
    try:
        cn = f"{name}_collision"
        r = add_node(save_path, ".", cn, "CollisionShape2D")
        if r.get("status") == "success":
            steps.append({"step": "collision", "status": "ok"})
        else:
            warnings.append(f"Collision: {r.get('message','')}")
            steps.append({"step": "collision", "status": "skipped"})
    except Exception as e:
        warnings.append(f"Collision error: {e}")
        steps.append({"step": "collision", "status": "error"})

    # 3. Script
    script_path = save_path.replace('.tscn', '.gd')
    script_created = False
    if behavior != "none" and entity_type in ("enemy", "player", "npc"):
        try:
            from tools.behavior_ops import behavior_tree_generate
            r = behavior_tree_generate(description=f"{entity_type} {name}: {description}", behavior_name=name.replace(' ',''),
                                       tree_type="selector", save_path=script_path)
            if r.get("status") == "success":
                steps.append({"step": "script", "status": "ok", "lines": r.get("lines", 0)})
                script_created = True
                on_file_written(script_path)
            else:
                _write_basic_script(proj, script_path, godot_type, name, entity_type, description)
                steps.append({"step": "script", "status": "ok", "fallback": True})
                script_created = True
                on_file_written(script_path)
        except Exception:
            _write_basic_script(proj, script_path, godot_type, name, entity_type, description)
            steps.append({"step": "script", "status": "ok", "fallback": True})
            script_created = True
            on_file_written(script_path)
    else:
        steps.append({"step": "script", "status": "skipped"})

    # 4. Arte
    art_decision = decide_art(name, godot_type)
    if generate_art is True or (generate_art is None and art_decision["should_generate"]):
        try:
            gen = art_decision.get("generator", "placeholder")
            art_save = f"assets/sprites/{entity_type}s/{name}.png"
            if gen == "flux":
                from tools.flux_ops import generate_game_art_flux
                r = generate_game_art_flux(description or f"{entity_type} {name}", category="inimigo" if entity_type == "enemy" else entity_type,
                                           style=art_style, width=64, height=64, save_path=art_save)
            else:
                from tools.placeholder_ops import generate_placeholder_sprite
                r = generate_placeholder_sprite(name=name, width=64, height=64, save_path=art_save)
            steps.append({"step": "art", "status": "ok" if r.get("status") == "success" else "error", "generator": gen})
            if r.get("status") == "success":
                artifacts.append(art_save)
                on_file_written(art_save)
        except Exception as e:
            steps.append({"step": "art", "status": "error", "reason": str(e)})
    else:
        steps.append({"step": "art", "status": "skipped", "reason": art_decision["reason"]})

    # 5. Audio
    audio_decision = decide_audio(name)
    if generate_audio is True or (generate_audio is None and audio_decision["should_generate"]):
        try:
            from tools.placeholder_ops import generate_audio_sfx
            safe_audio_name = name.lower().replace(' ', '_')
            r = generate_audio_sfx(name=name, sfx_type=audio_decision.get("sfx_type", "beep"),
                                   duration=0.3, save_path=f"assets/audio/sfx/{safe_audio_name}.wav")
            steps.append({"step": "audio", "status": "ok" if r.get("status") == "success" else "error"})
            if r.get("status") == "success":
                artifacts.append(r.get("saved_to", ""))
                on_file_written(r.get("saved_to", ""))
        except Exception as e:
            steps.append({"step": "audio", "status": "error", "reason": str(e)})
    else:
        steps.append({"step": "audio", "status": "skipped", "reason": audio_decision["reason"]})

    refresh_state(proj)
    suggestions = suggest_next(name)

    return {"status": "success", "entity": {"name": name, "type": entity_type, "scene": save_path,
             "script": script_path if script_created else None},
            "steps_completed": steps, "artifacts_created": [a for a in artifacts if a],
            "suggestions": suggestions, "warnings": warnings,
            "message": f"'{name}' criado! {sum(1 for s in steps if s['status']=='ok')}/{len(steps)} etapas OK."}


def project_status() -> dict:
    """Retorna status completo do projeto."""
    from tools.project_ops import _get_active_project
    from tools.project_state import get_state, refresh_state
    proj = _get_active_project()
    refresh_state(proj)
    st = get_state()
    summary = st.summary()

    missing = []
    for sp, sc in st.scenes.items():
        for node in sc.get("nodes", []):
            if node["type"] in ("CharacterBody2D", "StaticBody2D"):
                if not st.has_sprite_for(node["name"]):
                    missing.append(f"{node['name']} ({node['type']}) em {sp} — sem sprite")

    suggestions = []
    stage = summary["stage"]
    if stage == "prototipo" and summary["sprites"] < 3:
        suggestions.append("Gerar sprites placeholder (use create_entity)")
    if summary["audio_files"] == 0:
        suggestions.append("Adicionar SFX (use create_entity com generate_audio=true)")

    return {"status": "success", "summary": summary, "missing": missing[:10], "suggestions": suggestions}


def _write_basic_script(proj, script_path, godot_type, name, entity_type, description):
    code = f"extends {godot_type}\n\n# {entity_type}: {name}\n# {description}\n\nfunc _ready():\n\tpass\n\nfunc _physics_process(delta):\n\tpass\n"
    full = proj / script_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(code, encoding='utf-8')
