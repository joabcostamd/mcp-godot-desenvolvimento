"""experimental/ — Verticais em quarentena.

Capacidades construídas antes da demanda real (violação de P9).
NENHUMA ferramenta aqui aparece no wire em qualquer fase com --profile standard.

Critério de saída da quarentena (para cada vertical):
    Um jogo real precisou da capacidade e ela foi exercitada
    pelo teste que fecha a fase correspondente do projeto.

Para acessar durante debug: --profile full
"""

VERTICAIS = {
    "telemetry": {
        "tools": ["telemetry_track_event", "telemetry_get_funnel",
                   "telemetry_session_summary", "telemetry_heatmap"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "POLIMENTO",
    },
    "accessibility": {
        "tools": ["accessibility_add_subtitles", "accessibility_apply_colorblind_filter",
                   "accessibility_remap_controls", "accessibility_audit_scene",
                   "accessibility_certification_checklist"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "POLIMENTO",
    },
    "onboarding": {
        "tools": ["onboarding_create_tutorial_step", "onboarding_create_guided_tour",
                   "onboarding_check_first_experience"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "CONTEUDO",
    },
    "cutscene": {
        "tools": ["cutscene_create_timeline", "cutscene_add_camera_shot",
                   "cutscene_add_dialogue_event"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "CONTEUDO",
    },
    "quest": {
        "tools": ["quest_generate"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "CONTEUDO",
    },
    "mods": {
        "tools": ["mod_manifest_generate", "validate_mod_compatibility"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "PRONTO_PARA_LANCAR",
    },
    "trailer_store": {
        "tools": ["trailer_capture_clip", "trailer_render_sequence",
                   "capsule_generate_store_image"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "PRONTO_PARA_LANCAR",
    },
    "achievements": {
        "tools": ["create_achievement_system", "validate_achievement_config"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "CONTEUDO",
    },
    "cloud": {
        "tools": ["cloud_save_configure"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "PRONTO_PARA_LANCAR",
    },
    "difficulty": {
        "tools": ["adaptive_difficulty_adjust"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "POLIMENTO",
    },
    "remote_balance": {
        "tools": ["remote_balance_config"],
        "status": "nunca exercitada por jogo real",
        "fase_alvo": "POLIMENTO",
    },
}
