"""domains/render/test_render_domain.py — 8 testes obrigatórios do domínio render (F5.7)."""

import pytest
import inspect


def test_manifest_valido():
    """Manifesto passa em registry.annotations."""
    from domains.render.manifest import MANIFEST
    from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest)
    assert MANIFEST.domain == "render"
    assert MANIFEST.tool_name == "render_manage"
    assert len(MANIFEST.ops) == 4


def test_todas_ops_tem_docstring():
    """Toda op tem docstring de primeira linha útil."""
    from domains.render.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.summary, f"Op '{op.name}' sem summary"
        assert len(op.summary) > 5, f"Summary da op '{op.name}' muito curto: {op.summary}"


def test_todas_ops_tem_exemplo():
    """Toda op tem ao menos 1 exemplo."""
    from domains.render.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.examples, f"Op '{op.name}' sem exemplos"
        assert len(op.examples) > 0, f"Op '{op.name}' com exemplos vazios"


def test_todas_ops_tem_schema():
    """Toda op tem schema com campos mínimos."""
    from domains.render.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.schema, f"Op '{op.name}' sem schema"


def test_dispatch_op_valida():
    """Op conhecida executa o handler correto."""
    from domains.render.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.fn is not None, f"Op '{op.name}' sem handler"
        assert callable(op.fn), f"Handler da op '{op.name}' não é callable"


def test_dispatch_op_invalida():
    """Ops desconhecidas não estão no manifesto."""
    from domains.render.manifest import MANIFEST
    op_names = {op.name for op in MANIFEST.ops}
    assert "invalid_op" not in op_names
    assert "" not in op_names


def test_params_faltando():
    """Schema declara required quando necessário."""
    from domains.render.manifest import MANIFEST
    for op in MANIFEST.ops:
        for param_name, param_def in op.schema.items():
            if param_def.get("required"):
                assert param_name in op.schema, f"Param required '{param_name}' não está no schema"


def test_handlers_keyword_only():
    """Handlers aceitam apenas keyword arguments."""
    from domains.render import handlers
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
