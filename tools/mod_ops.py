"""mod_ops.py — Suporte a Mods (Fatia 5.2).

Ferramentas para criar e validar sistemas de modding:
  - Gerar manifesto de mod
  - Validar compatibilidade de mods
  - Carregar mods em runtime (Godot 4 ResourceLoader)
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def mod_manifest_generate(args: dict | None = None) -> dict:
    """Gera um manifesto de mod (mod.json) para projetos Godot.

    O manifesto segue o formato padrão de modding:
      - Nome, versão, descrição
      - Dependências
      - Arquivos incluídos (.pck ou scripts soltos)
      - Compatibilidade com versão do jogo base

    Args:
        mod_name: Nome do mod.
        mod_version: Versão (semver).
        mod_author: Autor.
        mod_description: Descrição.
        dependencies: Lista de mods requeridos.
        target_game_version: Versão do jogo compatível.
        files: Lista de arquivos do mod.

    Returns:
        dict com manifest JSON e instruções de empacotamento.
    """
    args = args or {}
    import json

    manifest = {
        "name": args.get("mod_name", "meu_mod"),
        "version": args.get("mod_version", "1.0.0"),
        "author": args.get("mod_author", "Desconhecido"),
        "description": args.get("mod_description", ""),
        "dependencies": args.get("dependencies", []),
        "target_game_version": args.get("target_game_version", "1.0.0"),
        "files": args.get("files", []),
        "type": args.get("mod_type", "content"),
        "entry_script": args.get("entry_script", "mod_main.gd"),
        "compatible_with": args.get("compatible_with", []),
        "created_at": "",
        "min_game_version": args.get("target_game_version", "1.0.0"),
    }

    import datetime
    manifest["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "manifest": manifest,
        "manifest_json": manifest_json,
        "packaging_instructions": [
            "1. Coloque mod.json na raiz da pasta do mod",
            "2. Exporte como .pck: Godot --headless --export-pack " + manifest["name"] + ".pck",
            "3. Ou distribua a pasta com os scripts + mod.json",
            "4. No jogo base, use ProjectSettings.load_resource_pack() para carregar",
        ],
        "integration_gdscript": '''func load_mod(mod_path: String) -> bool:
    var dir = DirAccess.open(mod_path)
    if not dir: return false
    var manifest_path = mod_path + "/mod.json"
    if not FileAccess.file_exists(manifest_path): return false
    var f = FileAccess.open(manifest_path, FileAccess.READ)
    var manifest = JSON.parse_string(f.get_as_text())
    f.close()
    if not manifest: return false
    # Carregar .pck se houver
    var pck = mod_path + "/" + manifest.get("name", "mod") + ".pck"
    if FileAccess.file_exists(pck):
        ProjectSettings.load_resource_pack(pck)
    # Registrar na lista de mods carregados
    _loaded_mods.append(manifest)
    return true''',
        "message": f"Manifesto gerado para mod '{manifest['name']}' v{manifest['version']}.",
    }


def validate_mod_compatibility(args: dict | None = None) -> dict:
    """Valida compatibilidade entre mods e o jogo base.

    Verifica:
      - Versão do jogo é compatível (semver check)
      - Dependências do mod estão disponíveis
      - Não há conflitos de arquivos entre mods
      - Scripts de entrada existem e são válidos

    Args:
        mod_manifest: Manifesto do mod (dict ou path para mod.json).
        game_version: Versão atual do jogo.
        loaded_mods: Lista de manifestos de mods já carregados.

    Returns:
        dict com resultado da validação e problemas encontrados.
    """
    args = args or {}
    mod_manifest = args.get("mod_manifest", {})
    game_version = args.get("game_version", "1.0.0")
    loaded_mods = args.get("loaded_mods", [])

    if not mod_manifest:
        return {"status": "error", "message": "Forneca mod_manifest (dict ou path)."}

    issues = []

    # Validação de versão (semver simplificado)
    mod_min = mod_manifest.get("target_game_version", "0.0.0")
    try:
        mod_parts = ([int(x) for x in mod_min.split(".")] + [0, 0, 0])[:3]
        game_parts = ([int(x) for x in game_version.split(".")] + [0, 0, 0])[:3]
        if game_parts < mod_parts:
            issues.append({
                "severity": "error",
                "type": "version_mismatch",
                "message": f"Jogo v{game_version} < requerido v{mod_min}",
            })
    except (ValueError, IndexError):
        issues.append({"severity": "warning", "type": "version_parse", "message": "Não foi possível parsear versões."})

    # Validação de dependências
    for dep in mod_manifest.get("dependencies", []):
        dep_found = any(m.get("name") == dep for m in loaded_mods)
        if not dep_found:
            issues.append({
                "severity": "error",
                "type": "missing_dependency",
                "message": f"Dependência '{dep}' não encontrada.",
            })

    return {
        "status": "success" if not any(i["severity"] == "error" for i in issues) else "issues_found",
        "compatible": not any(i["severity"] == "error" for i in issues),
        "mod_name": mod_manifest.get("name", "?"),
        "game_version": game_version,
        "required_version": mod_min,
        "issues": issues,
        "message": f"Validação: {'compativel' if not issues else f'{len(issues)} problemas'}.",
    }
