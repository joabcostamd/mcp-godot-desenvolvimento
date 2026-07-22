"""entity_index.py — Indice de Entidades (FATIA 2.AF).

Mapeia nomes semanticos ("inimigo", "jogador", "moeda") para nos
concretos na cena. Permite comandos como "deixa os inimigos mais
rapidos" funcionarem sem que a IA precise adivinhar quais nos sao.

Estrategia:
  1. Parseia .tscn para extrair nos e seus scripts
  2. Classifica por behavior (class_name do script)
  3. Agrupa por tags dos behaviors (do behavior.json)
  4. Expoe indice invertido: tag → lista de NodePaths
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BEHAVIORS_DIR = ROOT / "behaviors"


def _load_behavior_tags() -> dict[str, list[str]]:
    """Carrega mapeamento class_name → tags de todos os behaviors."""
    tag_map = {}
    if not BEHAVIORS_DIR.is_dir():
        return tag_map

    for entry in BEHAVIORS_DIR.iterdir():
        if not entry.is_dir():
            continue
        bj = entry / "behavior.json"
        gd = entry / f"{entry.name}.gd"
        if not bj.exists() or not gd.exists():
            continue

        try:
            with open(bj, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        # Extrai class_name do .gd
        try:
            with open(gd, "r", encoding="utf-8") as f:
                gd_content = f.read()
            m = re.search(r"class_name\s+(\w+)", gd_content)
            class_name = m.group(1) if m else entry.name
        except OSError:
            class_name = entry.name

        tags = data.get("tags", [])
        genres = data.get("genres", [])
        all_tags = list(set(tags + genres))
        tag_map[class_name] = all_tags

    return tag_map


def index_scene(scene_path: str) -> dict:
    """Indexa uma cena .tscn, mapeando tags para NodePaths.

    Args:
        scene_path: Caminho para o arquivo .tscn.

    Returns:
        dict com indice de entidades.
    """
    scene_file = Path(scene_path)
    if not scene_file.exists():
        return {"status": "error", "message": f"Cena nao encontrada: {scene_path}"}

    try:
        content = scene_file.read_text(encoding="utf-8")
    except OSError as e:
        return {"status": "error", "message": f"Erro ao ler cena: {e}"}

    behavior_tags = _load_behavior_tags()

    # Parseia a cena
    entities = defaultdict(list)  # tag → [NodePath, ...]
    nodes = {}  # id → {name, type, script, path}

    # Extrai ext_resources (scripts)
    scripts = {}
    for m in re.finditer(r'\[ext_resource\s+type="Script".*?id="([^"]+)"\s*\]', content):
        # Proxima linha tem o path
        pass

    # Extrai scripts com path
    for m in re.finditer(r'\[ext_resource\s+type="Script".*?path="([^"]+)"\s+id="([^"]+)"', content):
        path = m.group(1)
        rid = m.group(2)
        scripts[rid] = path

    # Extrai nos
    current_path = []
    for line in content.split("\n"):
        # Node: [node name="X" type="Y" parent="Z"]
        node_match = re.match(r'\[node\s+name="([^"]+)"\s+type="([^"]+)"', line)
        if node_match:
            name = node_match.group(1)
            ntype = node_match.group(2)

            # Mantem hierarquia de paths
            parent_match = re.search(r'parent="([^"]+)"', line)
            if parent_match:
                parent = parent_match.group(1)
                # Find parent in current_path
                while current_path and current_path[-1] != parent:
                    current_path.pop()
            else:
                current_path = []

            current_path.append(name)
            full_path = "/".join(current_path)
            nodes[full_path] = {"name": name, "type": ntype, "path": full_path}

        # Script: script = ExtResource("X")
        script_match = re.search(r'script\s*=\s*ExtResource\("([^"]+)"\)', line)
        if script_match and current_path:
            rid = script_match.group(1)
            if rid in scripts:
                script_path = scripts[rid]
                # Extrai o nome do behavior do path
                for class_name, tags in behavior_tags.items():
                    if class_name.lower() in script_path.lower():
                        full_path = "/".join(current_path)
                        for tag in tags:
                            entities[tag].append(full_path)
                        entities[class_name.lower()].append(full_path)

    return {
        "status": "success",
        "scene": str(scene_file),
        "total_nodes": len(nodes),
        "entities": {tag: paths for tag, paths in sorted(entities.items())},
        "aliases": _generate_aliases(entities),
        "message": f"{len(nodes)} nos indexados. {len(entities)} categorias de entidades encontradas.",
    }


def _generate_aliases(entities: dict) -> dict:
    """Gera aliases PT-BR comuns para categorias."""
    alias_map = {
        "combate": ["inimigo", "inimigos", "enemy", "enemies", "monstro", "boss"],
        "movimento": ["moving", "movement", "andar", "correr"],
        "jogador": ["player", "heroi", "personagem"],
        "coleta": ["item", "moeda", "coin", "loot", "coletavel"],
        "ambiente": ["cenario", "mapa", "mundo", "fase"],
        "ui": ["interface", "hud", "menu", "botao"],
        "fisica": ["colisao", "gravidade", "corpo"],
        "sistema": ["save", "load", "config", "audio", "save/load"],
    }
    aliases = {}
    for tag, paths in entities.items():
        for canonical, alt_list in alias_map.items():
            if tag in alt_list or any(a in tag for a in alt_list):
                if canonical not in aliases:
                    aliases[canonical] = []
                aliases[canonical].extend(paths)
    return aliases


def query_entities(scene_path: str, query: str) -> dict:
    """Busca entidades por nome semantico.

    Args:
        scene_path: Caminho da cena .tscn.
        query: Termo de busca (ex: "inimigo", "jogador", "moeda").

    Returns:
        dict com NodePaths correspondentes.
    """
    index = index_scene(scene_path)
    if index["status"] != "success":
        return index

    query_lower = query.lower()

    # Busca direta nas tags
    for tag, paths in index["entities"].items():
        if query_lower in tag:
            return {
                "status": "success",
                "query": query,
                "matched_tag": tag,
                "nodes": paths,
                "count": len(paths),
            }

    # Busca nos aliases
    for canonical, paths in index.get("aliases", {}).items():
        if query_lower in canonical:
            return {
                "status": "success",
                "query": query,
                "matched_alias": canonical,
                "nodes": paths,
                "count": len(paths),
            }

    return {
        "status": "not_found",
        "query": query,
        "available_tags": sorted(index["entities"].keys()),
        "message": f"Entidade '{query}' nao encontrada. Tags disponiveis: {sorted(index['entities'].keys())[:20]}",
    }
