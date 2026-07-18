"""external_client.py — Cliente HTTP compartilhado para geracao externa (Fatia 0.9).

Fornece uma camada UNICA que toda tool de geracao externa
(musica, arte, 3D, voz) usa para chamar API, com:
  - Rate-limit (reusa RateLimiter)
  - Retry com backoff exponencial
  - Timeout configurável
  - Rastreio de custo por chamada
  - Tratamento de erro estruturado (nunca crash)

Uso:
    from tools.external_client import get_client
    client = get_client()
    result = client.call("generate_art", "https://api.example.com/v1/generate",
                         method="POST", json={"prompt": "..."})
"""

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("mcp-godot.external_client")

# ── Config defaults ─────────────────────────────────────────────────

DEFAULT_TIMEOUT = 30       # segundos
DEFAULT_MAX_RETRIES = 3    # tentativas antes de desistir
DEFAULT_BACKOFF_BASE = 2.0 # base do backoff exponencial (segundos)
DEFAULT_BACKOFF_MAX = 60.0 # teto do backoff


# ── Dataclasses ──────────────────────────────────────────────────────

@dataclass
class CallResult:
    """Resultado estruturado de uma chamada externa."""
    ok: bool
    status_code: int | None = None
    data: Any = None
    error: str = ""
    cost: float = 0.0         # custo estimado em USD
    retries: int = 0          # quantas tentativas foram feitas
    duration_ms: float = 0.0   # duracao total em ms
    idempotency_key: str = ""  # chave de idempotencia usada


@dataclass
class ClientStats:
    """Estatisticas acumuladas do cliente."""
    total_calls: int = 0
    total_success: int = 0
    total_failures: int = 0
    total_cost: float = 0.0
    total_retries: int = 0
    last_call_at: float = 0.0
    calls: list[dict] = field(default_factory=list)  # ultimas 100


# ── Cliente ──────────────────────────────────────────────────────────

