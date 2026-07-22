"""domains/node/test_node_domain.py"""
import inspect
def test_manifest_valido():
    from domains.node.manifest import MANIFEST; from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest); assert MANIFEST.domain == "node"; assert len(MANIFEST.ops) == 7
def test_ops():
    from domains.node.manifest import MANIFEST
    for op in MANIFEST.ops: assert op.summary; assert op.examples; assert op.schema is not None; assert op.fn and callable(op.fn)
def test_handlers_kw():
    from domains.node import handlers
    for name in handlers.__all__:
        fn = getattr(handlers, name); sig = inspect.signature(fn); params = list(sig.parameters.values())
        if not params or params[0].name == "self": continue
        for p in params: assert p.kind in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL) or p.default is not inspect.Parameter.empty
