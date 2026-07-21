"""config_lock.py — Locks compartilhados para escrita em arquivos de config.

Evita condicao de corrida entre multiplos escritores concorrentes:
- CONFIG_FILE_LOCK: protege config.local.json (config de MAQUINA)
- VIBE_STATE_LOCK: protege .mcp_vibe_state.json (estado vibe POR PROJETO)
- BRIEF_STATE_LOCK: protege .mcp_project_brief.json (project brief POR PROJETO)
"""

import threading

CONFIG_FILE_LOCK = threading.Lock()
VIBE_STATE_LOCK = threading.Lock()
BRIEF_STATE_LOCK = threading.Lock()
VERSION_HISTORY_LOCK = threading.Lock()
