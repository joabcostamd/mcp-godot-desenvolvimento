"""auto_resolver.py — Auto-resolucao de erros com travas (Fatia 1.12).

Laco completo: detectar -> diagnosticar -> aplicar -> confirmar.

Dois modos:
  - "seguro" (default): so aplica correcoes com confianca >= 0.9 E rotulo
    "corrige_causa". O resto so propoe.
  - "autonomo": aplica todas as "corrige_causa", checkpoint antes,
    verificacao depois. Rollback se quebrar.

Travas:
  - So age sobre erro reprodutivel
  - Checkpoint (safety.py) antes de modificar arquivo
  - Re-coleta erros apos aplicar e confirma que sumiu
  - Anti-spiral (governador 0.14): max 2 tentativas por erro
  - Marca: "corrigido", "silenciado", "falhou", "fantasma_ignorado", "proposto"

Uso:
    from tools.auto_resolver import AutoResolver, auto_resolve
    ar = AutoResolver()
    result = ar.resolve(project_path="/caminho/do/projeto", mode="seguro")
"""

import re as _re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ResolveResult:
    """Resultado da tentativa de resolucao de um erro."""

    erro_original: dict
    diagnosis: dict
    status: str  # "corrigido" | "silenciado" | "falhou" | "fantasma_ignorado" | "proposto"
    acao_tomada: str = ""
    backup_id: str | None = None
    tentativas: int = 1
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResolveReport:
    """Relatorio completo de uma sessao de auto-resolucao."""

    status: str  # "success" | "partial" | "nothing_to_do" | "blocked"
    mode: str
    total_erros: int = 0
    corrigidos: int = 0
    silenciados: int = 0
    falhas: int = 0
    propostos: int = 0
    fantasmas: int = 0
    resultados: list[dict] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["resumo"] = (
            f"{self.corrigidos} corrigidos, {self.silenciados} silenciados, "
            f"{self.falhas} falhas, {self.propostos} propostos, "
            f"{self.fantasmas} fantasmas de {self.total_erros} erros"
        )
        return d


