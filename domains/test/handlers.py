"""domains/test/handlers.py — Handlers do domínio test (F5.14).

Wrappers keyword-only (*). NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def assert_node_exists(*, scene_path: str, node_path: str, node_type: str | None = None) -> dict:
    """Verifica se um nó existe em uma cena."""
    from tools.playmode_ops import assert_node_exists as _impl
    return _impl(scene_path=scene_path, node_path=node_path, node_type=node_type)


def run_stress_test(
    *, project_path: str = "", spawn_scene_path: str = "", spawn_count: int = 10,
    duration_seconds: int = 5, input_actions: list[str] | None = None,
    random_seed: int = 42, fps_threshold: float = 30.0, sample_interval_ms: int = 500,
) -> dict:
    """Executa teste de stress: spawna entidades, injeta input e coleta métricas."""
    from tools.stress_test_ops import run_stress_test as _impl
    return _impl(project_path=project_path, spawn_scene_path=spawn_scene_path, spawn_count=spawn_count,
                 duration_seconds=duration_seconds, input_actions=input_actions, random_seed=random_seed,
                 fps_threshold=fps_threshold, sample_interval_ms=sample_interval_ms)


def test_coverage_report(*, args: dict | None = None) -> dict:
    """Relatório de cobertura de testes das tools do MCP."""
    from tools.test_ops import test_coverage_report as _impl
    return _impl(args=args)


def generate_test_cases_from_gdd(*, args: dict | None = None) -> dict:
    """Gera casos de teste a partir do GDD (concept, game_type)."""
    from tools.test_ops import generate_test_cases_from_gdd as _impl
    return _impl(args=args)


def run_canary_queries(*, args: dict | None = None) -> dict:
    """Executa canary queries para detecção precoce de regressão."""
    from tools.test_ops import run_canary_queries as _impl
    return _impl(args=args)


def run_gut_tests(
    *, project_path: str | None = None, test_dir: str = "res://tests",
    godot_path: str | None = None, timeout: int = 60,
) -> dict:
    """Executa testes GUT no projeto Godot."""
    from tools.gut_ops import run_gut_tests as _impl
    return _impl(project_path=project_path, test_dir=test_dir, godot_path=godot_path, timeout=timeout)


def run_scripted_tests(*, args: dict | None = None) -> dict:
    """Executa cenários de teste roteirizados com input sintético."""
    from tools.test_ops import run_scripted_tests as _impl
    return _impl(args=args)


def smoke_test(*, args: dict | None = None) -> dict:
    """Smoke test rápido: valida pipeline core do MCP (não requer Godot)."""
    from tools.test_ops import smoke_test as _impl
    return _impl(args=args)


def regression_test(*, args: dict | None = None) -> dict:
    """Teste de regressão: valida correções dos grupos 1 e 2."""
    from tools.test_ops import regression_test as _impl
    return _impl(args=args)


def run_verification_pipeline(
    *, project_path: str | None = None, godot_path: str | None = None,
    test_scene: str | None = None, gut_test_dir: str = "res://tests",
    headless_frames: int = 30, timeout_compile: int = 30, timeout_headless: int = 60,
    timeout_gut: int = 120, screenshot_dir: str | None = None,
    include_reachability_audit: bool = True, include_code_quality: bool = True,
) -> dict:
    """Pipeline completo de verificação: compila, headless run, GUT, auditoria."""
    from tools.verification_ops import run_verification_pipeline as _impl
    return _impl(project_path=project_path, godot_path=godot_path, test_scene=test_scene,
                 gut_test_dir=gut_test_dir, headless_frames=headless_frames,
                 timeout_compile=timeout_compile, timeout_headless=timeout_headless,
                 timeout_gut=timeout_gut, screenshot_dir=screenshot_dir,
                 include_reachability_audit=include_reachability_audit,
                 include_code_quality=include_code_quality)


__all__ = [
    "assert_node_exists", "run_stress_test", "test_coverage_report",
    "generate_test_cases_from_gdd", "run_canary_queries",
    "run_gut_tests", "run_scripted_tests", "smoke_test",
    "regression_test", "run_verification_pipeline",
]
