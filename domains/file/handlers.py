"""domains/file/handlers.py"""
def delete_file(*, file_path: str) -> dict:
    from tools.file_ops import delete_file as _impl; return _impl(file_path)
def move_file(*, source_path: str, dest_path: str) -> dict:
    from tools.file_ops import move_file as _impl; return _impl(source_path, dest_path)
def inspect_project(*, project_path: str | None = None) -> dict:
    from tools.file_ops import inspect_project as _impl; return _impl(project_path)
__all__ = ["delete_file", "move_file", "inspect_project"]
