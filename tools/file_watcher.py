"""file_watcher.py — Monitora arquivos do projeto e dispara hot reload.

GAP #2 — Hot Reload Automático:
Usa polling (os.stat().st_mtime) para detectar mudanças em scripts,
cenas e assets. Quando um arquivo muda, envia reload_resource ao
game bridge via bridge.py.

Sem dependências externas — usa apenas stdlib (os, pathlib, time, threading).
"""

import os
import threading
import time
from pathlib import Path


class FileWatcher:
    """Monitora diretórios por mudanças em arquivos via polling.

    Uso:
        watcher = FileWatcher(project_root)
        watcher.watch("scripts/", "*.gd")
        watcher.watch("scenes/", "*.tscn")
        watcher.on_change = lambda path: bridge.reload_resource(path)
        watcher.start()
        ...
        watcher.stop()
    """

    def __init__(self, project_root: Path, poll_interval: float = 1.0):
        self._root = Path(project_root)
        self._interval = poll_interval
        self._watched: dict[str, str] = {}  # dir -> glob pattern
        self._mtimes: dict[str, float] = {}  # abs_path -> mtime
        self._running = False
        self._thread: threading.Thread | None = None
        self.on_change = None  # callable(path: str)

    def watch(self, directory: str, pattern: str = "*") -> None:
        """Adiciona um diretório para monitorar.

        Args:
            directory: Caminho relativo ao project_root.
            pattern: Glob pattern (ex: "*.gd", "*.tscn", "*").
        """
        self._watched[str(directory).rstrip("/\\")] = pattern

    def _scan(self) -> list[str]:
        """Escaneia diretórios monitorados e retorna paths que mudaram."""
        changed = []
        for rel_dir, pattern in self._watched.items():
            full_dir = self._root / rel_dir
            if not full_dir.exists():
                continue
            for file_path in full_dir.rglob(pattern):
                if file_path.is_file():
                    abs_path = str(file_path.absolute())
                    try:
                        mtime = os.stat(abs_path).st_mtime
                    except OSError:
                        continue
                    old = self._mtimes.get(abs_path)
                    if old is not None and mtime > old + 0.1:
                        rel_path = str(file_path.relative_to(self._root)).replace("\\", "/")
                        changed.append(rel_path)
                    self._mtimes[abs_path] = mtime
        return changed

    def _poll_loop(self) -> None:
        """Loop de polling em thread separada."""
        # Primeiro scan: só registra mtimes, não dispara eventos
        self._scan()
        while self._running:
            time.sleep(self._interval)
            if not self._running:
                break
            try:
                changed = self._scan()
                for path in changed:
                    if self.on_change:
                        self.on_change(path)
            except Exception:
                pass  # Best-effort

    def start(self) -> None:
        """Inicia o monitoramento em thread separada."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Para o monitoramento."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None


# ── Singleton global ──────────────────────────────────────────────────

_watcher: FileWatcher | None = None


def start_watching(project_root: Path, poll_interval: float = 1.0) -> dict:
    """Inicia o watcher global de arquivos.

    Monitora scripts/ (.gd), scenes/ (.tscn), assets/ (*) por padrão.

    Args:
        project_root: Raiz do projeto Godot.
        poll_interval: Intervalo de polling em segundos (default 1s).

    Returns:
        {"status": "success", "watching": [str]}
    """
    global _watcher
    if _watcher and _watcher._running:
        return {"status": "success", "watching": list(_watcher._watched.keys()),
                "note": "Watcher já está rodando."}

    _watcher = FileWatcher(project_root, poll_interval)
    _watcher.watch("scripts", "*.gd")
    _watcher.watch("scenes", "*.tscn")
    _watcher.watch("assets", "*")
    _watcher.watch("addons", "*.gd")

    def _on_file_change(rel_path: str):
        """Callback: arquivo mudou → hot reload no jogo."""
        try:
            from tools.bridge import is_game_connected, reload_resource
            if is_game_connected():
                reload_resource(rel_path)
        except Exception:
            pass

    _watcher.on_change = _on_file_change
    _watcher.start()

    return {"status": "success", "watching": list(_watcher._watched.keys()),
            "poll_interval_sec": poll_interval}


def stop_watching() -> dict:
    """Para o watcher global."""
    global _watcher
    if _watcher:
        _watcher.stop()
        _watcher = None
        return {"status": "success", "stopped": True}
    return {"status": "success", "stopped": False, "note": "Watcher não estava rodando."}


def is_watching() -> bool:
    """Verifica se o watcher está ativo."""
    return _watcher is not None and _watcher._running


def watch_directory(directory: str, pattern: str = "*") -> dict:
    """Adiciona um diretório extra ao watcher existente."""
    global _watcher
    if not _watcher:
        return {"status": "error", "message": "Watcher não iniciado. Use start_watching primeiro."}
    _watcher.watch(directory, pattern)
    return {"status": "success", "watching": directory, "pattern": pattern}
