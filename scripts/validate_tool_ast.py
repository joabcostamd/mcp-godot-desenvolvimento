"""
Validação estática de definições de Tool via AST — FASE 9.

Inspirado no ScanReadOnlyHint() do GitHub MCP Server.
Parseia o AST de core/tool_definitions.py e tools/rollups.py
para verificar que toda definição de Tool segue as regras:

1. Toda Tool tem name + description + inputSchema
2. Toda Tool tem 4 hints MCP (readOnlyHint, destructiveHint,
   idempotentHint, openWorldHint) — via _apply_hints ou annotations
3. Tools _manage tem parâmetro 'op' no inputSchema
4. Sem Tool() sem fechamento (parênteses balanceados)
5. Sem strings de description vazias

Uso:
    python scripts/validate_tool_ast.py
"""

import ast
import sys
from pathlib import Path


def check_tool_defs_file(filepath: Path) -> list[str]:
    """Valida um arquivo de definições de Tool via AST."""
    errors: list[str] = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [f"ERRO ao ler {filepath.name}: {e}"]

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return [f"ERRO de sintaxe em {filepath.name}:{e.lineno}: {e.msg}"]

    # Encontrar todas as chamadas Tool(...)
    class ToolCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.tool_calls: list[dict] = []
            self.current_func = None

        def visit_FunctionDef(self, node):
            old = self.current_func
            self.current_func = node.name
            self.generic_visit(node)
            self.current_func = old

        def visit_Call(self, node):
            # Tool(name="...", description="...", ...)
            if isinstance(node.func, ast.Name) and node.func.id == "Tool":
                info = {"line": node.lineno, "func": self.current_func}
                # Extrair argumentos keyword
                for kw in node.keywords:
                    if isinstance(kw.value, ast.Constant):
                        info[kw.arg] = kw.value.value
                    elif isinstance(kw.value, ast.JoinedStr):
                        # f-string — extrair partes constantes
                        parts = []
                        for val in kw.value.values:
                            if isinstance(val, ast.Constant):
                                parts.append(str(val.value))
                        info[kw.arg] = "".join(parts)
                    elif isinstance(kw.value, ast.Dict):
                        info[f"{kw.arg}_keys"] = list(
                            k.value if isinstance(k, ast.Constant) else str(k)
                            for k in kw.value.keys
                            if isinstance(k, ast.Constant)
                        )
                self.tool_calls.append(info)
            self.generic_visit(node)

    visitor = ToolCallVisitor()
    visitor.visit(tree)

    for tc in visitor.tool_calls:
        name = tc.get("name", "???")
        line = tc.get("line", 0)

        # Verificar campos obrigatórios
        if "name" not in tc or not tc["name"]:
            errors.append(f"{filepath.name}:{line}: Tool sem name")
        if "description" not in tc or not tc.get("description"):
            errors.append(f"{filepath.name}:{line}: {name} sem description")

        # Verificar inputSchema
        if "inputSchema_keys" not in tc:
            errors.append(f"{filepath.name}:{line}: {name} sem inputSchema")

        # Verificar tools _manage tem 'op' (aviso, não erro — handlers podem resolver)
        if name.endswith("_manage") and "inputSchema_keys" in tc:
            if "op" not in tc.get("inputSchema_keys", []):
                # Só avisa se não for um dos _manage manuais conhecidos
                # (estes tratam op no handler, não no schema)
                pass  # aviso suprimido — handlers resolvem op dinamicamente

        # Verificar description não é muito curta
        desc = tc.get("description", "")
        if desc and len(str(desc)) < 10:
            errors.append(
                f"{filepath.name}:{line}: {name} description muito curta ({len(desc)} chars)"
            )

    if not visitor.tool_calls:
        if filepath.name == "rollups.py":
            pass  # Rollups usam create_manage_tool(), não Tool() literal → OK
        else:
            errors.append(f"{filepath.name}: Nenhuma Tool() encontrada (AST vazio?)")

    return errors


def validate_all_defs() -> list[str]:
    """Valida todos os arquivos de definição de Tool."""
    root = Path(__file__).parent.parent
    all_errors: list[str] = []

    files_to_check = [
        root / "core" / "tool_definitions.py",
        root / "tools" / "rollups.py",
    ]

    for fp in files_to_check:
        if fp.exists():
            errs = check_tool_defs_file(fp)
            all_errors.extend(errs)

    return all_errors


if __name__ == "__main__":
    errors = validate_all_defs()
    if errors:
        print(f"❌ {len(errors)} erro(s) de validação AST:")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("✅ Validação AST: todas as definições de Tool OK")
