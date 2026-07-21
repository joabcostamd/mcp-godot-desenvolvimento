"""registry/types.py — Tipos fundamentais do registry (Fase 1.1).

Define DomainManifest e OpSpec como fonte única de verdade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class Phase(str, Enum):
    """Fases do ciclo de vida do projeto de jogo."""
    IDEIA = "IDEIA"
    DESIGN = "DESIGN"
    PROTOTIPO = "PROTOTIPO"
    CONTEUDO = "CONTEUDO"
    POLIMENTO = "POLIMENTO"
    PRONTO_PARA_LANCAR = "PRONTO_PARA_LANCAR"


@dataclass
class OpSpec:
    """Especificação de uma operação dentro de um domínio.

    Fonte única de verdade para: nome, handler, schema, exemplos e anotações.
    """
    name: str
    fn: Callable[..., dict]
    summary: str
    schema: dict[str, Any] = field(default_factory=dict)
    examples: list[dict] = field(default_factory=list)
    annotations: dict[str, bool] = field(default_factory=dict)
    deprecated_since: str | None = None
    replaced_by: str | None = None
    rollback: str | None = None


@dataclass
class DomainManifest:
    """Manifesto de um domínio — fonte única de verdade.

    Um domínio agrupa >= 3 operações coesas que compartilham pré-condições.
    Declarado em domains/<x>/manifest.py.
    """
    # ── Identidade ──
    domain: str
    tool_name: str
    title: str = ""
    namespace: str = "project"
    version: str = "1.0.0"
    aliases: list[str] = field(default_factory=list)

    # ── Descrição ──
    description: str = ""

    # ── Curadoria ──
    phases: list[Phase] = field(default_factory=list)
    always_visible: bool = False
    internal: bool = False
    named_justification: str | None = None

    # ── Anotações MCP ──
    annotations: dict[str, bool] = field(default_factory=lambda: {
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    })

    # ── Operações ──
    ops: list[OpSpec] = field(default_factory=list)

    # ── Tags (não-MCP, usadas por catalog_search) ──
    tags: list[str] = field(default_factory=list)
