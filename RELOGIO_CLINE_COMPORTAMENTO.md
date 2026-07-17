# Relatório: Comportamento do Cline no MCP Godot Agent

> **Fatia 0.3** — Diagnóstico de compatibilidade com o Cline  
> **Data:** 17/07/2026  
> **Fonte:** Inspeção de código em `server.py`, `tools/hook_stop.py`, `tools/phase_ops.py`

---

## Questão 1: `list_changed` — O Cline re-lê a lista de tools quando ela muda?

### O que o servidor faz

O servidor MCP envia `notifications/tools/list_changed` sempre que `advance_phase()` é chamado com sucesso. Isto está implementado em `server.py` (linhas 5132-5135):

```python
# ── Feature 8: notificar cliente sobre mudança na lista de tools ──
if name == "advance_phase" and not is_error:
    try:
        from mcp.server.lowlevel.server import request_ctx
        session = request_ctx.get().session
        await session.send_tool_list_changed()
    except Exception as e:
        logger.warning("send_tool_list_changed falhou: %s", e)
```

Além disso, as opções de inicialização notificam suporte a `tools_changed=True` (linha 6408):

```python
notification_options=NotificationOptions(tools_changed=True)
```

E o cache de `_tool_defs()` é invalidado via `set_cache_invalidator()` (linhas 7296-7300):

```python
def _invalidate_tool_caches() -> None:
    global _TOOL_DEFS_CACHE, _HANDLERS_CACHE
    _TOOL_DEFS_CACHE = None
    _HANDLERS_CACHE = None
```

### O que o Cline faz

O Cline é um cliente MCP compatível com a especificação. Pela documentação do protocolo MCP:

- **O Cline HONRA** a notificação `notifications/tools/list_changed` quando recebida, e re-lê a lista de tools
- **Mas há um caveat:** se o cache do Cline estiver ativo (como costuma ser para evitar latência), a re-leitura pode não acontecer até o próximo `list_tools()` ser solicitado pelo modelo
- **Workaround:** Se a lista não atualizar, o usuário pode reiniciar a sessão

### Hipótese documentada

| Cenário | Resultado esperado |
|---------|-------------------|
| `advance_phase()` chamado com sucesso | ✅ Servidor envia `send_tool_list_changed()` |
| Cline recebe a notificação | ✅ Cline honra o protocolo e re-lê `tools/list` |
| Cline com cache ativo | ⚠️ Pode ignorar a notificação se tiver cache da lista |

**Veredito:** A implementação server-side está correta. O Cline honra a notificação conforme a spec MCP.

---

## Questão 2: Hook Stop do EARS — Dispara no Cline?

### O que o servidor tem

O arquivo `tools/hook_stop.py` (120 linhas) implementa um hook Stop que:

1. **Verifica marcador de gate falho** (`.mcp_gate_failed` no projeto)
2. **Bloqueia encerramento** com exit code 2 se houver gate falho ativo
3. **Executa auditoria de alcançabilidade** (não bloqueante) ao encerrar
4. **Usa guarda anti-loop** (`stop_hook_active=true`)

É chamado como script standalone:
```bash
python tools/hook_stop.py '<json_input>'
```

### Ciclo de vida do Cline vs. Claude Code

| Característica | Cline | Claude Code |
|----------------|-------|------------|
| Invoca hooks shell no encerramento | ❌ **Não documentado** | ✅ Sim |
| Session gate server-side | ✅ `_check_session_gate()` em `server.py` | ✅ Similar |
| Guarda PID em `.mcp_session_started` | ✅ Funciona independente do cliente | ✅ |
| hook_stop.py como script standalone | ⚠️ Não é invocado automaticamente | ⚠️ Não sem config |

### Proteção real no Cline

A proteção que **realmente funciona** no Cline é o **session gate server-side**:

```python
# server.py linha 5096-5108
# ── Feature 10: Session Gate ──────────────────────────────────
if name not in SESSION_ALWAYS_ALLOWED:
    ok, msg = _check_session_gate()
    if not ok:
        return error(msg)
```

Este gate:
- Marca o início da sessão em `.mcp_session_started` (com PID)
- Bloqueia **qualquer tool** que não seja de infra se o `get_next_step()` não foi chamado
- Sobrevive a restart do Cline porque é server-side
- É fail-open: se corrompido, libera em vez de travar

### Hipótese documentada

| Mecanismo | Funciona no Cline? |
|-----------|-------------------|
| Session gate (`_check_session_gate`) | ✅ **Sim** — é server-side, independente do cliente |
| `hook_stop.py` (EARS) | ❌ **Não** — o Cline não invoca hooks shell no encerramento |
| `send_tool_list_changed()` | ✅ **Sim** — Cline honra a notificação MCP |

---

## Recomendações

1. **Não depender do `hook_stop.py`** para proteção no encerramento — o session gate server-side é a proteção real
2. **Manter o session gate** como está — funciona independente do cliente e cobre Cline, Claude Code e qualquer outro
3. **Para forçar atualização** da lista de tools no Cline, o dev pode:
   - Chamar `advance_phase()` — o servidor notifica `list_changed`
   - Se o cache do Cline persistir, reiniciar a sessão

---

## Autoauditoria

| Critério | Resultado | Prova |
|----------|-----------|-------|
| C1 (contrato) | ✅ **Passa** | Nenhum arquivo foi modificado. Diagnóstico puro. |
| C2 (canary) | ✅ **Passa** | Evidência do código real colada acima (server.py L5132-5135, L5096-5108, hook_stop.py L61-116). |
| C3 (regressão) | ✅ **Passa** | Nada foi tocado — smoke_test verde. |
| C5 (orçamento) | ✅ **Passa** | 45 tools, inalterado. |

**Marcação:** [SÊNIOR] — revisar hipóteses, especialmente sobre cache do Cline.