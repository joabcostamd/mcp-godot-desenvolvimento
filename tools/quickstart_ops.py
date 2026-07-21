"""quickstart_ops — quick_start: frase → projeto jogável em minutos.

Implementa o rollup quickstart_manage com op="run".
Usa matching por palavras-chave para match frase→blueprint.
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Stopwords em português — palavras ignoradas no matching
_STOPWORDS = {
    "de", "da", "do", "das", "dos", "um", "uma", "uns", "umas",
    "o", "a", "os", "as", "e", "ou", "que", "com", "para", "em",
    "no", "na", "nos", "nas", "por", "se", "jogo", "jogar",
    "fazer", "quero", "queria", "gostaria", "tipo", "estilo",
}

# Sinônimos PT-BR → termos canônicos dos blueprints
# ATENÇÃO: só mapear palavras FORTEMENTE indicativas de gênero.
# Palavras genéricas como "inimigo", "heroi", "fase" aparecem em todos os gêneros.
_SYNONYMS: dict[str, str] = {
    # Tiro — palavras exclusivas do gênero
    "atirar": "tiro", "atirando": "tiro", "tiro": "tiro", "tiros": "tiro",
    "nave": "tiro", "naves": "tiro", "navinha": "tiro",
    "asteroide": "tiro", "asteroides": "tiro",
    "bala": "tiro", "balas": "tiro", "disparo": "tiro", "disparos": "tiro",
    "shooter": "tiro", "top-down": "tiro", "topdown": "tiro",
    "bullet": "tiro", "survivors": "tiro",
    # Plataforma — palavras exclusivas do gênero
    "plataforma": "plataforma", "plataformas": "plataforma",
    "pular": "plataforma", "pulo": "plataforma", "pulos": "plataforma",
    "scroll": "plataforma", "lateral": "plataforma",
    # Puzzle — palavras exclusivas do gênero
    "puzzle": "puzzle", "quebra": "puzzle", "cabeca": "puzzle",
    "raciocinio": "puzzle", "logica": "puzzle", "logico": "puzzle",
    "enigmas": "puzzle", "enigma": "puzzle",
}


def _extract_keywords(phrase: str, apply_synonyms: bool = True) -> set[str]:
    """Extrai palavras-chave significativas da frase.

    Args:
        phrase: Texto de entrada.
        apply_synonyms: Se True, aplica dicionário de sinônimos (para frases do usuário).
                        Se False, mantém palavras originais (para blueprints).
    """
    words = re.findall(r'[a-zà-ú0-9]+', phrase.lower())
    result = set()
    for w in words:
        if w in _STOPWORDS or len(w) <= 1:
            continue
        if apply_synonyms:
            result.add(_SYNONYMS.get(w, w))
        else:
            result.add(w)
    return result


def _match_blueprint(phrase: str) -> tuple[dict | None, str, float]:
    """Encontra o blueprint mais próximo da frase por palavras-chave.

    Args:
        phrase: Frase em linguagem natural descrevendo o jogo.

    Returns:
        (blueprint_dict, nome_display, score) ou (None, "", 0.0) se nenhum match.
    """
    bdir = ROOT / "blueprints"
    if not bdir.is_dir():
        return None, "", 0.0

    keywords = _extract_keywords(phrase)
    if not keywords:
        return None, "", 0.0

    # Coleta todos os blueprints (exceto schema)
    candidates: list[tuple[dict, str, set[str]]] = []
    for bf in sorted(bdir.glob("*.json")):
        if "schema" in bf.name:
            continue
        try:
            data = json.loads(bf.read_text(encoding="utf-8"))
        except Exception:
            continue
        display = data.get("display_name_pt", data.get("genre", bf.stem))
        desc = data.get("description_pt", data.get("description_en", ""))
        tags = data.get("tags", [])
        if isinstance(tags, list):
            tag_text = " ".join(tags)
        else:
            tag_text = ""

        bp_keywords = _extract_keywords(f"{display} {desc} {tag_text}", apply_synonyms=False)
        candidates.append((data, display, bp_keywords))

    if not candidates:
        return None, "", 0.0

    # Calcula score: quantas palavras-chave do usuário aparecem no blueprint
    # Dividido pelo total de keywords do usuário (para normalizar entre 0 e 1)
    best_score = 0.0
    best = None
    best_name = ""
    for data, display, bp_kw in candidates:
        if not bp_kw:
            continue
        matches = len(keywords & bp_kw)
        score = matches / len(keywords) if keywords else 0.0
        if score > best_score:
            best_score = score
            best = data
            best_name = display

    if best is not None and best_score > 0.0:
        return best, best_name, best_score

    return None, "", 0.0


def _copy_templates(project_path: Path) -> dict:
    """Copia templates para o projeto e ajusta paths no .tscn.

    Args:
        project_path: Caminho da raiz do projeto Godot.

    Returns:
        dict com status.
    """
    src_templates = ROOT / "templates"
    dst_scenes = project_path / "scenes"
    dst_scripts = project_path / "scripts"

    dst_scenes.mkdir(parents=True, exist_ok=True)
    dst_scripts.mkdir(parents=True, exist_ok=True)

    # Copia scripts .gd necessários
    scripts_para_copiar = [
        "player_2d_controller.gd",
        "enemy_chase_basic.gd",
    ]
    for script_name in scripts_para_copiar:
        src = src_templates / script_name
        if src.exists():
            dst = dst_scripts / script_name
            shutil.copy2(src, dst)

    # Copia e ajusta a cena quick_start
    src_scene = src_templates / "quick_start_scene.tscn"
    if not src_scene.exists():
        return {"status": "error", "message": "Template quick_start_scene.tscn nao encontrado"}

    dst_scene = dst_scenes / "main.tscn"
    content = src_scene.read_text(encoding="utf-8")

    # Ajusta paths: res://templates/ → res://scripts/
    content = content.replace(
        'path="res://templates/',
        'path="res://scripts/'
    )

    dst_scene.write_text(content, encoding="utf-8")

    return {"status": "success", "scene_path": str(dst_scene)}


def _clone_seed(seed_name: str, project_name: str) -> dict:
    """Clona um jogo-semente para um novo projeto.

    Args:
        seed_name: Nome do seed (ex: "breakout").
        project_name: Nome do novo projeto.

    Returns:
        dict com status e project_path.
    """
    seed_file = ROOT / "seeds" / f"{seed_name}.json"
    if not seed_file.exists():
        return {"status": "error", "message": f"Seed '{seed_name}' nao encontrada. Seeds disponiveis: breakout"}

    try:
        seed = json.loads(seed_file.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler seed '{seed_name}': {e}"}

    # Cria o projeto
    from tools.project_ops import create_project, _get_projects_root
    projects_root = _get_projects_root()
    project_dir = projects_root / project_name
    result = create_project(name=project_name, path=str(project_dir))
    if result.get("status") != "success":
        return result

    project_path = Path(result.get("project_path", ""))
    if not project_path or not project_path.exists():
        return {"status": "error", "message": f"Projeto criado mas caminho invalido: {project_path}"}

    # Cria diretórios
    (project_path / "scenes").mkdir(parents=True, exist_ok=True)
    (project_path / "scripts").mkdir(parents=True, exist_ok=True)
    (project_path / "assets").mkdir(parents=True, exist_ok=True)

    seed_root = ROOT / "seeds" / seed_name
    scenes_copied = 0
    behaviors_copied = 0
    assets_copied = 0

    # Copia ou gera cenas listadas no seed
    scenes = seed.get("scenes", [])
    for scene in scenes:
        src_path = seed_root / scene["path"] if seed_root.exists() else None
        dst_name = Path(scene["path"]).name
        dst_path = project_path / "scenes" / dst_name
        if src_path and src_path.exists():
            shutil.copy2(src_path, dst_path)
            scenes_copied += 1
        else:
            # Gera cena básica a partir da descrição no JSON
            purpose = scene.get("purpose", "scene")
            desc = scene.get("description", "")
            _generate_scene_placeholder(dst_path, dst_name.replace(".tscn", ""), purpose, desc)
            scenes_copied += 1

    # Copia behaviors que realmente existem
    behaviors = seed.get("behaviors_used", [])
    for bhv in behaviors:
        bhv_name = bhv.get("name", "")
        found = False
        for gd_file in (ROOT / "behaviors").rglob(f"{bhv_name}*.gd"):
            dst = project_path / "scripts" / gd_file.name
            shutil.copy2(gd_file, dst)
            found = True
            behaviors_copied += 1
        if not found:
            # Gera script placeholder
            purpose = bhv.get("purpose", "")
            _generate_script_placeholder(
                project_path / "scripts" / f"{bhv_name}.gd",
                bhv_name, purpose
            )
            behaviors_copied += 1

    # Copia assets que existem
    assets = seed.get("assets", [])
    for asset in assets:
        src_path = seed_root / asset["path"] if seed_root.exists() else None
        if src_path and src_path.exists():
            dst = project_path / asset["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            assets_copied += 1

    # Define a cena principal
    main_scene = scenes[0]["path"] if scenes else "scenes/main.tscn"
    try:
        pg = project_path / "project.godot"
        if pg.exists():
            cfg = pg.read_text(encoding="utf-8")
            if "run/main_scene" not in cfg:
                cfg = cfg.replace("[application]", f'[application]\n\nrun/main_scene="res://{main_scene}"')
                pg.write_text(cfg, encoding="utf-8")
    except Exception:
        pass

    # Define o brief
    try:
        from tools.project_brief_ops import set_project_brief
        set_project_brief(genre=seed.get("genre", ""))
    except Exception:
        pass

    display = seed.get("display_name", seed_name)
    return {
        "status": "success",
        "project_path": str(project_path),
        "project_name": project_name,
        "seed": seed_name,
        "display_name": display,
        "scenes_copied": scenes_copied,
        "behaviors_copied": behaviors_copied,
        "assets_copied": assets_copied,
        "next_step": f"Abra o Godot e aperte F5 para jogar {display}. Use /plan para continuar desenvolvendo.",
    }


def _generate_scene_placeholder(path: Path, name: str, purpose: str, description: str) -> None:
    """Gera um .tscn mínimo para uma cena."""
    safe_name = name.replace(" ", "_")
    content = f"""[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/{safe_name}.gd" id="1_script"]

[node name="{name}" type="Node2D"]

[node name="Label" type="Label" parent="."]
text = "{purpose}: {description[:60]}"
"""
    path.write_text(content, encoding="utf-8")


def _generate_script_placeholder(path: Path, name: str, purpose: str) -> None:
    """Gera um .gd placeholder para um comportamento."""
    content = f"""extends Node
## {purpose or name} — placeholder gerado pelo modo remix.
## Implemente a lógica real aqui.
"""
    path.write_text(content, encoding="utf-8")


def quickstart_manage(op: str = "run", phrase: str = "", project_name: str = "", seed: str = "breakout") -> dict:
    """Rollup quickstart_manage — cria projeto jogável a partir de uma frase.

    Args:
        op: Operação ("run").
        phrase: Frase descrevendo o jogo (ex: "jogo de plataforma com herói").
        project_name: Nome do projeto (opcional, gerado da frase se vazio).

    Returns:
        dict com status e project_path ou mensagem de erro.
    """
    if op == "remix":
        if not seed or not seed.strip():
            return {"status": "error", "message": "Parametro 'seed' obrigatorio para op='remix'. Ex: 'breakout'."}
        return _clone_seed(seed.strip(), project_name or seed.strip())

    if op != "run":
        return {"status": "error", "message": f"Operacao '{op}' nao suportada. Use op='run'."}

    if not phrase or not phrase.strip():
        return {"status": "error", "message": "Parametro 'phrase' obrigatorio. Ex: 'jogo de plataforma'"}

    phrase = phrase.strip()

    # 1. Match da frase → blueprint
    blueprint, bp_name, score = _match_blueprint(phrase)
    if blueprint is None:
        bp_name = "Plataforma 2D"
        matched = False
    else:
        matched = score >= 0.3

    # 2. Gera nome do projeto se não fornecido
    if not project_name:
        slug = re.sub(r'[^a-z0-9]+', '_', phrase.lower().strip())[:30]
        project_name = slug.strip('_') or "meu_jogo"

    # 3. Cria o projeto
    from tools.project_ops import create_project, _get_projects_root
    projects_root = _get_projects_root()
    project_dir = projects_root / project_name
    result = create_project(name=project_name, path=str(project_dir))
    if result.get("status") != "success":
        return result

    project_path = Path(result.get("project_path", ""))
    if not project_path or not project_path.exists():
        return {"status": "error", "message": f"Projeto criado mas caminho invalido: {project_path}"}

    # 4. Define o brief do projeto (melhor esforço)
    try:
        from tools.project_brief_ops import set_project_brief
        set_project_brief(genre=bp_name)
    except Exception:
        pass  # fail-open

    # 5. Copia templates para o projeto
    copy_result = _copy_templates(project_path)
    if copy_result.get("status") != "success":
        return copy_result

    # 6. Define a cena principal no project.godot
    try:
        pg = project_path / "project.godot"
        if pg.exists():
            cfg = pg.read_text(encoding="utf-8")
            if "run/main_scene" not in cfg:
                cfg = cfg.replace("[application]", '[application]\n\nrun/main_scene="res://scenes/main.tscn"')
                pg.write_text(cfg, encoding="utf-8")
    except Exception:
        pass  # fail-open

    return {
        "status": "success",
        "project_path": str(project_path),
        "project_name": project_name,
        "blueprint": bp_name,
        "blueprint_matched": matched,
        "phrase": phrase,
        "next_step": "Abra o Godot e aperte F5 para jogar. Use /plan para continuar desenvolvendo.",
    }
