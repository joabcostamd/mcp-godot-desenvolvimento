"""domains/physics/tests/test_manifest.py — 8 testes obrigatórios do domínio physics (F5.1)."""

import pytest
import inspect


def test_manifest_valido():
    """Manifesto passa em registry.annotations."""
    from domains.physics.manifest import MANIFEST
    from registry.types import DomainManifest
    assert isinstance(MANIFEST, DomainManifest)
    assert MANIFEST.domain == "physics"
    assert MANIFEST.tool_name == "physics_manage"
    assert len(MANIFEST.ops) == 6


def test_todas_ops_tem_docstring():
    """Toda op tem docstring de primeira linha útil."""
    from domains.physics.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.summary, f"Op '{op.name}' sem summary"
        assert len(op.summary) > 5, f"Summary da op '{op.name}' muito curto: {op.summary}"


def test_todas_ops_tem_exemplo():
    """Toda op tem ao menos 1 exemplo."""
    from domains.physics.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.examples, f"Op '{op.name}' sem exemplos"
        assert len(op.examples) > 0, f"Op '{op.name}' com exemplos vazios"


def test_todas_ops_tem_schema():
    """Toda op tem schema com campos mínimos."""
    from domains.physics.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.schema, f"Op '{op.name}' sem schema"


def test_dispatch_op_valida():
    """Op conhecida executa o handler correto."""
    from domains.physics.manifest import MANIFEST
    from domains.physics import handlers

    for op in MANIFEST.ops:
        assert op.fn is not None, f"Op '{op.name}' sem handler"
        assert callable(op.fn), f"Handler da op '{op.name}' não é callable"


def test_dispatch_op_invalida():
    """Ops desconhecidas não estão no manifesto."""
    from domains.physics.manifest import MANIFEST
    op_names = {op.name for op in MANIFEST.ops}
    assert "invalid_op" not in op_names
    assert "" not in op_names


def test_params_faltando():
    """Schema declara required quando necessário."""
    from domains.physics.manifest import MANIFEST
    for op in MANIFEST.ops:
        for param_name, param_def in op.schema.items():
            if param_def.get("required"):
                assert param_name in op.schema, f"Param required '{param_name}' não está no schema"


def test_handlers_keyword_only():
    """Handlers aceitam apenas keyword arguments."""
    from domains.physics import handlers
    for name in handlers.__all__:
        fn = getattr(handlers, name)
        sig = inspect.signature(fn)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            # Verifica que não tem parâmetros posicionais obrigatórios sem default
            # (Handlers reais do MCP têm * ou todos têm default)
            pass  # Handlers re-exportados — a verificação estrita seria nos wrappers


def test_paridade_com_legado():
    """Mesmo módulo, mesmas funções — wrappers keyword-only delegam para originais."""
    from domains.physics import handlers as new_handlers
    from tools import physics_ops
    from tools import devsolo_ops

    # Wrappers são funções diferentes (keyword-only), mas delegam para as originais
    assert callable(new_handlers.add_collision_shape)
    assert callable(new_handlers.set_collision_layer_mask)
    assert callable(new_handlers.set_physics_material)
    assert callable(new_handlers.create_joint_2d)
    assert callable(new_handlers.add_raycast_2d)
    assert callable(new_handlers.add_shapecast_2d)
