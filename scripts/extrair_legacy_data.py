"""Extrai dados legados de server.py para core/legacy_data.py — ONDA 1.3."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

with open(ROOT / "server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Localizar blocos
blocks = {}
current_name = None
current_start = None
brace_depth = 0

for i, line in enumerate(lines):
    if line.startswith("TOOLSETS = {"):
        current_name = "TOOLSETS"
        current_start = i
        brace_depth = 1
    elif line.startswith("PHASE_TOOLSETS: dict[str, set[str]] = {"):
        current_name = "PHASE_TOOLSETS"
        current_start = i
        brace_depth = 1
    elif line.startswith("PHASE_TOOLS_CORE = {"):
        current_name = "PHASE_TOOLS_CORE"
        current_start = i
        brace_depth = 1
    elif current_name and brace_depth > 0:
        brace_depth += line.count("{") - line.count("}")
        if brace_depth == 0:
            blocks[current_name] = (current_start, i + 1)
            current_name = None

print(f"Blocos encontrados: {list(blocks.keys())}")
for name, (start, end) in blocks.items():
    print(f"  {name}: linhas {start+1}-{end}")

# Escrever core/legacy_data.py
header = '''"""Dados legados de curadoria — ONDA 1.3.

Extraidos de server.py. Importados por server.py e registry/.
Serao substituidos pelo registry quando dominios tiverem manifestos.
"""

'''
with open(ROOT / "core" / "legacy_data.py", "w", encoding="utf-8") as f:
    f.write(header)
    for name in ["TOOLSETS", "PHASE_TOOLSETS", "PHASE_TOOLS_CORE"]:
        if name in blocks:
            start, end = blocks[name]
            f.write("".join(lines[start:end]))
            f.write("\n")

print("core/legacy_data.py criado.")
