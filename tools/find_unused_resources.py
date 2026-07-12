"""find_unused_resources — Detecção de recursos não usados (órfãos) no projeto.

Reaproveita o motor de busca de find_usages/validate_project_refs para
identificar assets que existem no projeto mas não são referenciados por
nenhum .tscn, .gd ou .tres.

Feature: Grupo C — Detecção de recursos não usados.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Extensões de asset escaneadas por padrão
_ASSET_EXTENSIONS = {
    "image":    {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".svg", ".tga"},
    "audio":    {".wav", ".mp3", ".ogg", ".flac", ".aac"},
    "model":    {".glb", ".gltf", ".obj", ".fbx", ".dae", ".blend"},
    "resource": {".tres", ".tscn", ".gdshader", ".tres", ".material"},
    "font":     {".ttf", ".otf", ".woff", ".woff2"},
}

_REFERENCE_SCAN_EXTENSIONS = {".tscn", ".gd", ".tres"}


def find_unused_resources(
    project_path: str | None = None,
    asset_types: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    min_size_bytes: int = 0,
) -> dict:
    """Encontra recursos (assets) que existem no projeto mas não são
    referenciados por nenhum .tscn, .gd ou .tres.

    Args:
        project_path: Caminho do projeto. Se None, usa o projeto ativo.
        asset_types: Tipos de asset a verificar (default: todos).
                     Opções: "image", "audio", "model", "resource", "font".
        exclude_paths: Caminhos a excluir da varredura (ex: ["addons/", ".godot/"]).
        min_size_bytes: Tamanho mínimo em bytes para considerar (default: 0).

    Returns:
        dict com lista de órfãos, total de assets escaneados, economia estimada.
    """

    proj = _resolve_project(project_path)
    if isinstance(proj, dict) and proj.get("status") == "error":
        return proj

    if asset_types is None:
        asset_types = list(_ASSET_EXTENSIONS.keys())

    # Valida asset_types
    for at in asset_types:
        if at not in _ASSET_EXTENSIONS:
            return {
                "status": "error",
                "message": f"asset_type inválido: '{at}'. Use: {sorted(_ASSET_EXTENSIONS.keys())}.",
            }

    if exclude_paths is None:
        exclude_paths = ["addons/", ".godot/", ".git/", "_backups/", "build/", ".mcp_"]

    # ═══ 1. Coletar TODOS os assets ═══
    extensions: set[str] = set()
    for at in asset_types:
        extensions.update(_ASSET_EXTENSIONS[at])

    all_assets: list[dict] = []
    for ext in sorted(extensions):
        for f in proj.rglob(f"*{ext}"):
            if _should_skip(f, exclude_paths):
                continue
            try:
                size = f.stat().st_size
            except OSError:
                size = 0
            if size < min_size_bytes:
                continue
            rel = str(f.relative_to(proj)).replace("\\", "/")
            all_assets.append({
                "path": f"res://{rel}",
                "size_bytes": size,
                "extension": ext,
                "type": _classify_asset(ext),
            })

    if not all_assets:
        return {
            "status": "success",
            "orphans": [],
            "total_scanned": 0,
            "total_size_bytes": 0,
            "message": "Nenhum asset encontrado no projeto.",
        }

    # ═══ 2. Construir índice de referências ═══
    referenced: set[str] = set()

    for ref_ext in _REFERENCE_SCAN_EXTENSIONS:
        for ref_file in proj.rglob(f"*{ref_ext}"):
            if _should_skip(ref_file, exclude_paths):
                continue
            try:
                content = ref_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Busca padrões de referência
            referenced.update(_extract_refs_from_content(content))

    # Adiciona referências implícitas: main_scene + autoloads
    try:
        godot_cfg = (proj / "project.godot").read_text(encoding="utf-8")
        import re
        main_match = re.search(r'run/main_scene\s*=\s*"(.+?)"', godot_cfg)
        if main_match:
            referenced.add(main_match.group(1).replace("res://", ""))
        # Autoloads: Nome="*res://caminho/script.gd"
        for m in re.finditer(r'^\s*(\w+)\s*=\s*"\*?res://([^"]+)"', godot_cfg, re.MULTILINE):
            autoload_path = m.group(2)
            referenced.add(autoload_path)
    except Exception:
        pass

    # ═══ 3. Filtrar órfãos ═══
    # Normaliza referências para comparação exata de path
    normalized_refs: set[str] = set()
    for ref in referenced:
        normalized_refs.add(ref.replace("\\", "/").lower())

    orphans: list[dict] = []
    total_orphan_size = 0

    for asset in all_assets:
        asset_rel = asset["path"].replace("res://", "").replace("\\", "/").lower()
        is_referenced = asset_rel in normalized_refs

        if not is_referenced:
            orphans.append(asset)
            total_orphan_size += asset["size_bytes"]

    return {
        "status": "success",
        "orphans": orphans,
        "total_scanned": len(all_assets),
        "total_orphans": len(orphans),
        "total_size_bytes": total_orphan_size,
        "total_size_mb": round(total_orphan_size / (1024 * 1024), 2),
        "message": (
            f"{len(orphans)} de {len(all_assets)} assets são órfãos "
            f"({round(total_orphan_size / (1024 * 1024), 2)} MB não referenciados)."
        ),
    }


def _resolve_project(project_path: str | None = None) -> Path:
    """Resolve o caminho do projeto."""
    if project_path:
        p = Path(project_path)
        if p.exists():
            return p
        return {"status": "error", "message": f"Projeto não encontrado: {project_path}"}
    try:
        from tools.project_ops import _get_active_project
        return Path(_get_active_project())
    except Exception:
        return {"status": "error", "message": "Nenhum projeto ativo definido."}


def _should_skip(path: Path, exclude_paths: list[str]) -> bool:
    """Verifica se o path deve ser ignorado."""
    path_str = str(path).replace("\\", "/")
    for excl in exclude_paths:
        if excl in path_str:
            return True
    return False


def _classify_asset(ext: str) -> str:
    """Classifica um asset pelo tipo de extensão."""
    for at, exts in _ASSET_EXTENSIONS.items():
        if ext in exts:
            return at
    return "unknown"


def _extract_refs_from_content(content: str) -> set[str]:
    """Extrai todas as referências a arquivos de um conteúdo de texto (.tscn, .gd, .tres)."""
    import re
    refs: set[str] = set()

    # Padrões comuns de referência no Godot:
    # - res://path/to/file.ext
    # - ExtResource("N") → mapeado depois
    # - preload("res://...")
    # - load("res://...")
    # - ResourceLoader.load("res://...")
    # - script = ExtResource("N") ou script = "res://..."
    # - scene = "res://..."
    # - texture = "res://..."
    # - mesh = "res://..."
    # - [ext_resource path="res://..." type="..." id=...]

    # Captura ext_resource path
    for m in re.finditer(r'path\s*=\s*"res://([^"]+)"', content):
        refs.add(m.group(1))

    # Captura res:// direto
    for m in re.finditer(r'"(res://[^"]+)"', content):
        refs.add(m.group(1).replace("res://", ""))

    # Captura preload/load
    for m in re.finditer(r'(?:preload|load)\s*\(\s*"res://([^"]+)"\s*\)', content):
        refs.add(m.group(1))

    # Captura scene =/script =/texture =/mesh =/icon =
    for prop in ["scene", "script", "texture", "mesh", "icon", "font", "audio"]:
        for m in re.finditer(rf'{prop}\s*=\s*"res://([^"]+)"', content):
            refs.add(m.group(1))

    # Captura change_scene_to_file
    for m in re.finditer(r'change_scene_to_file\s*\(\s*"res://([^"]+)"\s*\)', content):
        refs.add(m.group(1))

    return refs
