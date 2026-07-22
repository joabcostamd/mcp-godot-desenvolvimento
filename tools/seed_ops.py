"""seed_ops.py — Semente de Reproducibilidade (FATIA 2.AS).

Garante que a mesma frase de entrada produza o mesmo resultado,
permitindo testar regressao de comportamento do MCP + IA.

Fonte: Godot 4.7 docs — seed() e rand_from_seed().
Padrao: semente derivada do hash SHA-256 do prompt, garantindo
determinismo cross-sessao sem expor o prompt original.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# Arquivo que armazena a semente da sessao atual
_SEED_FILE = ROOT / ".mcp_seed_state.json"


def derive_seed(prompt: str) -> int:
    """Deriva uma semente inteira deterministica a partir do prompt.

    Usa SHA-256 para gerar um hash de 64 bits que cabe num int do Godot.
    O mesmo prompt sempre produz a mesma semente.
    """
    hash_bytes = hashlib.sha256(prompt.encode("utf-8")).digest()
    # Usa os primeiros 8 bytes como inteiro (64-bit signed)
    seed = int.from_bytes(hash_bytes[:8], byteorder="big", signed=True)
    return seed


def set_session_seed(seed: int | None = None, prompt: str = "") -> dict:
    """Define a semente de reprodutibilidade para a sessao atual.

    Se seed for None, deriva do prompt. Se prompt for vazio, usa timestamp.

    Returns:
        dict com status e a semente definida.
    """
    if seed is None:
        if prompt:
            seed = derive_seed(prompt)
        else:
            # Fallback: timestamp como semente (nao deterministico, mas documentado)
            seed = int(time.time() * 1000) % (2**31)

    state = {
        "seed": seed,
        "derived_from": "prompt_hash" if prompt else "timestamp",
        "timestamp": time.time(),
        "godot_seed_call": f"seed({seed})",
        "godot_rand_from_seed_call": f"rand_from_seed({seed})",
    }

    _SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SEED_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "seed": seed,
        "message": (
            f"Semente {seed} definida. "
            f"No Godot, use `seed({seed})` para RNG global ou "
            f"`rand_from_seed({seed})` para sequencia isolada."
        ),
    }


def get_session_seed() -> dict:
    """Le a semente da sessao atual.

    Returns:
        dict com a semente ou None se nao definida.
    """
    if not _SEED_FILE.exists():
        return {"status": "not_set", "seed": None, "message": "Nenhuma semente definida. Use set_session_seed()."}

    state = json.loads(_SEED_FILE.read_text(encoding="utf-8"))
    return {
        "status": "success",
        "seed": state["seed"],
        "derived_from": state.get("derived_from", "unknown"),
        "godot_call": state.get("godot_seed_call", f"seed({state['seed']})"),
    }


def verify_reproducibility(prompt: str, expected_seed: int | None = None) -> dict:
    """Verifica que o mesmo prompt produz a mesma semente.

    Se expected_seed for fornecido, verifica que bate.
    Senao, gera duas vezes e compara.
    """
    seed1 = derive_seed(prompt)
    seed2 = derive_seed(prompt)

    if expected_seed is not None:
        match = seed1 == expected_seed
        return {
            "status": "success" if match else "fail",
            "seed": seed1,
            "expected": expected_seed,
            "match": match,
            "message": (
                f"Semente {seed1} {'bate' if match else 'NAO bate'} com a esperada {expected_seed}."
            ),
        }

    match = seed1 == seed2
    return {
        "status": "success" if match else "fail",
        "seed": seed1,
        "match": match,
        "message": (
            f"Mesmo prompt produz mesma semente: {seed1} == {seed2} -> {match}."
        ),
    }


def seed_gdscript_inject(project_path: str, seed: int | None = None, prompt: str = "") -> dict:
    """Gera o codigo GDScript para injetar a semente num projeto.

    Cria um autoload seed_repro.gd que define a semente no inicio.
    """
    if seed is None:
        seed = derive_seed(prompt) if prompt else int(time.time() * 1000) % (2**31)

    gdscript = f'''# seed_repro.gd — Autoload de Reproducibilidade (FATIA 2.AS)
# Gerado pelo MCP Godot Agent.
# Semente: {seed}
extends Node

func _ready() -> void:
\tseed({seed})
\tprint("[seed_repro] Semente definida: {seed}")
'''

    project_dir = Path(project_path)
    if not project_dir.exists():
        return {"status": "error", "message": f"Projeto nao encontrado: {project_path}"}

    seed_file = project_dir / "seed_repro.gd"
    seed_file.write_text(gdscript, encoding="utf-8")

    return {
        "status": "success",
        "seed": seed,
        "file": str(seed_file),
        "message": f"Arquivo {seed_file} criado. Adicione como autoload no project.godot.",
    }
