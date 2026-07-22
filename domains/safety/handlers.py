"""domains/safety/handlers.py — F5.24."""
def list_backups() -> dict:
    from tools.safety import list_backups as _impl; return _impl()
def restore_backup(*, backup_id: str = "") -> dict:
    from tools.safety import restore as _impl; return _impl(backup_id)
def git_checkpoint(*, message: str = "checkpoint") -> dict:
    from tools.safety import git_checkpoint as _impl; return _impl(message)
def undo_last_action() -> dict:
    from tools.safety import undo_last_action as _impl; return _impl()
def get_undo_history() -> dict:
    from tools.safety import get_undo_history as _impl; return _impl()
__all__ = ["list_backups", "restore_backup", "git_checkpoint", "undo_last_action", "get_undo_history"]
