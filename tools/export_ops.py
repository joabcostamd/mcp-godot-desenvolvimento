"""export_ops — Operações de exportação de projetos.

Fase 5: list_export_presets, validate_export_templates_installed, build_export.
"""

import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

from tools.classdb import get_godot_bin, get_config
from tools.project_ops import _get_active_project, _check_path_traversal


def list_export_presets() -> dict:
    """Lista os presets de exportação do projeto ativo.

    Returns:
        {"status": "success", "presets": [str]}
    """
    proj = _get_active_project()
    cfg_path = proj / "export_presets.cfg"

    if not cfg_path.exists():
        return {
            "status": "success",
            "presets": [],
            "note": "Nenhum preset de exportação encontrado. build_export criará um preset padrão para seu SO.",
        }

    content = cfg_path.read_text(encoding="utf-8")
    presets = []
    for line in content.splitlines():
        if line.strip().startswith("name="):
            presets.append(line.split("=", 1)[1].strip().strip('"'))

    return {"status": "success", "presets": presets}


def validate_export_templates_installed() -> dict:
    """Verifica se os templates de exportação do Godot estão instalados.

    Usa detecção multiplataforma: verifica diretórios padrão do Godot
    (Windows/Linux/macOS) e faz fallback com teste real de exportação headless.

    Returns:
        {"status": "success", "installed": True, "detail": str}
        ou {"status": "error", "installed": False, "message": str}
    """
    import platform
    import tempfile

    godot = get_godot_bin()
    installed = False
    detail = ""

    # ── Multiplataforma: detecta diretório de templates ──────────
    system = platform.system()
    if system == "Windows":
        templates_dirs = [
            Path.home() / "AppData" / "Roaming" / "Godot" / "export_templates",
            Path(os.environ.get("APPDATA", "")) / "Godot" / "export_templates",
        ]
    elif system == "Darwin":  # macOS
        templates_dirs = [
            Path.home() / "Library" / "Application Support" / "Godot" / "export_templates",
        ]
    else:  # Linux
        templates_dirs = [
            Path.home() / ".local" / "share" / "godot" / "export_templates",
            Path.home() / ".godot" / "export_templates",
        ]

    for td in templates_dirs:
        if td.exists():
            tpz_files = list(td.rglob("*.tpz"))
            if tpz_files:
                installed = True
                detail = f"{len(tpz_files)} template(s) em {td}"
                break
            # Verifica subdiretórios versionados
            for ver_dir in td.iterdir():
                if ver_dir.is_dir():
                    tpz = list(ver_dir.rglob("*.tpz"))
                    if tpz:
                        installed = True
                        detail = f"v{ver_dir.name}: {len(tpz)} arquivo(s)"
                        break
            if installed:
                break

    # ── Fallback: teste real de exportação headless ──────────────
    if not installed:
        proj = _get_active_project()
        if (proj / "project.godot").exists():
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                from tools.subprocess_utils import run_subprocess_safe
                result = run_subprocess_safe(
                    [godot, "--headless", "--path", str(proj),
                     "--export-release", "Web", tmp_path],
                    timeout=30,
                )
                output = result.stdout + result.stderr
                # Templates instalados = Godot tenta exportar (erro de preset OK)
                # Templates ausentes = erro específico mencionando templates
                if "template" in output.lower() and ("not found" in output.lower() or "not installed" in output.lower()):
                    detail = "Templates ausentes (confirmado via exportação headless)"
                elif "Error" not in output or "Preset" in output:
                    # Se o erro é sobre preset (não templates), templates estão OK
                    installed = True
                    detail = "Templates OK (exportação headless respondeu)"
                elif result.returncode == 0:
                    installed = True
                    detail = "Exportação headless bem-sucedida"
            except Exception as e:
                detail = f"Verificação inconclusiva: {e}"
            finally:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception:
                    pass
        else:
            # Sem projeto ativo, tenta --dump-extension-api como smoke test
            try:
                from tools.subprocess_utils import run_subprocess_safe
                result = run_subprocess_safe(
                    [godot, "--headless", "--dump-extension-api"],
                    timeout=10,
                )
                if result.returncode == 0:
                    detail = "Godot responde (sem projeto para teste de exportação)"
                else:
                    detail = f"Godot erro: {result.stderr[:100]}"
            except Exception:
                detail = "Godot indisponível para verificação"

    if installed:
        return {"status": "success", "installed": True, "detail": detail}

    return {
        "status": "error",
        "installed": False,
        "message": (
            "Templates de exportação não encontrados. Para instalar:\n"
            "1. Abra o Godot Editor\n"
            "2. Menu Editor → Manage Export Templates\n"
            "3. Clique 'Download and Install'\n"
            "4. Reinicie o Godot após a instalação"
        ),
        "detail": detail,
    }


