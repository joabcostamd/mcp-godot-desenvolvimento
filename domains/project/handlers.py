"""domains/project/handlers.py"""
def create_project(*, project_name: str, project_path: str | None = None, template: str = "2D") -> dict:
    from tools.project_ops import create_project as _impl; return _impl(project_name, project_path, template)
def set_active_project(*, project_path: str) -> dict:
    from tools.project_ops import set_active_project as _impl; return _impl(project_path)
def get_project_settings(*, project_path: str | None = None) -> dict:
    from tools.project_ops import get_project_settings as _impl; return _impl(project_path)
def set_project_setting(*, key: str, value: str, project_path: str | None = None) -> dict:
    from tools.project_ops import set_project_setting as _impl; return _impl(key, value, project_path)
def set_main_scene(*, scene_path: str, project_path: str | None = None) -> dict:
    from tools.project_ops import set_main_scene as _impl; return _impl(scene_path, project_path)
__all__ = ["create_project", "set_active_project", "get_project_settings", "set_project_setting", "set_main_scene"]
