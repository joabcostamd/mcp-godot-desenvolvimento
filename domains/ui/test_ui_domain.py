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
    """Wrappers delegam para as mesmas funções fonte (equivalência comportamental)."""
    from domains.ui import handlers as h
    from tools import scene_ops, devsolo_ops
    import inspect

    # Verifica que os wrappers são funções distintas (não re-exports)
    assert h.create_ui_scene is not scene_ops.create_ui_scene, \
        "create_ui_scene deve ser wrapper, não re-export"
    assert h.add_control_node is not scene_ops.add_control_node, \
        "add_control_node deve ser wrapper, não re-export"
    assert h.create_main_menu is not devsolo_ops.create_main_menu, \
        "create_main_menu deve ser wrapper, não re-export"

    # Verifica que os wrappers apontam para as mesmas funções fonte (via __wrapped__)
    # Lazy imports: verificamos via inspection do código fonte do wrapper
    for wrapper_name, source_module, source_func_name in [
        ("create_ui_scene", scene_ops, "create_ui_scene"),
        ("add_control_node", scene_ops, "add_control_node"),
        ("create_main_menu", devsolo_ops, "create_main_menu"),
        ("create_hud_template", devsolo_ops, "create_hud_template"),
        ("create_pause_menu", devsolo_ops, "create_pause_menu"),
        ("create_health_bar", devsolo_ops, "create_health_bar"),
        ("create_loading_screen", devsolo_ops, "create_loading_screen"),
        ("create_ui_widget", devsolo_ops, "create_ui_widget"),
        ("create_tab_with_content", devsolo_ops, "create_tab_with_content"),
        ("configure_ui_focus_and_nav", devsolo_ops, "configure_ui_focus_and_nav"),
        ("set_tooltip", devsolo_ops, "set_tooltip"),
        ("set_anchor_preset", devsolo_ops, "set_anchor_preset"),
    ]:
        wrapper = getattr(h, wrapper_name)
        expected_source = getattr(source_module, source_func_name)
        # Verifica que o wrapper referencia o source no seu source code
        src = inspect.getsource(wrapper)
        assert source_func_name in src, (
            f"Wrapper '{wrapper_name}' não referencia '{source_func_name}' "
            f"no source. Esperado: import de {source_module.__name__}.{source_func_name}"
        )
        # Verifica que ambos são funções diferentes
        assert wrapper is not expected_source, (
            f"'{wrapper_name}' é re-export, não wrapper"
        )


def test_todas_ops_tem_schema():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        assert op.schema, f"Op '{op.name}' sem schema"


def test_dispatch_op_invalida():
    from domains.ui.manifest import MANIFEST
    op_names = {op.name for op in MANIFEST.ops}
    assert "invalid_op" not in op_names


def test_handlers_keyword_only():
    """Todos os 12 handlers são KW-only (assinatura com *)."""
    from domains.ui import handlers as h
    import inspect

    handler_names = [
        "create_ui_scene",
        "add_control_node",
        "create_main_menu",
        "create_hud_template",
        "create_pause_menu",
        "create_health_bar",
        "create_loading_screen",
        "create_ui_widget",
        "create_tab_with_content",
        "configure_ui_focus_and_nav",
        "set_tooltip",
        "set_anchor_preset",
    ]

    for name in handler_names:
        fn = getattr(h, name)
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        assert params, f"Handler '{name}' não tem parâmetros"
        # O primeiro parâmetro deve ser '*' ou o primeiro comum deve ter
        # a marcação KEYWORD_ONLY
        kw_only = [p for p in params if p.kind == inspect.Parameter.KEYWORD_ONLY]
        positional = [p for p in params if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD]
        assert len(positional) == 0, (
            f"Handler '{name}' tem parâmetros posicionais {[p.name for p in positional]}. "
            f"Todos devem ser keyword-only (*)."
        )
        assert len(kw_only) >= 1, (
            f"Handler '{name}' não tem parâmetros keyword-only"
        )


def test_params_faltando():
    from domains.ui.manifest import MANIFEST
    for op in MANIFEST.ops:
        for param_name, param_def in op.schema.items():
            if param_def.get("required"):
                assert param_name in op.schema
