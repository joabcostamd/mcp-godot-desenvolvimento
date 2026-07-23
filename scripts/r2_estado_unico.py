"""R2: Estado único — unifica os 3 arquivos de progresso em 1."""
import json
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

# 1. Backup datado
src = ROOT / ".roadmap_progress.json"
ts = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = ROOT / f".roadmap_progress.json.backup-r2-{ts}"
shutil.copy2(src, backup)
print(f"Backup: {backup.name} ({backup.stat().st_size} bytes)")

# 2. Ler principal
with open(src, "r", encoding="utf-8") as f:
    principal = json.load(f)
original_keys = set(principal.keys())
print(f"Principal: {len(principal)} chaves")

divergencias_registradas = []

# 3. Processar .reorg_progress.json
reorg_file = ROOT / ".reorg_progress.json"
if reorg_file.exists():
    with open(reorg_file, "r", encoding="utf-8") as f:
        reorg = json.load(f)
    added = 0
    for k, v in reorg.items():
        new_key = f"arquivado_reorg_{k}"
        if k not in principal and new_key not in principal:
            if isinstance(v, dict):
                v = dict(v)
                v["status"] = "arquivado"
            principal[new_key] = v
            added += 1
        elif k in principal:
            divergencias_registradas.append(f"reorg x principal: '{k}' existe nos dois")
    print(f".reorg_progress.json: {len(reorg)} chaves, {added} copiadas")

# 4. Processar .roadmap_progress_a2.json
a2_file = ROOT / ".roadmap_progress_a2.json"
if a2_file.exists():
    with open(a2_file, "r", encoding="utf-8") as f:
        a2 = json.load(f)
    added = 0
    for k, v in a2.items():
        new_key = f"arquivado_a2_{k}"
        if k not in principal and new_key not in principal:
            if isinstance(v, dict):
                v = dict(v)
                v["status"] = "arquivado"
            principal[new_key] = v
            added += 1
        elif k in principal and isinstance(v, dict) and isinstance(principal.get(k), dict):
            if v.get("status") != principal[k].get("status"):
                divergencias_registradas.append(
                    f"a2 x principal: '{k}' status diverge (a2={v.get('status')}, principal={principal[k].get('status')})"
                )
    print(f".roadmap_progress_a2.json: {len(a2)} chaves, {added} copiadas")

# 5. Nenhuma chave pré-existente alterada
assert original_keys == set(k for k in principal if not k.startswith("arquivado_")), \
    "FALHA: chaves pré-existentes foram alteradas!"

# 6. Salvar principal atualizado
with open(src, "w", encoding="utf-8", newline="\n") as f:
    json.dump(principal, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"Principal atualizado: {len(principal)} chaves")

# 7. Mover para journal/estado-antigo/
dest = ROOT / "journal" / "estado-antigo"
dest.mkdir(parents=True, exist_ok=True)
for fname in [".reorg_progress.json", ".roadmap_progress_a2.json"]:
    fpath = ROOT / fname
    if fpath.exists():
        shutil.move(str(fpath), str(dest / fname))
        print(f"Movido: {fname} -> journal/estado-antigo/")

# 8. Adicionar ao .gitignore
gitignore = ROOT / ".gitignore"
lines = gitignore.read_text(encoding="utf-8").splitlines()
for pattern in [".reorg_progress.json", ".roadmap_progress_a2.json"]:
    if pattern not in lines:
        with open(gitignore, "a", encoding="utf-8") as f:
            f.write(f"{pattern}\n")
        print(f".gitignore: +{pattern}")

# 9. Divergências
if divergencias_registradas:
    print(f"\n{len(divergencias_registradas)} divergencia(s) encontrada(s):")
    for d in divergencias_registradas:
        print(f"  - {d}")
else:
    print("\nNenhuma divergência encontrada.")

print("\nR2 concluída.")
