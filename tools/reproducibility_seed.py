"""reproducibility_seed.py — Semente de Reprodutibilidade (FATIA 2.AS).

Garante que a mesma frase de entrada produza o mesmo resultado,
permitindo testar regressao de comportamento do MCP.

Como funciona:
1. Gera um hash deterministico (SHA-256) da frase de entrada + versao do MCP
2. Usa o hash como seed para random, garantindo reproducibilidade
3. Salva o par (frase, seed) para auditoria futura
4. Permite replay: mesma frase → mesma seed → mesmo resultado

Tools:
    generate_seed — gera seed a partir de frase
    replay_seed — replay de uma sessao anterior
    list_seeds — lista seeds registradas
    verify_seed — verifica se resultado atual bate com seed anterior
"""

import hashlib
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEEDS_FILE_NAME = ".mcp_reproducibility_seeds.json"


# ══════════════════════════════════════════════════════════════════════
# generate_seed
# ══════════════════════════════════════════════════════════════════════

def generate_seed(
    prompt: str,
    mcp_version: str = "3.2.1",
    project_path: str = ".",
) -> dict:
    """Gera uma seed deterministica a partir de uma frase/prompt.

    Args:
        prompt: Frase ou prompt do usuario.
        mcp_version: Versao do MCP (para versionamento de seeds).
        project_path: Caminho do projeto.

    Returns:
        dict com seed, hash e metadados.
    """
    # Hash deterministico: prompt + versao + timestamp truncado (dia)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seed_input = f"{prompt.strip()}|v{mcp_version}|{today}"
    seed_hash = hashlib.sha256(seed_input.encode("utf-8")).hexdigest()

    # Usa o hash como seed numerica
    seed_int = int(seed_hash[:16], 16) % (2**31 - 1)

    # Salvar no registro
    proj = Path(project_path)
    seeds_file = proj / SEEDS_FILE_NAME
    seeds_data = _load_seeds(seeds_file)

    seed_entry = {
        "prompt": prompt.strip(),
        "seed_hash": seed_hash[:16],
        "seed_int": seed_int,
        "mcp_version": mcp_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()[:16],
    }

    # Evitar duplicatas
    existing = [s for s in seeds_data if s["prompt_hash"] == seed_entry["prompt_hash"]]
    if existing:
        return {
            "status": "already_exists",
            "seed": existing[0],
            "message": "Seed ja existe para este prompt. Use replay_seed() para reproduzir.",
        }

    seeds_data.append(seed_entry)
    _save_seeds(seeds_file, seeds_data)

    return {
        "status": "generated",
        "seed": seed_entry,
        "message": f"Seed gerada: {seed_hash[:16]}. Use replay_seed() para reproduzir o resultado.",
    }


# ══════════════════════════════════════════════════════════════════════
# replay_seed
# ══════════════════════════════════════════════════════════════════════

def replay_seed(
    prompt_hash: str = "",
    prompt: str = "",
    project_path: str = ".",
) -> dict:
    """Recupera uma seed anterior pelo hash ou prompt original.

    Args:
        prompt_hash: Hash do prompt (16 chars). Alternativa ao prompt.
        prompt: Prompt original. Alternativa ao prompt_hash.
        project_path: Caminho do projeto.

    Returns:
        dict com seed recuperada ou erro.
    """
    proj = Path(project_path)
    seeds_file = proj / SEEDS_FILE_NAME
    seeds_data = _load_seeds(seeds_file)

    if not seeds_data:
        return {"status": "empty", "message": "Nenhuma seed registrada. Use generate_seed() primeiro."}

    # Buscar por hash ou prompt
    if prompt_hash:
        target_hash = prompt_hash[:16]
        for seed in seeds_data:
            if seed["prompt_hash"] == target_hash:
                return {
                    "status": "found",
                    "seed": seed,
                    "message": f"Seed recuperada: {seed['seed_hash']}. Use seed_int={seed['seed_int']} para reproduzir.",
                }

    if prompt:
        target_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()[:16]
        for seed in seeds_data:
            if seed["prompt_hash"] == target_hash:
                return {
                    "status": "found",
                    "seed": seed,
                    "message": f"Seed recuperada para: '{seed['prompt'][:80]}...'",
                }

    return {"status": "not_found", "message": "Seed nao encontrada. Verifique o prompt ou hash."}


