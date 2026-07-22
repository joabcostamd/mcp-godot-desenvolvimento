"""domains/export/handlers.py — F5.21."""
def list_export_presets(*, project_path: str | None = None) -> dict:
    from tools.export_ops import list_export_presets as _impl; return _impl(project_path)
def validate_export_templates(*, project_path: str | None = None) -> dict:
    from tools.export_ops import validate_export_templates_installed as _impl; return _impl(project_path)
def build_export(*, preset: str = "HTML5", project_path: str | None = None) -> dict:
    from tools.export_ops import build_export as _impl; return _impl(preset=preset, project_path=project_path)
__all__ = ["list_export_presets", "validate_export_templates", "build_export"]
