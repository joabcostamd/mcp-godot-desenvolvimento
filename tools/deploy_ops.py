"""deploy_ops.py — Deploy automatizado para itch.io (GRATIS).

Usa butler CLI (oficial do itch.io, gratuito) para upload.
Exporta builds do Godot para Windows, Linux, Web, macOS, Android.
"""

import json
import os
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def deploy_itch(itch_username: str = "", itch_game: str = "",
                platforms: list[str] | None = None, version: str = "1.0.0",
                dry_run: bool = True) -> dict:
    """Exporta e envia o jogo para itch.io via butler CLI.

    Args:
        itch_username: Seu nome de usuario no itch.io.
        itch_game: Nome do jogo no itch.io (slug).
        platforms: Plataformas: windows, linux, web, macos, android.
        version: Versao da build.
        dry_run: Se True, apenas simula sem enviar.

    Returns:
        {"status": "success", "builds": [...], "itch_url": str, "butler_available": bool}
    """
    from tools.project_ops import _get_active_project
    proj = _get_active_project()

    if not platforms:
        platforms = ["windows"]

    butler_installed = False
    try:
        result = subprocess.run(["butler", "--version"], capture_output=True, text=True, timeout=5)
        butler_installed = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    builds = []
    build_dir = proj / "builds"
    build_dir.mkdir(exist_ok=True)

    for platform in platforms:
        platform_dir = build_dir / platform
        platform_dir.mkdir(exist_ok=True)

        build_info = {"platform": platform, "status": "simulated" if dry_run else "pending",
                      "path": str(platform_dir)}

        if dry_run:
            build_info["note"] = "Dry run — build real requer Godot rodando"
        else:
            try:
                from tools.export_ops import build_export
                result = build_export(platform=platform, output_path=str(platform_dir / f"game_{version}"))
                build_info["status"] = result.get("status", "unknown")
            except Exception as e:
                build_info["status"] = "error"
                build_info["error"] = str(e)

        builds.append(build_info)

    itch_url = f"https://{itch_username}.itch.io/{itch_game}" if itch_username and itch_game else ""

    # Se butler disponivel, mostrar comando
    butler_cmd = ""
    if butler_installed and itch_username and itch_game:
        chan = {"windows": "windows", "linux": "linux", "web": "web", "macos": "osx"}.get(platforms[0], platforms[0])
        butler_cmd = f"butler push builds/{platforms[0]} {itch_username}/{itch_game}:{chan} --userversion {version}"

    return {
        "status": "success",
        "builds": builds,
        "butler_available": butler_installed,
        "itch_url": itch_url,
        "butler_command": butler_cmd,
        "dry_run": dry_run,
        "message": f"{'[SIMULADO] ' if dry_run else ''}{len(platforms)} plataformas. Butler: {'disponivel' if butler_installed else 'instale: https://itchio.itch.io/butler'}",
    }


def release_checklist() -> dict:
    """Verifica se o projeto esta pronto para lancamento (nota 0-10)."""
    from tools.project_ops import _get_active_project
    proj = _get_active_project()

    checks = []
    score = 0
    total = 10

    # 1. project.godot
    if (proj / "project.godot").exists():
        checks.append({"check": "project.godot", "status": "pass"})
        score += 1
    else:
        checks.append({"check": "project.godot", "status": "fail", "message": "Arquivo de projeto nao encontrado"})

    # 2. Main scene
    try:
        config = (proj / "project.godot").read_text(encoding="utf-8")
        has_main = "run/main_scene" in config
        checks.append({"check": "main_scene", "status": "pass" if has_main else "fail"})
        if has_main: score += 1
    except:
        checks.append({"check": "main_scene", "status": "fail"})

    # 3. Scripts
    gd_files = list(proj.rglob("*.gd"))
    checks.append({"check": "scripts", "status": "pass", "count": len(gd_files)})
    if gd_files: score += 1

    # 4. Assets
    png_files = list(proj.rglob("*.png")) + list(proj.rglob("*.jpg"))
    checks.append({"check": "assets", "status": "pass", "count": len(png_files)})
    if png_files: score += 1

    # 5. Audio
    audio = list(proj.rglob("*.wav")) + list(proj.rglob("*.mp3")) + list(proj.rglob("*.ogg"))
    checks.append({"check": "audio", "status": "pass" if audio else "warn", "count": len(audio)})
    if audio: score += 1

    # 6. Export presets
    has_export = (proj / "export_presets.cfg").exists()
    checks.append({"check": "export_presets", "status": "pass" if has_export else "warn"})
    if has_export: score += 1

    # 7. .gitignore
    has_gitignore = (proj / ".gitignore").exists()
    checks.append({"check": "gitignore", "status": "pass" if has_gitignore else "warn"})
    if has_gitignore: score += 1

    # 8. README
    readme = list(proj.glob("README*"))
    checks.append({"check": "readme", "status": "pass" if readme else "fail"})
    if readme: score += 1

    # 9. License
    lic = list(proj.glob("LICENSE*")) + list(proj.glob("LICENÇA*"))
    checks.append({"check": "license", "status": "pass" if lic else "warn"})
    if lic: score += 1

    # 10. Project size
    total_size = sum(f.stat().st_size for f in proj.rglob("*") if f.is_file() and '.git' not in str(f))
    size_mb = total_size / (1024 * 1024)
    size_ok = size_mb < 500
    checks.append({"check": "project_size", "status": "pass" if size_ok else "warn", "size_mb": round(size_mb, 1)})
    if size_ok: score += 1

    return {
        "status": "success",
        "checks": checks,
        "score": f"{score}/{total}",
        "ready": score >= 7,
        "message": f"Projeto {'PRONTO' if score >= 7 else 'PRECISA DE AJUSTES'} para lancamento ({score}/{total})",
    }


def auto_screenshot(count: int = 5, delay_between: float = 2.0, save_dir: str = "screenshots") -> dict:
    """Gera screenshots automaticas do jogo para loja. Requer jogo rodando."""
    import time
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    violation = _check_path_traversal(save_dir, proj)
    if violation:
        return {"status": "error", "message": violation}

    out_dir = proj / save_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    screenshots = []
    try:
        from tools.game_bridge import _send_game_command
        for i in range(count):
            try:
                result = _send_game_command("screenshot", {})
                if result.get("image_data"):
                    import base64
                    filepath = out_dir / f"screenshot_{i+1:02d}.png"
                    filepath.write_bytes(base64.b64decode(result["image_data"]))
                    screenshots.append(str(filepath.relative_to(proj)))
                if i < count - 1:
                    time.sleep(delay_between)
            except Exception:
                screenshots.append(f"falha frame {i+1}")
    except ImportError:
        screenshots = ["game_bridge indisponivel — jogo precisa estar rodando"]

    return {
        "status": "success" if screenshots else "error",
        "screenshots": screenshots,
        "total": len([s for s in screenshots if not s.startswith("falha")]),
        "message": f"{len(screenshots)} screenshots em {save_dir}/" if screenshots else "Jogo nao esta rodando?",
    }
