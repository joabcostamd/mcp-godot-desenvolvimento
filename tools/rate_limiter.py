"""rate_limiter — Controle de taxa de chamadas ao MCP server.

Onda 6: Protege contra loops infinitos da IA e uso excessivo.
Implementa sliding window simples em memória (não requer Redis/DB).
"""

import time
from collections import deque
from typing import Optional

# ── Configuração ────────────────────────────────────────────────────

DEFAULT_MAX_REQUESTS = 100   # máximo de requisições por janela
DEFAULT_WINDOW_SECONDS = 60  # janela de 1 minuto
DEFAULT_COOLDOWN_SECONDS = 30  # cooldown após exceder limite


class RateLimiter:
    """Rate limiter com sliding window.

    Uso:
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        allowed, info = limiter.check()
        if not allowed:
            return {"status": "error", "retry_after": info["retry_after"]}
    """

    def __init__(
        self,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cooldown_seconds = cooldown_seconds
        self._timestamps: deque = deque()
        self._blocked_until: float = 0.0

    def check(self) -> tuple[bool, dict]:
        """Verifica se uma requisição é permitida.

        Returns:
            (allowed: bool, info: dict)
        """
        now = time.time()

        # ── Cooldown pós-bloqueio ───────────────────────────────
        if now < self._blocked_until:
            return False, {
                "retry_after": round(self._blocked_until - now, 1),
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "status": "rate_limited",
            }

        # ── Remove timestamps antigos ───────────────────────────
        cutoff = now - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

        # ── Verifica limite ─────────────────────────────────────
        if len(self._timestamps) >= self.max_requests:
            self._blocked_until = now + self.cooldown_seconds
            return False, {
                "retry_after": self.cooldown_seconds,
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "status": "rate_limited",
            }

        # ── Permite ─────────────────────────────────────────────
        self._timestamps.append(now)
        return True, {
            "remaining": self.max_requests - len(self._timestamps),
            "limit": self.max_requests,
            "window_seconds": self.window_seconds,
        }


# ── Instância global ────────────────────────────────────────────────

_limiter: Optional[RateLimiter] = None


def get_limiter() -> RateLimiter:
    """Retorna a instância global do rate limiter (lazy init)."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter


def check_rate_limit() -> tuple[bool, dict]:
    """Verifica rate limit global. Conveniência para server.py."""
    return get_limiter().check()
