"""domains/test/manifest.py — Manifesto do domínio test (F5.14)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="test",
    tool_name="test_manage",
    title="Gerenciar Testes",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia testes: assert_node, stress_test, coverage_report, generate_test_cases, canary, "
        "GUT, scripted tests, smoke, regression e verification pipeline.\n"
        "QUANDO USAR: para validar cenas, rodar suites de teste, verificar regressões e cobertura.\n"
        "QUANDO NÃO USAR: para debug interativo (use debug_manage), para compilar (use runtime_manage).\n"
        "PRÉ-CONDIÇÕES: para GUT e verification_pipeline, Godot deve estar instalado.\n"
        "ERRO COMUM: GUT não instalado — instale o addon GUT no projeto antes de rodar run_gut_tests."
    ),
    phases=[Phase.POLIMENTO],
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    ops=[
        OpSpec(name="assert_node", fn=handlers.assert_node_exists, summary="Verifica se um nó existe em uma cena",
               schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "node_type": {"type": "string", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "node_path": "./Player"}], rollback=None),
        OpSpec(name="stress_test", fn=handlers.run_stress_test, summary="Teste de stress: spawna entidades e coleta métricas",
               schema={"project_path": {"type": "string", "required": False}, "spawn_scene_path": {"type": "string", "required": False}, "spawn_count": {"type": "integer", "required": False}},
               examples=[{"spawn_count": 100, "duration_seconds": 5}], rollback=None),
        OpSpec(name="coverage_report", fn=handlers.test_coverage_report, summary="Relatório de cobertura de testes das tools",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="generate_test_cases", fn=handlers.generate_test_cases_from_gdd, summary="Gera casos de teste a partir do GDD",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="canary", fn=handlers.run_canary_queries, summary="Executa canary queries para detecção precoce de regressão",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="gut", fn=handlers.run_gut_tests, summary="Executa testes GUT no projeto Godot",
               schema={"project_path": {"type": "string", "required": False}, "test_dir": {"type": "string", "required": False}, "timeout": {"type": "integer", "required": False}},
               examples=[{"test_dir": "res://tests", "timeout": 60}], rollback=None),
        OpSpec(name="scripted", fn=handlers.run_scripted_tests, summary="Executa cenários de teste roteirizados",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="smoke", fn=handlers.smoke_test, summary="Smoke test rápido (não requer Godot)",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="regression", fn=handlers.regression_test, summary="Teste de regressão dos grupos 1 e 2",
               schema={"args": {"type": "object", "required": False}}, examples=[{}], rollback=None),
        OpSpec(name="verify_pipeline", fn=handlers.run_verification_pipeline, summary="Pipeline completo: compila, headless, GUT, auditoria",
               schema={"project_path": {"type": "string", "required": False}, "timeout_compile": {"type": "integer", "required": False}, "timeout_gut": {"type": "integer", "required": False}},
               examples=[{"timeout_compile": 30, "timeout_gut": 120}], rollback=None),
    ],
    tags=["teste", "assert", "stress", "GUT", "verificação"],
)