# ══════════════════════════════════════════════════════════════════════
# list_seeds
# ══════════════════════════════════════════════════════════════════════

def list_seeds(project_path: str = ".", limit: int = 20) -> dict:
    """Lista todas as seeds registradas no projeto.

    Args:
        project_path: Caminho do projeto.
        limit: Numero maximo de seeds retornadas.

    Returns:
        dict com lista de seeds.
    """
    proj = Path(project_path)
    seeds_file = proj / SEEDS_FILE_NAME
    seeds_data = _load_seeds(seeds_file)

    if not seeds_data:
        return {"status": "empty", "total": 0, "seeds": [], "message": "Nenhuma seed registrada."}

    recent = seeds_data[-limit:]

    return {
        "status": "success",
        "total": len(seeds_data),
        "shown": len(recent),
        "seeds": [
            {
                "prompt": s["prompt"][:100] + ("..." if len(s["prompt"]) > 100 else ""),
                "seed_hash": s["seed_hash"],
                "mcp_version": s["mcp_version"],
                "generated_at": s["generated_at"],
            }
            for s in reversed(recent)
        ],
        "message": f"{len(seeds_data)} seeds registradas. Mostrando as {len(recent)} mais recentes.",
    }


# ══════════════════════════════════════════════════════════════════════
# verify_seed
# ══════════════════════════════════════════════════════════════════════

def verify_seed(
    prompt: str,
    expected_result_signature: str = "",
    project_path: str = ".",
) -> dict:
    """Verifica se o resultado atual bate com uma seed anterior.

    Compara o hash do resultado atual com o hash armazenado na seed.
    Usado para detectar regressoes de comportamento.

    Args:
        prompt: Prompt original usado.
        expected_result_signature: Hash SHA-256 do resultado esperado.
        project_path: Caminho do projeto.

    Returns:
        dict com resultado da verificacao.
    """
    proj = Path(project_path)
    seeds_file = proj / SEEDS_FILE_NAME
    seeds_data = _load_seeds(seeds_file)

    target_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()[:16]

    matching = [s for s in seeds_data if s["prompt_hash"] == target_hash]
    if not matching:
        return {
            "status": "no_baseline",
            "message": "Nenhuma seed baseline encontrada para este prompt. Gere uma com generate_seed().",
        }

    seed = matching[0]

    if not expected_result_signature:
        return {
            "status": "baseline_only",
            "seed": seed,
            "message": "Baseline encontrada, mas sem assinatura de resultado para comparar.",
        }

    # Comparar assinaturas
    match = expected_result_signature[:16] == seed["seed_hash"]
    return {
        "status": "match" if match else "diverged",
        "seed": seed,
        "expected": seed["seed_hash"],
        "actual": expected_result_signature[:16],
        "message": "Resultado CONSISTENTE com baseline ✅" if match
        else "RESULTADO DIVERGIU da baseline ❌ — possivel regressao.",
    }


# ══════════════════════════════════════════════════════════════════════
# get_reproducible_random
# ══════════════════════════════════════════════════════════════════════

def get_reproducible_random(seed_int: int) -> random.Random:
    """Retorna um objeto Random com a seed especificada.

    Use para garantir que geracoes aleatorias sejam reproduziveis.

    Args:
        seed_int: Numero inteiro da seed.

    Returns:
        random.Random inicializado com a seed.
    """
    rng = random.Random()
    rng.seed(seed_int)
    return rng


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _load_seeds(filepath: Path) -> list[dict]:
    """Carrega seeds do arquivo JSON."""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_seeds(filepath: Path, seeds: list[dict]) -> None:
    """Salva seeds no arquivo JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(seeds, f, indent=2, ensure_ascii=False)
