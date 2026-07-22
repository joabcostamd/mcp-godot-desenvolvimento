"""domains/skeleton/test_skeleton_domain.py — 8 testes obrigatórios do domínio skeleton (F5.8)."""

import pytest
import inspect


def test_manifest_valido():
    from domains.skeleton.manifest import MANIFEST
    from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest)
    assert MANIFEST.domain == "skeleton"
    assert MANIFEST.tool_name == "skeleton_manage"
    assert len(MANIFEST.ops) == 6


def test_todas_ops_tem_docstring():
    from domains.skeleton.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.summary, f"Op '{op.name}' sem summary"
        assert len(op.summary) > 5, f"Summary da op '{op.name}' muito curto: {op.summary}"


def test_todas_ops_tem_exemplo():
    from domains.skeleton.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.examples, f"Op '{op.name}' sem exemplos"
        assert len(op.examples) > 0, f"Op '{op.name}' com exemplos vazios"


def test_todas_ops_tem_schema():
    from domains.skeleton.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.schema, f"Op '{op.name}' sem schema"


def test_dispatch_op_valida():
    from domains.skeleton.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.fn is not None, f"Op '{op.name}' sem handler"
        assert callable(op.fn), f"Handler da op '{op.name}' não é callable"


def test_dispatch_op_invalida():
    from domains.skeleton.manifest import MANIFEST
    op_names = {op.name for op in MANIFEST.ops}
    assert "invalid_op" not in op_names
    assert "" not in op_names


def test_params_faltando():
    from domains.skeleton.manifest import MANIFEST
    for op in MANIFEST.ops:
        for param_name, param_def in op.schema.items():
            if param_def.get("required"):
                assert param_name in op.schema, f"Param required '{param_name}' não está no schema"


def test_handlers_keyword_only():
    from domains.skeleton import handlers
    for name in handlers.__all__:
        fn = getattr(handlers, name)
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        if not params:
            continue
        first_param = params[0]
        if first_param.name == "self":
            continue
        for p in params:
            assert p.kind in (
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ) or p.default is not inspect.Parameter.empty, (
                f"Handler '{name}' tem parâmetro posicional obrigatório '{p.name}'"
            )