class ExternalApiClient:
    """Cliente HTTP unico para todas as chamadas de API externa.

    Features:
      - Rate-limit via RateLimiter (tools/rate_limiter.py)
      - Retry com backoff exponencial + jitter
      - Timeout configuravel por chamada
      - Rastreio de custo acumulado
      - Idempotencia: mesma chamada com mesma chave = mesmo resultado (cache)
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        backoff_max: float = DEFAULT_BACKOFF_MAX,
        cache_size: int = 100,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.stats = ClientStats()
        self._idempotency_cache: dict[str, CallResult] = {}
        self._cache_max = cache_size

        # Rate limiter: 60 chamadas por minuto (default conservador)
        from tools.rate_limiter import RateLimiter
        self._rate_limiter = RateLimiter(
            max_requests=60,
            window_seconds=60,
            cooldown_seconds=30,
        )

    # ── API principal ────────────────────────────────────────────

    def call(
        self,
        tool_name: str,
        url: str,
        *,
        method: str = "POST",
        headers: dict | None = None,
        json_data: dict | None = None,
        data: bytes | None = None,
        timeout: int | None = None,
        idempotency_key: str | None = None,
        cost_estimate: float = 0.0,
    ) -> CallResult:
        """Faz uma chamada HTTP com retry, rate-limit e rastreio.

        Args:
            tool_name: Nome da tool que originou a chamada (ex: 'generate_art').
            url: URL completa do endpoint.
            method: HTTP method (GET, POST, etc).
            headers: Headers HTTP adicionais.
            json_data: Payload JSON para POST/PUT.
            data: Payload binario (alternativa a json_data).
            timeout: Timeout em segundos (default: self.timeout).
            idempotency_key: Chave de idempotencia (auto-gerada se None).
            cost_estimate: Custo estimado em USD desta chamada.

        Returns:
            CallResult com ok, data, error, cost, retries, duration.
        """
        import random
        import urllib.error
        import urllib.request

        start_time = time.time()
        timeout_val = timeout if timeout is not None else self.timeout

        # ── Rate limit ──────────────────────────────────────────
        allowed, rate_info = self._rate_limiter.check()
        if not allowed:
            return CallResult(
                ok=False,
                error=f"Rate limit excedido. Tente novamente em {rate_info['retry_after']}s.",
            )

        # ── Idempotencia ────────────────────────────────────────
        if idempotency_key is None:
            idempotency_key = self._make_idempotency_key(tool_name, url, json_data or {})
        cached = self._idempotency_cache.get(idempotency_key)
        if cached is not None:
            logger.info("Idempotency cache hit for %s", tool_name)
            self.stats.total_calls += 1
            self.stats.total_success += 1
            return cached

        # ── Preparar request ─────────────────────────────────────
        req_headers = dict(headers or {})
        req_headers.setdefault("User-Agent", "mcp-godot-agent/1.0")
        req_headers.setdefault("X-Idempotency-Key", idempotency_key)

        body: bytes | None = None
        if json_data is not None:
            body = json.dumps(json_data, ensure_ascii=False).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        elif data is not None:
            body = data

        # ── Retry loop ───────────────────────────────────────────
        last_error = ""
        retries = 0
        for attempt in range(self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers=req_headers,
                    method=method,
                )
                with urllib.request.urlopen(req, timeout=timeout_val) as resp:
                    resp_body = resp.read()
                    status = resp.status
                    result_data = resp_body.decode("utf-8", errors="replace")
                    try:
                        result_data = json.loads(result_data)
                    except (json.JSONDecodeError, TypeError):
                        pass  # mantem como string

                duration_ms = (time.time() - start_time) * 1000

                result = CallResult(
                    ok=True,
                    status_code=status,
                    data=result_data,
                    cost=cost_estimate,
                    retries=retries,
                    duration_ms=round(duration_ms, 1),
                    idempotency_key=idempotency_key,
                )

                # ── Atualizar estatisticas ─────────────────────
                self.stats.total_calls += 1
                self.stats.total_success += 1
                self.stats.total_cost += cost_estimate
                self.stats.total_retries += retries
                self.stats.last_call_at = time.time()
                self._record_call(tool_name, True, retries, cost_estimate)

                # ── Cache de idempotencia ──────────────────────
                self._idempotency_cache[idempotency_key] = result
                if len(self._idempotency_cache) > self._cache_max:
                    # Remove o mais antigo (FIFO simples)
                    oldest = next(iter(self._idempotency_cache))
                    del self._idempotency_cache[oldest]

                return result

            except urllib.error.HTTPError as e:
                status = e.code
                last_error = f"HTTP {status}: {e.reason}"
                # 4xx nao faz retry (erro do cliente, nao do servidor)
                if 400 <= status < 500:
                    break
            except urllib.error.URLError as e:
                last_error = f"URL Error: {e.reason}"
            except TimeoutError:
                last_error = f"Timeout apos {timeout_val}s"
            except Exception as e:
                last_error = f"Erro inesperado: {e}"

            retries = attempt + 1
            if attempt < self.max_retries:
                backoff = min(
                    self.backoff_base * (2 ** attempt) + random.uniform(0, 1),
                    self.backoff_max,
                )
                logger.warning(
                    "Retry %d/%d para %s apos %.1fs: %s",
                    retries, self.max_retries, tool_name, backoff, last_error,
                )
                time.sleep(backoff)

        # ── Todas as tentativas falharam ──────────────────────────
        duration_ms = (time.time() - start_time) * 1000
        self.stats.total_calls += 1
        self.stats.total_failures += 1
        self.stats.total_retries += retries
        self.stats.last_call_at = time.time()
        self._record_call(tool_name, False, retries, 0.0)

        return CallResult(
            ok=False,
            error=f"Falhou apos {retries} tentativas: {last_error}",
            cost=0.0,
            retries=retries,
            duration_ms=round(duration_ms, 1),
            idempotency_key=idempotency_key,
        )

    # ── Helpers ──────────────────────────────────────────────────

    def _make_idempotency_key(self, tool_name: str, url: str, payload: dict) -> str:
        """Gera chave de idempotencia baseada no conteudo da chamada."""
        raw = f"{tool_name}:{url}:{json.dumps(payload, sort_keys=True, ensure_ascii=False)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _record_call(self, tool_name: str, success: bool, retries: int, cost: float):
        """Registra chamada no historico (ultimas 100)."""
        self.stats.calls.append({
            "tool": tool_name,
            "success": success,
            "retries": retries,
            "cost": cost,
            "timestamp": time.time(),
        })
        if len(self.stats.calls) > 100:
            self.stats.calls = self.stats.calls[-100:]

    def get_stats(self) -> dict:
        """Retorna estatisticas atuais do cliente."""
        s = self.stats
        return {
            "total_calls": s.total_calls,
            "success": s.total_success,
            "failures": s.total_failures,
            "success_rate": round(s.total_success / max(s.total_calls, 1), 3),
            "total_cost_usd": round(s.total_cost, 4),
            "total_retries": s.total_retries,
            "last_call_at": s.last_call_at,
        }

    def reset(self):
        """Reseta estatisticas e cache."""
        self.stats = ClientStats()
        self._idempotency_cache.clear()


# ── Instancia global ─────────────────────────────────────────────────

_client: ExternalApiClient | None = None


def get_client() -> ExternalApiClient:
    """Retorna instancia global do cliente HTTP (lazy init)."""
    global _client
    if _client is None:
        _client = ExternalApiClient()
    return _client