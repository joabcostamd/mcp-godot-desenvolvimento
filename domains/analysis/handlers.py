"""domains/analysis/handlers.py — F5.25."""
def analyze_game_structure(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import analyze_game_structure as _impl; return _impl(project_path)
def suggest_next_steps(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import suggest_next_steps as _impl; return _impl(project_path)
def find_missing_references(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import find_missing_references as _impl; return _impl(project_path)
def validate_game_design(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import validate_game_design as _impl; return _impl(project_path)
def estimate_game_scope(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import estimate_game_scope as _impl; return _impl(project_path)
def search_codebase(*, query: str = "", project_path: str | None = None) -> dict:
    from tools.analyze_ops import search_codebase as _impl; return _impl(query=query, project_path=project_path)
def get_project_history(*, project_path: str | None = None) -> dict:
    from tools.analyze_ops import get_project_history as _impl; return _impl(project_path)
__all__ = ["analyze_game_structure", "suggest_next_steps", "find_missing_references", "validate_game_design", "estimate_game_scope", "search_codebase", "get_project_history"]
