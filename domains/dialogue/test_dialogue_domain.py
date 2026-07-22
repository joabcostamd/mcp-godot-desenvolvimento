"""domains/dialogue/test_dialogue_domain.py — 8 testes (F5.19)."""
import pytest, inspect

def test_manifest_valido():
    from domains.dialogue.manifest import MANIFEST; from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest); assert MANIFEST.domain == "dialogue"; assert len(MANIFEST.ops) == 3

def test_todas_ops_tem_docstring():
    from domains.dialogue.manifest import MANIFEST
    for op in MANIFEST.ops: assert op.summary and len(op.summary) > 5

def test_todas_ops_tem_exemplo():
    from domains.dialogue.manifest import MANIFEST
    for op in MANIFEST.ops: assert op.examples and len(op.examples) > 0

def test_todas_ops_tem_schema():
    from domains.dialogue.manifest import MANIFEST
    for op in MANIFEST.ops: assert op.schema is not None

def test_dispatch_op_valida():
    from domains.dialogue.manifest import MANIFEST
    for op in MANIFEST.ops: assert op.fn and callable(op.fn)

def test_dispatch_op_invalida():
    from domains.dialogue.manifest import MANIFEST
    assert "invalid_op" not in {op.name for op in MANIFEST.ops}

def test_params_faltando():
    from domains.dialogue.manifest import MANIFEST
    for op in MANIFEST.ops:
        if not op.schema: continue
        for pn, pd in op.schema.items():
            if isinstance(pd, dict) and pd.get("required"): assert pn in op.schema

def test_handlers_keyword_only():
    from domains.dialogue import handlers
    for name in handlers.__all__:
        fn = getattr(handlers, name); sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        if not params or params[0].name == "self": continue
        for p in params:
            assert p.kind in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL) or p.default is not inspect.Parameter.empty
