"""Registra fatias das ondas no .roadmap_progress.json."""
import json, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

with open(REPO / ".roadmap_progress.json", "r", encoding="utf-8") as f:
    d = json.load(f)

h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(REPO)).stdout.strip()

ondas = {
    "ONDA_1_registry.md": ["1.1", "1.2", "1.3", "1.4"],
    "ONDA_2_conformidade.md": ["2.1", "2.2", "2.3", "2.4", "2.5"],
    "ONDA_3_rollups.md": ["3.1"],
    "ONDA_4_descoberta.md": ["4.2", "4.3", "4.4", "4.5"],
    "ONDA_8_curadoria.md": ["8.1", "8.2", "8.3"],
    "ONDA_9_quarentena.md": ["9.1", "9.2"],
    "ONDA_10_congelar.md": ["10.1", "10.2", "10.3", "10.4", "10.5"],
    "ONDA_P_pendencias.md": ["P.1", "P.2", "P.3", "P.4", "P.5", "P.6", "P.7", "P.8", "P.9", "P.10", "P.11"],
}

count = 0
for onda, fatias in ondas.items():
    for f in fatias:
        key = f"fatia_{f.replace('.', '_')}"
        if key not in d:
            d[key] = {
                "status": "nao verificado",
                "checkpoint": None,
                "ficha": f".github/roadmap/{onda}",
                "marcacao": "[EIXO-CENTRAL]",
            }
            count += 1

d["reorg_R8_fichas"]["status"] = "concluida"
d["reorg_R8_fichas"]["checkpoint"] = h
d["reorg_R8_fichas"]["resultado"] = (
    f"R8 concluida: 8 arquivos ONDA_*.md criados, "
    f"{count} fatias registradas como nao verificado."
)

with open(REPO / ".roadmap_progress.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Registradas: {count} fatias novas")
print(f"R8 checkpoint: {h}")
