"""project_state.py — Estado compartilhado do projeto (Onda 7).

Singleton que mantem snapshot em memoria do projeto ativo.
Atualizado automaticamente por hooks nos write handlers.
"""

import re as _re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ProjectState:
    """Singleton — estado compartilhado do projeto ativo."""

    def __init__(self):
        self.scenes: dict = {}
        self.scripts: dict = {}
        self.sprites: dict = {}
        self.audio: dict = {}
        self.last_scan: float = 0.0
        self.project_root: Path | None = None

    def scan(self, project_root: Path):
        self.project_root = project_root
        self.last_scan = time.time()

        self.scenes = {}
        for tscn in project_root.rglob("*.tscn"):
            if '.godot' in str(tscn) or 'builds' in str(tscn):
                continue
            rel = str(tscn.relative_to(project_root)).replace('\\', '/')
            self.scenes[rel] = self._parse_scene(tscn)

        self.scripts = {}
        for gd in project_root.rglob("*.gd"):
            if '.godot' in str(gd) or 'addons' in str(gd):
                continue
            rel = str(gd.relative_to(project_root)).replace('\\', '/')
            self.scripts[rel] = self._parse_script(gd)

        self.sprites = {}
        for png in project_root.rglob("*.png"):
            if '.godot' in str(png) or 'builds' in str(png):
                continue
            rel = str(png.relative_to(project_root)).replace('\\', '/')
            self.sprites[rel] = self._analyze_sprite(png)

        self.audio = {}
        for ext in ['*.wav', '*.mp3', '*.ogg']:
            for af in project_root.rglob(ext):
                if '.godot' in str(af) or 'builds' in str(af):
                    continue
                rel = str(af.relative_to(project_root)).replace('\\', '/')
                self.audio[rel] = self._analyze_audio(af)

    def _parse_scene(self, path: Path) -> dict:
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {"nodes": [], "error": "cannot_read"}
        nodes = []
        for line in content.split('\n'):
            if '[node name=' in line:
                nm = _re.search(r'name="([^"]+)"', line)
                tm = _re.search(r'type="([^"]+)"', line)
                if nm:
                    nodes.append({"name": nm.group(1), "type": tm.group(1) if tm else "Node"})
        return {"nodes": nodes, "total_nodes": len(nodes)}

    def _parse_script(self, path: Path) -> dict:
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {"extends": "unknown", "methods": []}
        extends = "Node"
        methods = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('extends '):
                extends = line.replace('extends ', '').strip()
            elif line.startswith('func '):
                m = _re.match(r'func\s+(\w+)', line)
                if m: methods.append(m.group(1))
        return {"extends": extends, "methods": methods}

    def _analyze_sprite(self, path: Path) -> dict:
        return {"size_bytes": path.stat().st_size, "category": self._guess_sprite_category(path)}

    def _guess_sprite_category(self, path: Path) -> str:
        n = path.stem.lower()
        if any(w in n for w in ['player','jogador','hero']): return "personagem"
        if any(w in n for w in ['enemy','inimigo','boss']): return "inimigo"
        if any(w in n for w in ['tower','torre','turret']): return "torre"
        if any(w in n for w in ['bullet','projetil','laser']): return "projetil"
        if any(w in n for w in ['background','bg','fundo','sky']): return "fundo"
        if any(w in n for w in ['tile','chao','wall']): return "tile"
        if any(w in n for w in ['ui','button','hud','icon']): return "ui"
        return "outro"

    def _analyze_audio(self, path: Path) -> dict:
        return {"size_bytes": path.stat().st_size, "format": path.suffix.replace('.', '')}

    def has_sprite_for(self, entity_name: str) -> bool:
        n = entity_name.lower()
        return any(n in p.lower() for p in self.sprites)

    def has_audio_for(self, action: str) -> bool:
        a = action.lower()
        return any(a in p.lower() for p in self.audio)

    def missing_assets(self, entity_name: str) -> dict:
        return {"needs_sprite": not self.has_sprite_for(entity_name),
                "needs_audio": not self.has_audio_for(entity_name),
                "needs_script": entity_name.lower() not in str(self.scripts).lower()}

    def get_stage(self) -> str:
        sc = len(self.scenes)
        sr = len(self.scripts)
        sp = len(self.sprites)
        if sc <= 1 and sr <= 2: return "vazio"
        if sp < 5 and sr > 3: return "prototipo"
        if sr > 5 and sp > 3: return "desenvolvimento"
        if sp > 10: return "polimento"
        return "desenvolvimento"

    def summary(self) -> dict:
        return {"scenes": len(self.scenes), "scripts": len(self.scripts),
                "sprites": len(self.sprites), "audio_files": len(self.audio),
                "stage": self.get_stage(), "last_scan": self.last_scan}


_state = ProjectState()

def get_state() -> ProjectState:
    return _state

def refresh_state(project_root: Path | None = None):
    if project_root is None:
        from tools.project_ops import _get_active_project
        project_root = _get_active_project()
    _state.scan(project_root)

def on_file_written(file_path: str):
    """Hook chamado apos escrever qualquer arquivo."""
    from tools.project_ops import _get_active_project
    proj = _get_active_project()
    full = Path(file_path) if Path(file_path).is_absolute() else proj / file_path
    if not full.exists(): return
    rel = str(full.relative_to(proj)).replace('\\', '/')
    if rel.endswith('.tscn'): _state.scenes[rel] = _state._parse_scene(full)
    elif rel.endswith('.gd'): _state.scripts[rel] = _state._parse_script(full)
    elif rel.endswith('.png'): _state.sprites[rel] = _state._analyze_sprite(full)
    elif any(rel.endswith(e) for e in ['.wav','.mp3','.ogg']): _state.audio[rel] = _state._analyze_audio(full)
