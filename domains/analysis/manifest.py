"""domains/analysis/manifest.py — F5.25."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="analysis", tool_name="analysis_manage", title="Análise", namespace="project", version="1.0.0",
    description="Analisa o projeto: estrutura, próximos passos, referências, design, escopo e busca.\nQUANDO USAR: para diagnóstico e planejamento.\nQUANDO NÃO USAR: para testes (use test_manage).",
    phases=[Phase.DESIGN, Phase.PROTOTIPO], annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    ops=[OpSpec("structure", handlers.analyze_game_structure, "Analisa estrutura", {}, [{}]),
         OpSpec("next_steps", handlers.suggest_next_steps, "Sugere próximos passos", {}, [{}]),
         OpSpec("missing_refs", handlers.find_missing_references, "Encontra refs faltantes", {}, [{}]),
         OpSpec("validate_design", handlers.validate_game_design, "Valida design", {}, [{}]),
         OpSpec("estimate_scope", handlers.estimate_game_scope, "Estima escopo", {}, [{}]),
         OpSpec("search", handlers.search_codebase, "Busca no código", {"query": {"type": "string", "required": False}}, [{"query": "player"}]),
         OpSpec("history", handlers.get_project_history, "Histórico do projeto", {}, [{}])],
    tags=["análise", "diagnóstico", "métricas"])
