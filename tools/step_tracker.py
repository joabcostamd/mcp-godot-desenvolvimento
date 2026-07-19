"""step_tracker.py — Registro de passos por fatia (Fatia 1.9).

Singleton que persiste passos concluidos intra-fatia, permitindo
durable execution: se a sessao morre no meio de uma fatia longa,
a retomada sabe exatamente onde parou.

Persiste em <mcp_root>/.mcp_fatia_steps/<fatia_key>.json

Uso:
    from tools.step_tracker import get_step_tracker
    st = get_step_tracker()
    st.record_step("fatia_1.9", 1, "ok — modulo criado")
    st.record_step("fatia_1.9", 2, "ok — integrado com resume_session")
    pending = st.get_next_pending_step("fatia_1.9")  # -> 3
"""

import json as _json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS_DIR = ROOT / ".mcp_fatia_steps"


class StepTracker:
    """Singleton — tracking de passos concluidos por fatia."""

    def __init__(self):
        STEPS_DIR.mkdir(parents=True, exist_ok=True)

    def _path_for(self, fatia_key: str) -> Path:
        """Caminho do arquivo de passos para uma fatia."""
        safe = fatia_key.replace("/", "_").replace("\\", "_")
        return STEPS_DIR / f"{safe}.json"

    def _load(self, fatia_key: str) -> dict:
        """Carrega o registro de passos de uma fatia, ou cria vazio."""
        fp = self._path_for(fatia_key)
        if fp.exists():
            try:
                return _json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "fatia": fatia_key,
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "passos": [],
        }

    def _save(self, data: dict):
        """Persiste o registro."""
        fp = self._path_for(data["fatia"])
        data["atualizado_em"] = datetime.now(timezone.utc).isoformat()
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(
            _json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def record_step(self, fatia_key: str, passo: int, resultado: str) -> dict:
        """Registra um passo como concluido.

        Args:
            fatia_key: chave da fatia (ex: "fatia_1.9")
            passo: numero do passo (1-based)
            resultado: descricao curta do resultado

        Returns:
            dict com status e passo registrado
        """
        data = self._load(fatia_key)
        # Evita duplicar o mesmo passo
        for p in data["passos"]:
            if p.get("passo") == passo:
                p["resultado"] = resultado
                p["atualizado_em"] = datetime.now(timezone.utc).isoformat()
                self._save(data)
                return {"status": "success", "action": "updated", "passo": passo}

        data["passos"].append({
            "passo": passo,
            "resultado": resultado,
            "concluido_em": datetime.now(timezone.utc).isoformat(),
        })
        # Ordena por numero de passo
        data["passos"].sort(key=lambda p: p["passo"])
        self._save(data)
        return {"status": "success", "action": "recorded", "passo": passo}

    def get_progress(self, fatia_key: str) -> dict:
        """Retorna o progresso completo de uma fatia.

        Returns:
            dict com fatia, total_passos, concluidos, passos[...]
        """
        data = self._load(fatia_key)
        passos_concluidos = [p["passo"] for p in data["passos"]]
        return {
            "fatia": fatia_key,
            "passos_concluidos": sorted(passos_concluidos),
            "total_concluidos": len(passos_concluidos),
            "detalhes": data["passos"],
        }

    def get_next_pending_step(self, fatia_key: str, total_passos: int | None = None) -> int | None:
        """Retorna o proximo passo pendente (1-based).

        Se a fatia nunca foi registrada, retorna 1.
        Se todos os passos conhecidos estao concluidos e total_passos
        e fornecido, retorna o proximo apos o ultimo concluido.
        Se todos estao feitos e total_passos e None, retorna None.

        Args:
            fatia_key: chave da fatia
            total_passos: numero total esperado de passos (opcional)

        Returns:
            numero do proximo passo pendente, ou None se todos concluidos
        """
        data = self._load(fatia_key)
        concluidos = {p["passo"] for p in data["passos"]}

        if not concluidos:
            return 1

        max_concluido = max(concluidos)

        # Verifica buracos (ex: passos 1,3 concluidos mas 2 nao)
        for i in range(1, max_concluido + 1):
            if i not in concluidos:
                return i

        # Todos de 1..max_concluido estao feitos
        # Se nao sabemos o total, sugerimos o proximo (comportamento padrao)
        if total_passos is not None:
            if max_concluido < total_passos:
                return max_concluido + 1
            return None  # todos os passos planejados estao feitos
        else:
            # Sem total conhecido: sugere o proximo passo logico
            return max_concluido + 1

    def clear_progress(self, fatia_key: str) -> dict:
        """Remove o progresso de uma fatia (ex: ao reiniciar)."""
        fp = self._path_for(fatia_key)
        if fp.exists():
            fp.unlink()
            return {"status": "success", "action": "cleared"}
        return {"status": "success", "action": "not_found"}


# ── Singleton ──────────────────────────────────────────────────────

_step_tracker: StepTracker | None = None


def get_step_tracker() -> StepTracker:
    """Retorna o singleton StepTracker."""
    global _step_tracker
    if _step_tracker is None:
        _step_tracker = StepTracker()
    return _step_tracker
