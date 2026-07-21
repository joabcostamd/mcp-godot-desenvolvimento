# 🚀 PROMPT MESTRE — Próxima Sessão

> **Copie e cole este bloco inteiro no chat da próxima sessão.**
> **Data:** 2026-07-21 | **Commit:** a742ee2 | **Branch:** main

---

Continue o desenvolvimento do **mcp-godot-desenvolvimento**.

## Estado atual
- **Branch:** main (Agente 1 — Núcleo)
- **Commit:** a742ee2 (push OK para origin/main)
- **F5:** 5 domínios migrados (physics ✅, ui ⚠️, shader ✅, camera ✅, navigation ✅)
- **Testes:** 146/148 passam (2 falhas pré-existentes: test_remix)
- **Tools raw:** 272 | **Rollups:** 37

## ⚠️ Pendência crítica
**F5.2 ui: handlers.py ainda usa re-exports.** Precisa converter 12 funções para
KW-only wrappers (`def fn(*, param: type) -> dict:`). Este é o PRÓXIMO PASSO obrigatório.

## Instruções

1. **LEIA antes de qualquer ação:**
   - `.session/NEXT_SESSION.md`
   - `HANDOFF.md`
   - `MASTER_IMPLEMENTATION_ROADMAP.md` §FASE 5 (receita de migração de domínio)
   - `.github/instructions/aprendizados.instructions.md`

2. **VALIDAR baseline:**
   ```
   .venv\Scripts\python.exe -m pytest tests/ -q
   ```
   Deve retornar 146 passed, 2 failed (test_remix — pré-existente).

3. **CORRIGIR F5.2 ui handlers:**
   - Abrir `domains/ui/handlers.py`
   - Converter cada `from tools import X` em wrapper KW-only:
     ```python
     def create_ui_widget(*, scene_path: str, parent_node_path: str, widget_type: str, widget_name: str = "", properties: dict | None = None) -> dict:
         """Cria widget de UI."""
         from tools.devsolo_ops import create_ui_widget as _impl
         return _impl(scene_path, parent_node_path, widget_type, widget_name, properties)
     ```
   - Fazer isso para TODAS as 12 funções
   - Atualizar `test_ui_domain.py`: trocar `is` por `callable()` no teste de paridade
   - Rodar testes: `pytest domains/ui/ -v`

4. **CONTINUAR com /plan para F5.6** (domínio audio)

5. **NUNCA:**
   - Criar tool de topo nova (use rollup)
   - Usar re-exports em handlers de domínio
   - Commitar sem rodar `auditar.py`
   - Pular a leitura do MASTER_IMPLEMENTATION_ROADMAP

6. **SEMPRE:**
   - Validar com `auditar.py --fatia F5.X` após cada fatia
   - Rodar `pytest tests/ -q` após cada fatia
   - Atualizar `.roadmap_progress.json`
   - Commitar e dar push
   - Atualizar `HANDOFF.md` ao final da sessão
   - Executar protocolo `/encerrar` completo ao final

## Comando rápido para iniciar
```
/plan
```