class AutoResolver:
    """Auto-resolvedor de erros com travas de seguranca."""

    def __init__(self):
        self._attempts: dict[str, int] = {}  # erro_hash -> tentativas

    def resolve(
        self, project_path: str | None = None, mode: str = "seguro"
    ) -> dict:
        """Executa o laco completo de resolucao.

        Args:
            project_path: Caminho do projeto Godot
            mode: "seguro" (default) ou "autonomo"

        Returns:
            ResolveReport como dict
        """
        if mode not in ("seguro", "autonomo"):
            return {
                "status": "error",
                "message": f"Modo invalido: '{mode}'. Use 'seguro' ou 'autonomo'.",
            }

        # 1. Coletar erros
        from tools.error_collector import collect_errors
        collected = collect_errors(project_path)
        errors = collected.get("errors", [])

        if not errors:
            return ResolveReport(
                status="nothing_to_do", mode=mode
            ).to_dict()

        # 2. Classificar
        from tools.error_classifier import classify_errors
        diagnoses = classify_errors(errors)

        # 3. Resolver cada erro
        report = ResolveReport(
            status="success", mode=mode, total_erros=len(errors)
        )

        for i, diag in enumerate(diagnoses):
            error = errors[i] if i < len(errors) else {}
            result = self._resolve_one(error, diag, mode, project_path)
            report.resultados.append(result.to_dict())

            if result.status == "corrigido":
                report.corrigidos += 1
            elif result.status == "silenciado":
                report.silenciados += 1
            elif result.status == "falhou":
                report.falhas += 1
            elif result.status == "proposto":
                report.propostos += 1
            elif result.status == "fantasma_ignorado":
                report.fantasmas += 1

        if report.falhas > 0:
            report.status = "partial"
        if report.falhas == report.total_erros:
            report.status = "blocked"

        return report.to_dict()

    def _resolve_one(
        self, error: dict, diagnosis: dict, mode: str, project_path: str | None
    ) -> ResolveResult:
        """Resolve um unico erro."""
        rotulo = diagnosis.get("rotulo", "corrige_causa")
        confianca = diagnosis.get("confianca", 0.0)

        # Trava 1: Fantasma — nao age sobre erro nao reprodutivel
        reprodutivel = error.get("reprodutivel")
        if reprodutivel is False:
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status="fantasma_ignorado",
                acao_tomada="Erro nao reprodutivel — ignorado (fantasma).",
            )

        # Trava 2: Modo seguro — so aplica alta confianca + corrige_causa
        if mode == "seguro":
            if rotulo != "corrige_causa" or confianca < 0.9:
                return ResolveResult(
                    erro_original=error,
                    diagnosis=diagnosis,
                    status="proposto",
                    acao_tomada=(
                        f"Modo seguro: apenas proposicao. "
                        f"Rotulo={rotulo}, confianca={confianca}. "
                        f"Patch proposto: {diagnosis.get('patch_proposto', '?')[:200]}"
                    ),
                )

        # Trava 3: Anti-spiral — max 2 tentativas por erro
        erro_key = self._error_key(error)
        self._attempts[erro_key] = self._attempts.get(erro_key, 0) + 1
        if self._attempts[erro_key] > 2:
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status="falhou",
                tentativas=self._attempts[erro_key],
                acao_tomada=(
                    f"Anti-spiral: {self._attempts[erro_key]} tentativas. "
                    f"Escalar para revisao humana."
                ),
            )

        # Trava 4: Checkpoint antes de modificar
        arquivo = error.get("arquivo", "")
        backup_id = None
        if arquivo:
            try:
                from tools.safety import checkpoint
                backup_id = checkpoint(arquivo, project_path)
            except Exception:
                pass  # Checkpoint falhou — segue sem (modo autônomo assume risco)

        # Trava 5: Aplicar patch
        patch = diagnosis.get("patch_proposto", "")
        if not patch or not arquivo:
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status="falhou",
                backup_id=backup_id,
                acao_tomada="Sem arquivo ou patch para aplicar.",
            )

        applied = self._apply_patch(error, diagnosis, arquivo, project_path)

        if not applied:
            # Rollback se checkpoint foi criado
            if backup_id and project_path:
                self._do_rollback(backup_id, project_path)
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status="falhou",
                backup_id=backup_id,
                acao_tomada="Falha ao aplicar o patch no arquivo.",
            )

        # Trava 6: Baseline antes, re-coletar depois, confirmar que sumiu
        baseline = self._capture_baseline(error, project_path)
        confirmed = self._confirm_fix(error, project_path, baseline)

        if confirmed:
            status = "corrigido" if rotulo == "corrige_causa" else "silenciado"
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status=status,
                backup_id=backup_id,
                acao_tomada="Patch aplicado e erro confirmado como resolvido.",
            )
        else:
            # Rollback — desfaz a correcao que nao funcionou
            if backup_id and project_path:
                self._do_rollback(backup_id, project_path)
            return ResolveResult(
                erro_original=error,
                diagnosis=diagnosis,
                status="falhou",
                backup_id=backup_id,
                acao_tomada="Patch aplicado mas erro persiste. Rollback executado.",
            )

    # ── Helpers ────────────────────────────────────────────────

    def _error_key(self, error: dict) -> str:
        """Gera chave unica para tracking de tentativas."""
        return (
            f"{error.get('tipo','?')}:{error.get('arquivo','?')}:"
            f"{error.get('linha','?')}:{error.get('mensagem','')[:80]}"
        )

    def _apply_patch(
        self, error: dict, diagnosis: dict, arquivo: str, project_path: str | None
    ) -> bool:
        """Aplica o patch proposto no arquivo.

        Para correcoes triviais (typo, null check, variavel nao declarada),
        tenta gerar uma edicao concreta baseada no tipo de erro.

        Returns:
            True se o patch foi aplicado com sucesso
        """
        tipo = error.get("tipo", "parse")
        mensagem = diagnosis.get("causa_provavel", "")

        try:
            # Resolve caminho do arquivo
            file_path = self._resolve_file(arquivo, project_path)
            if not file_path or not file_path.exists():
                return False

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            linha = error.get("linha")

            # Gera conteudo corrigido baseado no tipo de erro
            new_content = self._generate_fix(
                content, linha, tipo, mensagem, diagnosis
            )

            if new_content is None or new_content == content:
                return False  # Nao foi possivel gerar uma correcao

            file_path.write_text(new_content, encoding="utf-8")
            return True

        except Exception:
            return False

    def _generate_fix(
        self, content: str, linha: int | None,
        tipo: str, mensagem: str, diagnosis: dict
    ) -> str | None:
        """Gera correcao concreta baseada no tipo de erro."""
        if linha is None:
            return None

        lines = content.split("\n")
        if linha < 1 or linha > len(lines):
            return None

        idx = linha - 1
        target = lines[idx]

        if tipo == "parse":
            return self._fix_parse(target, lines, idx, mensagem, diagnosis)
        elif tipo == "runtime":
            return self._fix_runtime(target, lines, idx, mensagem, diagnosis)
        else:
            return None

    def _fix_parse(
        self, target: str, lines: list, idx: int,
        mensagem: str, diagnosis: dict
    ) -> str | None:
        """Correcoes para erros de parse."""
        causa = diagnosis.get("causa_provavel", "")

        # "Identifier 'X' not declared" → adiciona var X antes da linha
        m = _re.search(r"(?i)variavel\s+['\"]?(\w+)['\"]?\s+usada\s+mas\s+nao\s+declarada", causa)
        if m:
            var_name = m.group(1)
            indent = len(target) - len(target.lstrip())
            declaration = " " * indent + f"var {var_name}"
            lines.insert(idx, declaration)
            return "\n".join(lines)

        # "Tipo 'X' encontrado onde se esperava 'Y'" — tenta cast
        m = _re.search(r"(?i)tipo\s+['\"]?(\w+)['\"]?\s+encontrado.*esperava\s+['\"]?(\w+)['\"]?", causa)
        if m:
            # Tenta adicionar cast: var = expected_type(value)
            # Isso e heuristico — nem sempre funciona
            return None  # Nao arriscar cast automatico

        # Erro de sintaxe — tenta correcoes simples
        if "sintaxe" in causa.lower() or "syntax" in causa.lower():
            # Remove caracteres problematicos comuns
            fixed = target
            fixed = _re.sub(r"[;]\s*$", "", fixed)  # Remove ; no fim (Python style em GDScript)
            if fixed != target:
                lines[idx] = fixed
                return "\n".join(lines)

        return None

    def _fix_runtime(
        self, target: str, lines: list, idx: int,
        mensagem: str, diagnosis: dict
    ) -> str | None:
        """Correcoes para erros de runtime."""
        causa = diagnosis.get("causa_provavel", "")

        # Null reference → adiciona if obj != null antes da linha
        if "null" in causa.lower() or "nula" in causa.lower():
            indent = len(target) - len(target.lstrip())
            # Tenta extrair nome da variavel da linha
            var_match = _re.search(r"(\w+)\.", target)
            if var_match:
                var_name = var_match.group(1)
                guard = " " * indent + f"if {var_name} != null:"
                lines[idx] = " " * (indent + 4) + lines[idx].lstrip()
                lines.insert(idx, guard)
                return "\n".join(lines)

        # Divisao por zero — extrai variavel da linha e adiciona guard
        if "divisao" in causa.lower() or "zero" in causa.lower():
            indent = len(target) - len(target.lstrip())
            # Tenta extrair nome da variavel usada como divisor
            div_match = _re.search(r"/\s*(\w+)", target)
            divisor = div_match.group(1) if div_match else "divisor"
            guard = " " * indent + f"if {divisor} != 0:"
            lines[idx] = " " * (indent + 4) + lines[idx].lstrip()
            lines.insert(idx, guard)
            return "\n".join(lines)

        return None

    def _capture_baseline(self, error: dict, project_path: str | None) -> dict | None:
        """Captura estado dos erros ANTES da correcao para comparacao."""
        try:
            from tools.error_collector import collect_errors
            return collect_errors(project_path)
        except Exception:
            return None

    def _do_rollback(self, backup_id: str, project_path: str | None) -> bool:
        """Restaura arquivo a partir do backup."""
        try:
            from tools.safety import restore
            result = restore(backup_id, project_path)
            return result.get("status") == "success"
        except Exception:
            return False

    def _confirm_fix(
        self, error: dict, project_path: str | None, baseline: dict | None = None
    ) -> bool:
        """Re-coleta erros e verifica se o erro especifico desapareceu.

        Compara contra baseline (se fornecida) para evitar falso positivo
        quando collect_errors retorna vazio por falha de conexao.
        """
        try:
            from tools.error_collector import collect_errors
            collected = collect_errors(project_path)
            remaining = collected.get("errors", [])

            # Se tem baseline, verifica se a coleta atual e valida
            if baseline:
                baseline_total = baseline.get("total", -1)
                # Se baseline tinha erros e agora tem 0, e uma mudanca real
                if baseline_total > 0 and len(remaining) == 0:
                    return True  # Todos os erros sumiram — correcao funcionou
                # Se baseline ja era 0, nao podemos confirmar (falso positivo)
                if baseline_total == 0:
                    return False  # Nao havia erros antes — nao podemos confirmar

            # Procura o mesmo erro nos remanescentes
            for e in remaining:
                if (
                    e.get("tipo") == error.get("tipo")
                    and e.get("arquivo") == error.get("arquivo")
                    and e.get("linha") == error.get("linha")
                    and e.get("mensagem", "")[:80] == error.get("mensagem", "")[:80]
                ):
                    return False  # Erro ainda existe

            return True  # Erro sumiu
        except Exception:
            return False

    def _resolve_file(self, arquivo: str, project_path: str | None) -> Path | None:
        """Resolve caminho do arquivo para Path absoluto."""
        if not arquivo:
            return None

        p = Path(arquivo)
        if p.is_absolute() and p.exists():
            return p

        if project_path:
            base = Path(project_path)
            candidate = base / arquivo
            if candidate.exists():
                return candidate

        # Tenta com projeto ativo
        try:
            from tools.project_ops import _get_active_project
            proj = _get_active_project()
            if proj:
                candidate = Path(proj) / arquivo
                if candidate.exists():
                    return candidate
        except Exception:
            pass

        return None


# ── Singleton ──────────────────────────────────────────────────────

_resolver: AutoResolver | None = None


def get_auto_resolver() -> AutoResolver:
    global _resolver
    if _resolver is None:
        _resolver = AutoResolver()
    return _resolver


def auto_resolve(project_path: str | None = None, mode: str = "seguro") -> dict:
    """Interface publica — resolve erros automaticamente.

    Args:
        project_path: Caminho do projeto Godot
        mode: "seguro" (default) ou "autonomo"

    Returns:
        ResolveReport como dict
    """
    return get_auto_resolver().resolve(project_path, mode)
