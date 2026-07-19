"""error_collector.py — Coletor unificado de erros (Fatia 1.10).

Consolida erros de 3 fontes num formato unico:
  1. gdscript_diagnostics (LSP)  → tipo "parse"
  2. read_console_output          → tipo "runtime"
  3. audit_*                      → tipo "editor"

Formato UnifiedError:
  {tipo, mensagem, arquivo, linha, coluna, stack, reprodutivel, fonte, timestamp}

Uso:
    from tools.error_collector import ErrorCollector
    ec = ErrorCollector()
    erros = ec.collect_all("/caminho/do/projeto")
"""

import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ── UnifiedError ────────────────────────────────────────────────────

@dataclass
class UnifiedError:
    """Formato canonico de erro — unifica parse, runtime e editor."""

    tipo: str           # "parse" | "runtime" | "editor"
    mensagem: str       # Mensagem literal do erro
    arquivo: str = ""   # Caminho do arquivo (relativo ao projeto)
    linha: int | None = None
    coluna: int | None = None
    stack: str = ""     # Stack trace (se disponivel)
    reprodutivel: bool | None = None  # True/False/None (None = nao verificado)
    fonte: str = ""     # Tool de origem (ex: "gdscript_diagnostics")
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


class ErrorCollector:
    """Coletor unificado de erros — agrega 3 fontes em 1 formato."""

    def collect_all(self, project_path: str | None = None) -> list[dict]:
        """Coleta erros de todas as fontes disponiveis.

        Args:
            project_path: Caminho do projeto Godot (opcional — usa ativo)

        Returns:
            Lista de UnifiedError como dicts
        """
        all_errors: list[UnifiedError] = []

        # Fonte 1: LSP (parse/compilacao)
        all_errors.extend(self._from_lsp(project_path))

        # Fonte 2: Console (runtime)
        all_errors.extend(self._from_console(project_path))

        # Fonte 3: Auditorias (editor/referencias)
        all_errors.extend(self._from_audits(project_path))

        return [e.to_dict() for e in all_errors]

    # ── Fonte 1: LSP (parse) ──────────────────────────────────

    def _from_lsp(self, project_path: str | None) -> list[UnifiedError]:
        """Coleta erros de compilacao via gdscript_diagnostics."""
        errors: list[UnifiedError] = []
        try:
            from tools.lsp_ops import gdscript_diagnostics
            from tools.project_ops import _get_active_project

            proj = self._resolve_project(project_path)
            if not proj:
                return errors

            # Varre scripts .gd do projeto
            for gd_file in proj.rglob("*.gd"):
                if self._should_skip(gd_file):
                    continue
                try:
                    diag = gdscript_diagnostics(str(gd_file))
                    if isinstance(diag, dict):
                        items = diag.get("diagnostics", diag.get("items", []))
                        if not items:
                            # Tenta extrair do resultado direto
                            if diag.get("status") == "error":
                                errors.append(UnifiedError(
                                    tipo="parse",
                                    mensagem=diag.get("message", str(diag)),
                                    arquivo=str(gd_file.relative_to(proj)),
                                    fonte="gdscript_diagnostics",
                                ))
                            continue
                        for item in items:
                            if isinstance(item, dict):
                                severity = item.get("severity", 0)
                                if severity >= 1:  # 1=error, 2=warning
                                    errors.append(UnifiedError(
                                        tipo="parse",
                                        mensagem=item.get("message", str(item)),
                                        arquivo=str(gd_file.relative_to(proj)),
                                        linha=item.get("line"),
                                        coluna=item.get("column"),
                                        fonte="gdscript_diagnostics",
                                    ))
                except Exception:
                    pass  # Arquivo pode nao ter script ou LSP offline
        except Exception:
            pass  # LSP nao disponivel

        return errors

    # ── Fonte 2: Console (runtime) ────────────────────────────

    def _from_console(self, project_path: str | None) -> list[UnifiedError]:
        """Coleta erros de runtime via read_console_output."""
        errors: list[UnifiedError] = []
        try:
            from tools.runtime_ops import read_console_output

            console = read_console_output()
            if console.get("status") != "success":
                return errors

            lines = console.get("lines", [])
            if not lines:
                return errors

            # Parse de linhas de erro do console Godot
            import re as _re

            for line in lines:
                text = line if isinstance(line, str) else str(line)

                # Padrao: E 0:00:00:0000   {mensagem} - {arquivo}:{linha} - {stack}
                error_match = _re.match(
                    r'^E\s+\d+:\d+:\d+:\d+\s+(.+)', text
                )
                if error_match:
                    msg = error_match.group(1).strip()
                    # Tenta extrair arquivo:linha
                    file_match = _re.search(r'-\s+(\S+\.gd):(\d+)\s*-', msg)
                    arquivo = ""
                    linha = None
                    if file_match:
                        arquivo = file_match.group(1)
                        linha = int(file_match.group(2))
                        msg = msg[:file_match.start()].strip()

                    errors.append(UnifiedError(
                        tipo="runtime",
                        mensagem=msg[:500],
                        arquivo=arquivo,
                        linha=linha,
                        fonte="read_console_output",
                    ))
        except Exception:
            pass

        return errors

    # ── Fonte 3: Auditorias (editor) ──────────────────────────

    def _from_audits(self, project_path: str | None) -> list[UnifiedError]:
        """Coleta problemas estruturais das ferramentas de auditoria."""
        errors: list[UnifiedError] = []

        audit_modules = [
            ("audit_input_map", "Input Map"),
            ("audit_autoloads", "Autoloads"),
            ("audit_scene_reachability", "Cenas inalcancaveis"),
            ("audit_uid_consistency", "UIDs inconsistentes"),
            ("audit_save_compatibility", "Save compatibility"),
        ]

        for mod_name, label in audit_modules:
            try:
                mod = __import__(f"tools.{mod_name}", fromlist=["audit"])
                # Cada modulo de auditoria tem uma funcao principal
                func = getattr(mod, "audit", None) or getattr(mod, f"run_{mod_name}", None)
                if func is None:
                    # Tenta achar qualquer funcao publica que faca auditoria
                    for attr in dir(mod):
                        if attr.startswith("audit") or attr.startswith("run_"):
                            func = getattr(mod, attr)
                            break

                if func is None:
                    continue

                # Se a funcao requer project_path
                import inspect
                sig = inspect.signature(func)
                result = None
                if "project_path" in sig.parameters:
                    result = func(project_path=project_path)
                else:
                    result = func()

                if isinstance(result, dict):
                    issues = result.get("issues", result.get("errors", result.get("findings", [])))
                    if not issues and result.get("status") == "success":
                        # Auditoria passou — sem erros
                        continue
                    if isinstance(issues, list):
                        for issue in issues:
                            if isinstance(issue, dict):
                                errors.append(UnifiedError(
                                    tipo="editor",
                                    mensagem=issue.get("message", issue.get("description", str(issue))),
                                    arquivo=issue.get("file", issue.get("path", "")),
                                    linha=issue.get("line"),
                                    fonte=f"audit/{mod_name}",
                                ))
                            elif isinstance(issue, str):
                                errors.append(UnifiedError(
                                    tipo="editor",
                                    mensagem=issue,
                                    fonte=f"audit/{mod_name}",
                                ))
                    elif result.get("status") == "error":
                        errors.append(UnifiedError(
                            tipo="editor",
                            mensagem=result.get("message", f"Auditoria {label} falhou"),
                            fonte=f"audit/{mod_name}",
                        ))
            except Exception:
                pass  # Auditoria nao disponivel — segue

        return errors

    # ── Helpers ────────────────────────────────────────────────

    def _resolve_project(self, project_path: str | None) -> Path | None:
        if project_path:
            return Path(project_path)
        try:
            from tools.project_ops import _get_active_project
            proj = _get_active_project()
            return Path(proj) if proj else None
        except Exception:
            return None

    def _should_skip(self, path: Path) -> bool:
        skip_dirs = {".godot", ".mcp_backups", "addons", ".git", "__pycache__"}
        return any(skip in path.parts for skip in skip_dirs)


# ── Singleton ──────────────────────────────────────────────────────

_collector: ErrorCollector | None = None


def get_error_collector() -> ErrorCollector:
    global _collector
    if _collector is None:
        _collector = ErrorCollector()
    return _collector


def collect_errors(project_path: str | None = None) -> dict:
    """Interface publica — coleta e retorna erros unificados.

    Returns:
        {"status": "success", "total": N, "errors": [UnifiedError...], "fontes": [...]}
    """
    ec = get_error_collector()
    errors = ec.collect_all(project_path)
    fontes = list(set(e.get("fonte", "?") for e in errors))
    return {
        "status": "success",
        "total": len(errors),
        "fontes_consultadas": fontes,
        "errors": errors,
    }