def build_export(preset_name: str | None = None, output_path: str | None = None) -> dict:
    """Exporta o projeto para executável.

    Feature 9: Trava de exportação — exige release_checklist >= 6/10.
    Se a nota for insuficiente, retorna erro com os itens reprovados.

    Args:
        preset_name: Nome do preset (se None, cria preset padrão para o SO atual).
        output_path: Caminho do executável de saída.

    Returns:
        {"status": "success", "executable_path": str}
    """
    proj = _get_active_project()
    godot = get_godot_bin()

    # ── Feature 9: Trava de exportação ──────────────────────────
    from tools.deploy_ops import release_checklist

    checklist = release_checklist()
    score_str = checklist.get("score", "0/10")
    try:
        score_num = int(score_str.split("/")[0])
    except (ValueError, IndexError):
        score_num = 0

    MIN_SCORE = 7
    if score_num < MIN_SCORE:
        failed = [c for c in checklist.get("checks", []) if c.get("status") in ("fail", "warn")]
        failed_items = "; ".join(
            f"{c['check']}={c.get('status', '?')}" for c in failed
        )
        return {
            "status": "error",
            "message": (
                f"Exportação bloqueada: release_checklist retornou {score_str} "
                f"(mínimo: {MIN_SCORE}/10). Itens pendentes: {failed_items or 'nenhum listado'}. "
                f"Corrija os problemas e tente novamente, ou use release_checklist() "
                f"para ver o relatório completo."
            ),
            "checklist_score": score_str,
            "minimum_required": f"{MIN_SCORE}/10",
            "failed_checks": failed,
        }

    # ── Validação de segurança ──────────────────────────────────
    if output_path:
        violation = _check_path_traversal(output_path, proj)
        if violation:
            return violation
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("export", 300)

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": "Projeto não encontrado."}

    # Verifica templates
    tmpl_check = validate_export_templates_installed()
    if tmpl_check.get("installed") is False:
        return tmpl_check

    # Se não tem preset, cria um padrão
    cfg_path = proj / "export_presets.cfg"
    if not cfg_path.exists() or not preset_name:
        import platform
        system = platform.system()
        if system == "Windows":
            preset_name = "Windows Desktop"
            preset_content = _generate_windows_preset(proj)
        elif system == "Darwin":
            preset_name = "macOS"
            preset_content = _generate_macos_preset(proj)
        else:
            preset_name = "Linux/X11"
            preset_content = _generate_linux_preset(proj)

        cfg_path.write_text(preset_content, encoding="utf-8")

    # Define output path
    if not output_path:
        build_dir = proj / "build"
        build_dir.mkdir(exist_ok=True)
        import platform
        ext = ".exe" if platform.system() == "Windows" else ""
        output_path = str(build_dir / (proj.name + ext))

    try:
        from tools.subprocess_utils import run_subprocess_safe
        result = run_subprocess_safe(
            [godot, "--headless", "--export-release", preset_name, output_path, "--path", str(proj)],
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Exportação falhou. Output: {output[-500:]}",
            }
        return {"status": "success", "executable_path": output_path}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Timeout — exportação excedeu 5 minutos."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao exportar: {e}"}


# ── Presets padrão ──────────────────────────────────────────────────

def _generate_windows_preset(proj: Path) -> str:
    name = proj.name
    return f"""[preset.0]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/{name}.exe"
patched=true
embed_pck=false
packing_format="zip"

[preset.0.options]

custom_template/debug=""
custom_template/release=""
binary_format/embed_pck=false
application/icon=""
application/console_use_system_dock=false
application/console_dpi_allow_hi-res=false
application/console_dpi_override=0
application/file_version="1.0.0"
application/product_version="1.0.0"
application/company_name=""
application/product_name="{name}"
application/file_description=""
application/copyright=""
application/trademarks=""
codesign/enable=false
codesign/identity_type=0
codesign/identity=""
codesign/password=""
codesign/timestamp=true
codesign/timestamp_server_url=""
codesign/digest_algorithm=0
codesign/description=""
codesign/custom_options=PackedStringArray()
application/modify_resources=true
application/icon_interpolation=0
ssh_remote_deploy/enabled=false
ssh_remote_deploy/host=""
ssh_remote_deploy/port=""
ssh_remote_deploy/extra_args_scp=""
ssh_remote_deploy/extra_args_ssh=""
ssh_remote_deploy/run_script=""
ssh_remote_deploy/cleanup_script=""
"""


def _generate_macos_preset(proj: Path) -> str:
    name = proj.name
    return f"""[preset.0]

name="macOS"
platform="macOS"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/{name}.zip"
patched=true

[preset.0.options]

custom_template/debug=""
custom_template/release=""
application/name="{name}"
application/bundle_identifier="com.godot.{name.lower()}"
application/signature=""
application/short_version="1.0"
application/version="1.0"
application/copyright=""
application/icon=""
"""


def _generate_linux_preset(proj: Path) -> str:
    name = proj.name
    return f"""[preset.0]

name="Linux/X11"
platform="Linux/X11"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/{name}.x86_64"
patched=true

[preset.0.options]

custom_template/debug=""
custom_template/release=""
binary_format/architecture="x86_64"
binary_format/embed_pck=false
texture_format/s3tc=true
texture_format/etc=true
texture_format/etc2=true
"""

