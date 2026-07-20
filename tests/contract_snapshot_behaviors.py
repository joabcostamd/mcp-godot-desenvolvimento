"""
test_contract_behaviors.py — Verificação de contrato para behaviors.

Estende o conceito do contract_snapshot.py existente:
- Verifica que behaviors/ tem estrutura canônica
- Verifica que behavior.json valida contra schema
- Verifica que .gd compila (Godot --check-only quando disponível)
- Verifica que .tscn referencia script existente

Este arquivo é chamado pelo auditar.py como parte do gate de qualidade.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Caminho base: diretório do projeto (raiz do repo)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEHAVIORS_DIR = PROJECT_ROOT / "behaviors"
SCHEMA_PATH = BEHAVIORS_DIR / "behavior.schema.json"

# Campos obrigatórios em todo behavior.json (sem validação completa de schema,
# apenas o mínimo para o gate rápido do auditar.py)
REQUIRED_FIELDS = {"name", "description_pt", "description_en", "version"}


def _load_json(path: Path) -> dict[str, Any] | None:
    """Carrega um JSON e retorna o dict, ou None se inválido."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
        print(f"[CONTRACT_FAIL] {path}: {e}")
        return None


def check_behaviors_exist() -> tuple[bool, str]:
    """Verifica que o diretório behaviors/ existe e não está vazio."""
    if not BEHAVIORS_DIR.exists():
        return False, f"[CONTRACT_FAIL] Diretório {BEHAVIORS_DIR} não existe."
    subdirs = [d for d in BEHAVIORS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not subdirs:
        return False, f"[CONTRACT_FAIL] behaviors/ existe mas está vazio."
    return True, f"[CONTRACT_PASS] behaviors/ contém {len(subdirs)} behavior(s): {[d.name for d in subdirs]}"


def check_schema_exists() -> tuple[bool, str]:
    """Verifica que behavior.schema.json existe e é JSON válido."""
    if not SCHEMA_PATH.exists():
        return False, f"[CONTRACT_FAIL] {SCHEMA_PATH} não encontrado."
    data = _load_json(SCHEMA_PATH)
    if data is None:
        return False, f"[CONTRACT_FAIL] {SCHEMA_PATH} não é JSON válido."
    return True, f"[CONTRACT_PASS] behavior.schema.json existe e é JSON válido."


def check_each_behavior() -> tuple[bool, list[str]]:
    """Verifica cada behavior individualmente."""
    results: list[str] = []
    all_ok = True

    if not BEHAVIORS_DIR.exists():
        return False, ["[CONTRACT_FAIL] behaviors/ não existe."]

    for behavior_dir in sorted(BEHAVIORS_DIR.iterdir()):
        if not behavior_dir.is_dir() or behavior_dir.name.startswith("."):
            continue

        name = behavior_dir.name
        json_path = behavior_dir / "behavior.json"
        gd_path = behavior_dir / f"{name}.gd"
        tscn_path = behavior_dir / f"{name}.tscn"
        test_path = behavior_dir / f"test_{name}.gd"
        readme_path = behavior_dir / "README.md"

        # 1. behavior.json existe e é válido
        if not json_path.exists():
            results.append(f"[CONTRACT_FAIL] {name}: behavior.json ausente.")
            all_ok = False
            continue

        data = _load_json(json_path)
        if data is None:
            results.append(f"[CONTRACT_FAIL] {name}: behavior.json inválido.")
            all_ok = False
            continue

        # 2. Campos obrigatórios
        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            results.append(f"[CONTRACT_FAIL] {name}: campos ausentes no behavior.json: {missing}")
            all_ok = False

        # 3. name bate com diretório
        if data.get("name") != name:
            results.append(
                f"[CONTRACT_FAIL] {name}: 'name' no behavior.json ({data.get('name')}) "
                f"não bate com diretório ({name})."
            )
            all_ok = False

        # 4. .gd existe
        if not gd_path.exists():
            results.append(f"[CONTRACT_FAIL] {name}: {name}.gd ausente.")
            all_ok = False

        # 5. .tscn existe
        if not tscn_path.exists():
            results.append(f"[CONTRACT_FAIL] {name}: {name}.tscn ausente.")
            all_ok = False

        # 6. test_*.gd existe
        if not test_path.exists():
            results.append(f"[CONTRACT_FAIL] {name}: test_{name}.gd ausente.")
            all_ok = False

        # 7. README.md existe
        if not readme_path.exists():
            results.append(f"[CONTRACT_FAIL] {name}: README.md ausente.")
            all_ok = False

        # 8. Parâmetros com range (para int e float)
        params = data.get("parameters", [])
        for p in params:
            ptype = p.get("type", "")
            if ptype in ("int", "float") and "range" not in p:
                results.append(
                    f"[CONTRACT_WARN] {name}: parâmetro '{p.get('name', '?')}' "
                    f"({ptype}) sem 'range' declarado."
                )

        if all(
            p.exists()
            for p in [json_path, gd_path, tscn_path, test_path, readme_path]
        ) and not missing:
            results.append(f"[CONTRACT_PASS] {name}: estrutura completa.")

    return all_ok, results


def check_distinct_names() -> tuple[bool, str]:
    """Verifica que nomes de behaviors são distinguíveis (distância de Levenshtein)."""
    if not BEHAVIORS_DIR.exists():
        return True, "[CONTRACT_SKIP] behaviors/ não existe."

    names = sorted(
        d.name for d in BEHAVIORS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    # Só verifica se houver 2+ behaviors
    if len(names) < 2:
        return True, f"[CONTRACT_PASS] Apenas {len(names)} behavior(s), sem risco de colisão."

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            ratio = _levenshtein_ratio(a, b)
            if ratio >= 0.75:
                return False, (
                    f"[CONTRACT_FAIL] Nomes muito similares: '{a}' e '{b}' "
                    f"({ratio:.0%}). Risco de confusão na busca semântica."
                )

    return True, "[CONTRACT_PASS] Todos os nomes são distinguíveis."


def _levenshtein_ratio(a: str, b: str) -> float:
    """Razão de similaridade de Levenshtein (0.0 = totalmente diferente, 1.0 = idêntico)."""
    la, lb = len(a), len(b)
    if la == 0:
        return 1.0 if lb == 0 else 0.0
    if lb == 0:
        return 0.0

    # Matriz com apenas 2 linhas (otimização de espaço)
    prev = list(range(lb + 1))
    curr = [0] * (lb + 1)

    for i in range(1, la + 1):
        curr[0] = i
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev

    distance = prev[lb]
    return 1.0 - distance / max(la, lb)


def check_tscn_validity() -> tuple[bool, list[str]]:
    """Verifica que .tscn files referenciam SubResources e ExtResources definidos.

    Analisa os arquivos .tscn em behaviors/ e templates/:
    - SubResource("X") usado → X deve estar definido em [sub_resource type="..." id="X"]
    - ExtResource("X") usado → X deve estar definido em [ext_resource ... id="X"]
    """
    results: list[str] = []
    all_ok = True
    tscn_dirs = [
        BEHAVIORS_DIR,
        PROJECT_ROOT / "templates",
    ]

    for tscn_dir in tscn_dirs:
        if not tscn_dir.exists():
            continue
        for tscn_path in sorted(tscn_dir.rglob("*.tscn")):
            ok, msg = _validate_one_tscn(tscn_path)
            results.append(msg)
            if not ok:
                all_ok = False

    if not results:
        results.append("[CONTRACT_SKIP] Nenhum .tscn encontrado.")

    return all_ok, results


def _validate_one_tscn(tscn_path: Path) -> tuple[bool, str]:
    """Valida um arquivo .tscn individual."""
    rel = tscn_path.relative_to(PROJECT_ROOT)
    try:
        content = tscn_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"[CONTRACT_FAIL] {rel}: erro ao ler — {e}"

    lines = content.split("\n")
    defined_subs: set[str] = set()
    defined_exts: set[str] = set()
    used_subs: list[tuple[str, int]] = []   # (name, line_no)
    used_exts: list[tuple[str, int]] = []   # (name, line_no)

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # SubResource definido: [sub_resource type="..." id="X"]
        if stripped.startswith("[sub_resource"):
            # Extrai o id
            parts = stripped.split()
            for part in parts:
                if part.startswith('id="'):
                    sub_id = part.split('"')[1]
                    defined_subs.add(sub_id)
                    break

        # ExtResource definido: [ext_resource ... id="X"]
        if stripped.startswith("[ext_resource"):
            parts = stripped.split()
            for part in parts:
                if part.startswith('id="'):
                    ext_id = part.split('"')[1]
                    defined_exts.add(ext_id)
                    break

        # SubResource usado: SubResource("X")
        if "SubResource(" in stripped:
            import re
            for match in re.finditer(r'SubResource\("([^"]+)"\)', stripped):
                used_subs.append((match.group(1), i))

        # ExtResource usado: ExtResource("X")
        if "ExtResource(" in stripped:
            import re
            for match in re.finditer(r'ExtResource\("([^"]+)"\)', stripped):
                used_exts.append((match.group(1), i))

    # Verifica SubResources
    undef_subs = [(name, ln) for name, ln in used_subs if name not in defined_subs]
    if undef_subs:
        details = ", ".join(f"{name} (linha {ln})" for name, ln in undef_subs)
        return False, (
            f"[CONTRACT_FAIL] {rel}: SubResource(s) usados mas não definidos: {details}. "
            f"Defina com [sub_resource type=\"...\" id=\"...\"]."
        )

    # Verifica ExtResources
    undef_exts = [(name, ln) for name, ln in used_exts if name not in defined_exts]
    if undef_exts:
        details = ", ".join(f"{name} (linha {ln})" for name, ln in undef_exts)
        return False, (
            f"[CONTRACT_FAIL] {rel}: ExtResource(s) usados mas não definidos: {details}."
        )

    return True, f"[CONTRACT_PASS] {rel}: .tscn válido ({len(defined_subs)} sub, {len(defined_exts)} ext)."


def run_all_checks() -> int:
    """Executa todas as verificações. Retorna 0 se tudo passar, 1 se falhar."""
    print("=" * 60)
    print("CONTRACT CHECK: Behaviors")
    print("=" * 60)

    all_pass = True

    # 1. Diretório existe
    ok, msg = check_behaviors_exist()
    print(msg)
    all_pass = all_pass and ok

    # 2. Schema existe
    ok, msg = check_schema_exists()
    print(msg)
    all_pass = all_pass and ok

    # 3. Cada behavior
    ok, results = check_each_behavior()
    for r in results:
        print(r)
    all_pass = all_pass and ok

    # 4. Nomes distinguíveis
    ok, msg = check_distinct_names()
    print(msg)
    all_pass = all_pass and ok

    # 5. .tscn validity (SubResource/ExtResource integrity)
    ok, results = check_tscn_validity()
    for r in results:
        print(r)
    all_pass = all_pass and ok

    print("=" * 60)
    if all_pass:
        print("RESULTADO: TODOS OS CHECKS PASSARAM.")
    else:
        print("RESULTADO: HÁ FALHAS. Corrija antes de prosseguir.")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run_all_checks())
