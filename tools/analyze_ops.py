"""analyze_ops — Análise inteligente do projeto (Onda 4: IA Agêntica).

Permite à IA entender o estado do projeto sem ler dezenas de arquivos.
Métricas estruturais, busca full-text, validação de design, histórico.

Funções:
    analyze_game_structure — métricas completas do projeto
    suggest_next_steps — próximos passos baseado no estado atual
    find_missing_references — referências quebradas em .tscn/.gd
    validate_game_design — checklist de game design
    estimate_game_scope — classificação do tamanho do projeto
    search_codebase — busca full-text em todos os arquivos
    get_project_history — linha do tempo de alterações
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.project_ops import _get_active_project

ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# 4.1 — analyze_game_structure
# ═══════════════════════════════════════════════════════════════════════

def analyze_game_structure() -> dict:
    """Analisa a estrutura completa do projeto ativo.

    Retorna métricas: cenas, scripts, nós, sinais, inputs, autoloads,
    assets, tamanho total.

    Returns:
        {"status": "success", "metrics": {...}, "scenes": [...], "scripts": [...]}
    """
    proj = _get_active_project()

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": "Projeto não encontrado."}

    # ── Coleta arquivos ──────────────────────────────────────────
    scenes = sorted([str(p.relative_to(proj)) for p in proj.glob("**/*.tscn")])
    scripts = sorted([str(p.relative_to(proj)) for p in proj.glob("**/*.gd")])
    assets = sorted([
        str(p.relative_to(proj)) for p in proj.glob("**/*")
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".svg",
                                 ".wav", ".ogg", ".mp3", ".tres", ".res",
                                 ".glb", ".gltf", ".obj")
    ])

    # ── Analisa cenas ────────────────────────────────────────────
    scene_details = []
    total_nodes = 0
    total_signals = 0
    node_types = {}
    for sc in scenes:
        try:
            content = (proj / sc).read_text(encoding="utf-8")
            nodes = re.findall(r'\[node\s+name="([^"]*)"(?:\s+type="([^"]*)")?', content)
            connections = re.findall(r'\[connection\s+', content)
            total_nodes += len(nodes)
            total_signals += len(connections)
            for _, ntype in nodes:
                if ntype:
                    node_types[ntype] = node_types.get(ntype, 0) + 1
            scene_details.append({
                "path": sc,
                "node_count": len(nodes),
                "signal_connections": len(connections),
                "root_type": nodes[0][1] if nodes else "unknown",
            })
        except Exception:
            scene_details.append({"path": sc, "error": "não foi possível analisar"})

    # ── Analisa scripts ──────────────────────────────────────────
    total_script_lines = 0
    script_sizes = []
    for sc in scripts:
        try:
            lines = len((proj / sc).read_text(encoding="utf-8").splitlines())
            total_script_lines += lines
            script_sizes.append({"path": sc, "lines": lines})
        except Exception:
            script_sizes.append({"path": sc, "lines": 0})

    # ── Analisa project.godot ────────────────────────────────────
    godot_config = (proj / "project.godot").read_text(encoding="utf-8")
    project_name = "Unknown"
    m = re.search(r'config/name\s*=\s*"([^"]*)"', godot_config)
    if m:
        project_name = m.group(1)
    main_scene = None
    m = re.search(r'config/run/main_scene\s*=\s*"([^"]*)"', godot_config)
    if m:
        main_scene = m.group(1)
    has_autoload = "[autoload]" in godot_config
    has_input_map = "[input]" in godot_config
    autoloads = []
    if has_autoload:
        autoloads = re.findall(r'(\w+)\s*=\s*"\*?([^"]+)"', godot_config)

    # ── Estatísticas de assets ───────────────────────────────────
    asset_types = {}
    for a in assets:
        ext = Path(a).suffix.lower()
        asset_types[ext] = asset_types.get(ext, 0) + 1

    # ── Tamanho total ────────────────────────────────────────────
    total_size = sum(
        f.stat().st_size for f in proj.rglob("*")
        if f.is_file() and ".godot" not in str(f) and ".mcp_backups" not in str(f)
    )

    # ── Auditoria de Wiring (resumo, sem detalhes completos) ──
    wiring_status = {}
    try:
        from tools.audit_input_map import audit_input_map
        from tools.audit_autoloads import audit_autoloads
        from tools.audit_scene_reachability import audit_scene_reachability

        input_audit = audit_input_map(project_path=str(proj))
        if input_audit.get("status") in ("ok", "issues_found"):
            wiring_status["unused_actions"] = input_audit.get("unused_actions", [])
            wiring_status["undeclared_actions_count"] = len(input_audit.get("undeclared_actions_referenced", []))

        autoload_audit = audit_autoloads(project_path=str(proj))
        if autoload_audit.get("status") in ("ok", "issues_found"):
            wiring_status["possibly_unused_autoloads"] = autoload_audit.get("possibly_unused_autoloads", [])

        reach_audit = audit_scene_reachability(project_path=str(proj))
        if reach_audit.get("status") in ("ok", "issues_found"):
            wiring_status["unreachable_scenes"] = reach_audit.get("unreachable_scenes", [])

        # ── Bloco 2: UID + Save ──
        from tools.audit_uid_consistency import audit_uid_consistency
        from tools.audit_save_compatibility import audit_save_compatibility
        uid_audit = audit_uid_consistency(project_path=str(proj))
        if uid_audit.get("status") in ("ok", "issues_found"):
            wiring_status["uid_duplicates"] = len(uid_audit.get("duplicate_uid", []))
            wiring_status["uid_mismatches"] = len(uid_audit.get("mismatched_uid", []))
        save_audit = audit_save_compatibility(project_path=str(proj))
        if save_audit.get("status") in ("ok", "issues_found"):
            wiring_status["save_key_mismatches"] = len(save_audit.get("write_read_key_mismatch", []))
            wiring_status["save_has_migration"] = save_audit.get("has_migration_logic", False)
            wiring_status["save_has_version"] = save_audit.get("has_version_field", False)
    except Exception:
        pass  # Falha na auditoria não quebra analyze_game_structure

    return {
        "status": "success",
        "project_name": project_name,
        "main_scene": main_scene,
        "metrics": {
            "scene_count": len(scenes),
            "script_count": len(scripts),
            "asset_count": len(assets),
            "total_nodes": total_nodes,
            "total_signal_connections": total_signals,
            "total_script_lines": total_script_lines,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "autoload_count": len(autoloads),
            "has_input_map": has_input_map,
            "has_autoload": has_autoload,
            "unique_node_types": len(node_types),
        },
        "scenes": scene_details,
        "scripts": script_sizes,
        "assets_by_type": asset_types,
        "autoloads": [{"name": a[0], "path": a[1]} for a in autoloads],
        "top_node_types": sorted(node_types.items(), key=lambda x: -x[1])[:10],
        "wiring_status": wiring_status,
    }


# ═══════════════════════════════════════════════════════════════════════
# 4.2 — suggest_next_steps
# ═══════════════════════════════════════════════════════════════════════

def suggest_next_steps() -> dict:
    """Sugere próximos passos baseado no estado atual do projeto.

    Analisa a estrutura e retorna recomendações ordenadas por prioridade.

    Returns:
        {"status": "success", "suggestions": [...], "stage": str}
    """
    analysis = analyze_game_structure()
    if analysis["status"] != "success":
        return analysis

    m = analysis["metrics"]
    suggestions = []
    stage = "unknown"

    # ── Estágio 1: Projeto vazio ─────────────────────────────────
    if m["scene_count"] == 0:
        stage = "vazio"
        suggestions = [
            {"priority": 1, "action": "Criar a cena principal", "tool": "create_scene",
             "detail": "Use create_scene com root_type='Node2D' (2D) ou 'Node3D' (3D)."},
            {"priority": 2, "action": "Configurar o projeto", "tool": "set_project_setting",
             "detail": "Defina o nome do jogo e a resolução."},
            {"priority": 3, "action": "Definir a cena principal", "tool": "set_main_scene",
             "detail": "Essencial para run_game funcionar."},
        ]

    # ── Estágio 2: Projeto básico ────────────────────────────────
    elif m["scene_count"] <= 3 and m["total_nodes"] < 10:
        stage = "básico"
        suggestions = [
            {"priority": 1, "action": "Adicionar entidades ao jogo", "tool": "add_node / add_nodes_batch",
             "detail": "Adicione player, inimigos, cenário."},
            {"priority": 2, "action": "Criar scripts de comportamento", "tool": "generate_gdscript / write_file",
             "detail": "Scripts para movimento, colisão, game logic."},
            {"priority": 3, "action": "Configurar física e colisão", "tool": "add_collision_shape + set_collision_layer_mask",
             "detail": "Essencial para que objetos interajam entre si."},
        ]

    # ── Estágio 3: Em desenvolvimento ────────────────────────────
    elif m["script_count"] > 0 and not m["has_input_map"]:
        stage = "sem_input"
        suggestions = [
            {"priority": 1, "action": "Configurar mapa de input", "tool": "configure_input_action",
             "detail": "É o erro mais comum: scripts usam Input.is_action_pressed() mas ações não existem!"},
            {"priority": 2, "action": "Validar compilação", "tool": "compile_test",
             "detail": "Verifique se não há erros de sintaxe."},
        ]

    elif m["scene_count"] >= 3 and m["script_count"] >= 1:
        stage = "desenvolvimento"
        suggestions = [
            {"priority": 1, "action": "Criar tela de UI/HUD", "tool": "create_ui_scene + add_control_node",
             "detail": "Score, vidas, botões — essencial para o jogador."},
            {"priority": 2, "action": "Rodar e testar", "tool": "run_game",
             "detail": "Teste o jogo para verificar gameplay."},
            {"priority": 3, "action": "Adicionar áudio", "tool": "generate_audio_sfx / import_audio",
             "detail": "Sons de pulo, tiro, coleta melhoram muito a experiência."},
            {"priority": 4, "action": "Criar animações", "tool": "create_animation_player + create_animation",
             "detail": "Animações de idle, walk, jump para sprites."},
        ]

    main = analysis.get("main_scene")
    if not main:
        suggestions.insert(0, {
            "priority": 1, "action": "Definir a cena principal", "tool": "set_main_scene",
            "detail": "Sem main_scene, run_game não funciona. Defina AGORA."})

    if m["total_script_lines"] > 100 and m.get("has_input_map"):
        suggestions.append({
            "priority": len(suggestions) + 1, "action": "Verificar compilação",
            "tool": "compile_test",
            "detail": f"Com {m['total_script_lines']} linhas de código, é bom validar."})

    if m["scene_count"] >= 5 and m["total_nodes"] > 20 and m["script_count"] >= 3:
        suggestions.append({
            "priority": len(suggestions) + 1, "action": "Fazer checkpoint git",
            "tool": "git_commit_checkpoint",
            "detail": "Projeto está crescendo — salve o progresso."})

    # ── Status de wiring (se houver issues) ──
    ws = analysis.get("wiring_status", {})
    wiring_issue_count = (
        len(ws.get("unused_actions", [])) +
        ws.get("undeclared_actions_count", 0) +
        len(ws.get("possibly_unused_autoloads", [])) +
        len(ws.get("unreachable_scenes", [])) +
        ws.get("uid_duplicates", 0) +
        ws.get("uid_mismatches", 0) +
        ws.get("save_key_mismatches", 0)
    )
    if wiring_issue_count > 0:
        summary_parts = []
        if ws.get("unused_actions"):
            summary_parts.append(f"{len(ws['unused_actions'])} ações não usadas")
        if ws.get("undeclared_actions_count", 0) > 0:
            summary_parts.append(f"{ws['undeclared_actions_count']} ações referenciadas sem existir")
        if ws.get("possibly_unused_autoloads"):
            summary_parts.append(f"{len(ws['possibly_unused_autoloads'])} autoloads órfãos")
        if ws.get("unreachable_scenes"):
            summary_parts.append(f"{len(ws['unreachable_scenes'])} cenas inalcançáveis")
        if ws.get("uid_duplicates", 0) > 0:
            summary_parts.append(f"{ws['uid_duplicates']} UIDs duplicados (crítico)")
        if ws.get("uid_mismatches", 0) > 0:
            summary_parts.append(f"{ws['uid_mismatches']} UIDs divergentes")
        if ws.get("save_key_mismatches", 0) > 0:
            summary_parts.append(f"{ws['save_key_mismatches']} chaves de save divergentes")
        if not ws.get("save_has_migration") and ws.get("save_has_version"):
            summary_parts.append("save sem lógica de migração")
        suggestions.insert(0, {
            "priority": 0,
            "action": "Corrigir wiring do projeto",
            "tool": "audit_input_map / audit_autoloads / audit_scene_reachability / audit_uid_consistency / audit_save_compatibility",
            "detail": f"Status de wiring: {', '.join(summary_parts)}.",
        })

    return {"status": "success", "stage": stage, "suggestions": suggestions,
            "metrics_summary": {k: m[k] for k in ["scene_count", "script_count", "total_nodes",
                                                    "total_script_lines", "total_size_mb"]}}


# ═══════════════════════════════════════════════════════════════════════
# 4.3 — find_missing_references
# ═══════════════════════════════════════════════════════════════════════

def find_missing_references() -> dict:
    """Encontra referências quebradas no projeto.

    Verifica .tscn e .gd por: scripts inexistentes, cenas instanciadas
    que não existem, texturas referenciadas mas não importadas.

    Returns:
        {"status": "success", "broken": [...], "warnings": [...]}
    """
    proj = _get_active_project()
    broken = []
    warnings = []

    # ── Coleta todos os caminhos existentes ───────────────────────
    existing = set()
    for f in proj.rglob("*"):
        if f.is_file() and ".godot" not in str(f) and ".mcp_backups" not in str(f):
            existing.add(str(f.relative_to(proj)).replace("\\", "/"))

    # ── Verifica .tscn ───────────────────────────────────────────
    for tscn in proj.glob("**/*.tscn"):
        try:
            content = tscn.read_text(encoding="utf-8")
            # ext_resource path
            for m in re.finditer(r'path\s*=\s*"res://([^"]+)"', content):
                ref = m.group(1)
                if ref not in existing:
                    broken.append({
                        "file": str(tscn.relative_to(proj)),
                        "type": "ext_resource",
                        "reference": ref,
                        "message": f"Recurso 'res://{ref}' referenciado mas não encontrado.",
                    })
            # script = ExtResource ou inline
            for m in re.finditer(r'script\s*=\s*ExtResource\("([^"]+)"\)', content):
                pass  # ext resources não podem ser validados por path inline
        except Exception:
            pass

    # ── Verifica .gd ─────────────────────────────────────────────
    for gd in proj.glob("**/*.gd"):
        try:
            content = gd.read_text(encoding="utf-8")
            # preload("res://...")
            for m in re.finditer(r'preload\s*\(\s*"res://([^"]+)"', content):
                ref = m.group(1)
                if ref not in existing:
                    warnings.append({
                        "file": str(gd.relative_to(proj)),
                        "type": "preload",
                        "reference": ref,
                        "message": f"preload('res://{ref}') — recurso não encontrado.",
                    })
        except Exception:
            pass

    return {
        "status": "success",
        "broken_count": len(broken),
        "warning_count": len(warnings),
        "broken": broken[:20],  # limita a 20
        "warnings": warnings[:20],
        "note": "OK — nenhuma referência quebrada." if not broken and not warnings
                else f"{len(broken)} referências quebradas, {len(warnings)} warnings.",
    }


# ═══════════════════════════════════════════════════════════════════════
# 4.4 — validate_game_design
# ═══════════════════════════════════════════════════════════════════════

def validate_game_design() -> dict:
    """Valida checklist de game design no projeto.

    Verifica se o projeto tem os elementos mínimos para ser jogável.

    Returns:
        {"status": "success", "passed": int, "failed": int, "checks": [...]}
    """
    analysis = analyze_game_structure()
    if analysis["status"] != "success":
        return analysis

    proj = _get_active_project()
    m = analysis["metrics"]
    checks = []

    def check(name: str, condition: bool, ok_msg: str, fail_msg: str, tool: str = ""):
        checks.append({
            "check": name, "passed": condition,
            "message": ok_msg if condition else fail_msg,
            "fix_tool": tool if not condition else None,
        })

    # 1. Projeto existe
    check("Projeto inicializado", m["scene_count"] >= 0,
          "✅ Projeto existe.", "❌ Projeto não encontrado.", "create_project")

    # 2. Tem cena principal
    check("Main scene definida", bool(analysis.get("main_scene")),
          "✅ Main scene configurada.", "❌ Main scene não definida — run_game não funciona.", "set_main_scene")

    # 3. Tem pelo menos uma cena
    check("Pelo menos 1 cena", m["scene_count"] >= 1,
          f"✅ {m['scene_count']} cena(s).", "❌ Nenhuma cena criada.", "create_scene")

    # 4. Tem scripts
    check("Scripts de comportamento", m["script_count"] >= 1,
          f"✅ {m['script_count']} script(s).", "❌ Nenhum script — sem comportamento.", "generate_gdscript")

    # 5. Tem nodes
    check("Nós na árvore", m["total_nodes"] >= 2,
          f"✅ {m['total_nodes']} nós.", "❌ Poucos nós — jogo pode estar vazio.", "add_node")

    # 6. Input map
    check("Input map configurado", m["has_input_map"],
          "✅ Ações de input configuradas.", "❌ Sem input map — jogador não controla nada.", "configure_input_action")

    # 7. Tem UI
    has_ui = any("ui" in s.get("path", "").lower() or "hud" in s.get("path", "").lower()
                 for s in analysis.get("scenes", []))
    check("Interface de usuário (UI)", has_ui,
          "✅ UI encontrada.", "⚠️ Nenhuma cena de UI/HUD — jogador não vê score, vidas, etc.", "create_ui_scene")

    # 8. Tem assets ou placeholders
    check("Assets visuais", m["asset_count"] >= 1,
          f"✅ {m['asset_count']} assets.", "⚠️ Nenhum asset importado — use placeholders.", "generate_placeholder_sprite")

    # 9. Compilação recente
    check("Estrutura de projeto", analysis["metrics"]["total_size_mb"] > 0.01,
          "✅ Projeto tem conteúdo.", "⚠️ Projeto pode estar vazio.")

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed

    return {
        "status": "success",
        "passed": passed,
        "failed": failed,
        "total": len(checks),
        "score": f"{passed}/{len(checks)}",
        "verdict": "✅ PRONTO para testar!" if failed <= 1
                   else "⚠️ EM DESENVOLVIMENTO" if failed <= 3
                   else "🔴 INICIAL — muitas coisas faltando",
        "checks": checks,
    }


# ═══════════════════════════════════════════════════════════════════════
# 4.5 — estimate_game_scope
# ═══════════════════════════════════════════════════════════════════════

def estimate_game_scope() -> dict:
    """Estima o escopo do projeto baseado em métricas.

    Returns:
        {"status": "success", "scope": str, "category": str, "metrics": {...}}
    """
    analysis = analyze_game_structure()
    if analysis["status"] != "success":
        return analysis

    m = analysis["metrics"]
    score = (
        m["scene_count"] * 2
        + m["script_count"] * 3
        + m["total_nodes"] * 0.5
        + m["total_script_lines"] * 0.01
        + m["total_size_mb"] * 5
    )

    if score < 10:
        category = "micro"
        label = "🎯 Micro Jogo (< 10pts)"
    elif score < 40:
        category = "pequeno"
        label = "🎮 Jogo Pequeno (10-40pts)"
    elif score < 100:
        category = "medio"
        label = "🎲 Jogo Médio (40-100pts)"
    elif score < 250:
        category = "grande"
        label = "🏰 Jogo Grande (100-250pts)"
    else:
        category = "epico"
        label = "👑 Jogo Épico (250+ pts)"

    return {
        "status": "success",
        "scope_score": round(score, 1),
        "category": category,
        "label": label,
        "metrics": {k: m[k] for k in ["scene_count", "script_count", "total_nodes",
                                        "total_script_lines", "total_size_mb"]},
        "tip": {
            "micro": "Ideal para game jams e protótipos rápidos.",
            "pequeno": "Escopo adequado para um primeiro jogo indie.",
            "medio": "Projeto substancial — considere checkpoints frequentes.",
            "grande": "Projeto ambicioso — gerencie complexidade com git e backups.",
            "epico": "Projeto de escala comercial — planeje modularização.",
        }.get(category, ""),
    }


# ═══════════════════════════════════════════════════════════════════════
# 4.6 — search_codebase
# ═══════════════════════════════════════════════════════════════════════

def search_codebase(
    query: str,
    file_pattern: str = "*.gd",
    max_results: int = 20,
) -> dict:
    """Busca full-text nos arquivos do projeto.

    Args:
        query: Texto a buscar (case-insensitive).
        file_pattern: Glob pattern (ex: "*.gd", "*.tscn", "*").
        max_results: Máximo de resultados.

    Returns:
        {"status": "success", "matches": [...], "total_found": int}
    """
    proj = _get_active_project()
    matches = []
    total = 0

    for f in proj.glob(f"**/{file_pattern}"):
        if ".godot" in str(f) or ".mcp_backups" in str(f):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    total += 1
                    if len(matches) < max_results:
                        # Contexto: ±2 linhas
                        ctx_start = max(0, i - 2)
                        ctx_end = min(len(lines), i + 3)
                        ctx = []
                        for j in range(ctx_start, ctx_end):
                            prefix = ">>> " if j == i else "    "
                            ctx.append(f"{prefix}{j + 1}: {lines[j]}")
                        matches.append({
                            "file": str(f.relative_to(proj)),
                            "line": i + 1,
                            "context": "\n".join(ctx),
                        })
        except Exception:
            pass

    return {
        "status": "success",
        "query": query,
        "total_found": total,
        "shown": len(matches),
        "matches": matches,
        "note": f"Encontradas {total} ocorrências de '{query}' em arquivos {file_pattern}."
                if total > 0 else f"Nenhuma ocorrência de '{query}' encontrada.",
    }


# ═══════════════════════════════════════════════════════════════════════
# 4.7 — get_project_history
# ═══════════════════════════════════════════════════════════════════════

def get_project_history() -> dict:
    """Retorna o histórico de alterações do projeto (backups + git).

    Returns:
        {"status": "success", "backups": [...], "git_commits": [...]}
    """
    proj = _get_active_project()
    backups = []

    # ── Backups (.mcp_backups) ────────────────────────────────────
    backup_dir = proj / ".mcp_backups"
    if backup_dir.exists():
        index_file = backup_dir / "index.json"
        if index_file.exists():
            try:
                idx = json.loads(index_file.read_text(encoding="utf-8"))
                for entry in sorted(idx, key=lambda e: e.get("timestamp", ""), reverse=True)[:20]:
                    backups.append({
                        "backup_id": entry.get("backup_id", "?"),
                        "original": entry.get("original_path", "?"),
                        "timestamp": entry.get("timestamp", "?"),
                        "operation": entry.get("operation", "?"),
                    })
            except Exception:
                pass

    # ── Git log ───────────────────────────────────────────────────
    git_commits = []
    git_dir = proj / ".git"
    if git_dir.exists():
        import subprocess
        try:
            result = subprocess.run(
                ["git", "-C", str(proj), "log", "--oneline", "-20", "--format=%h|%s|%ai"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.strip().splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    git_commits.append({
                        "hash": parts[0], "message": parts[1], "date": parts[2],
                    })
        except Exception:
            pass

    return {
        "status": "success",
        "backup_count": len(backups),
        "git_commit_count": len(git_commits),
        "backups": backups,
        "git_commits": git_commits,
        "note": "Use restore_backup para desfazer alterações específicas."
                if backups else "Nenhum backup ou commit encontrado.",
    }
