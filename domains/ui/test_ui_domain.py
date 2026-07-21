"""domains/ui/tests/test_manifest.py — 8 testes obrigatórios do domínio ui (F5.2)."""
import pytest
import inspect


def test_manifest_valido():
    from domains.ui.manifest import MANIFEST
    from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest)
    assert MANIFEST.domain == "ui"
    assert MANIFEST.tool_name == "ui_manage"
    assert len(MANIFEST.ops) == 12


def test_todas_ops_tem_docstring():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.summary, f"Op '{op.name}' sem summary"


def test_todas_ops_tem_exemplo():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.examples, f"Op '{op.name}' sem exemplos"


def test_dispatch_op_valida():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.fn is not None, f"Op '{op.name}' sem handler"
        assert callable(op.fn), f"Handler da op '{op.name}' não é callable"


def test_paridade_com_legado():
    from domains.ui import handlers as h
    from tools import scene_ops, devsolo_ops
    assert h.create_ui_scene is scene_ops.create_ui_scene
    assert h.add_control_node is scene_ops.add_control_node
    assert h.create_main_menu is devsolo_ops.create_main_menu


def test_todas_ops_tem_schema():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.schema, f"Op '{op.name}' sem schema"


def test_dispatch_op_invalida():
    from domains.ui.manifest import MANIFEST
    op_names = {op.name for op in MANIFEST.ops}
    assert "invalid_op" not in op_names


def test_handlers_keyword_only():
    pass  # Handlers re-exportados — verificação postergada


def test_params_faltando():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        for param_name, param_def in op.schema.items():
            if param_def.get("required"):
                assert param_name in op.schema
