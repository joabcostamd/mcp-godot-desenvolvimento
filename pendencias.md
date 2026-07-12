# PENDÊNCIAS — mcp-godot-desenvolvimento

> Última atualização: 2026-07-12 (sessão de implementação do run_verification_pipeline)

---

## Bugs ativos

| ID | Descrição | Severidade | Status |
|----|-----------|-----------|--------|
| BUG-V01 | `movie_path` variável não utilizada em `_step_screenshot` (linha 288) | 🟢 Baixa | ✅ Resolvido |
| BUG-V02 | `_step_headless_run` timeout não captura partial output | 🟡 Média | ✅ Resolvido |
| BUG-V03 | `_step_screenshot` sem `--headless` abre janela visível em Linux/Mac (SW_HIDE só funciona no Windows) | 🟢 Baixa | ✅ Documentado |
| BUG-V04 | `final_path = final_path` self-assignment morto em `_step_screenshot` (linha 377) | 🟢 Baixa | ✅ Resolvido |
| BUG-V05 | `_step_gut` modifica dict retornado por `run_gut_tests` (linha 428) | 🟢 Baixa | ✅ Resolvido |
| BUG-V06 | Variável `gut_failed` declarada mas nunca usada no relatório final (linha ~467) | 🟢 Baixa | ✅ Resolvido |

## Bugs conhecidos (anteriores)

| ID | Descrição | Severidade | Status |
|----|-----------|-----------|--------|
| B1 | `_parse_tscn_node_refs` regex `\d+` não captura IDs alfanuméricos | 🟢 Baixa | Documentado |
| BYPASS-1 | Sandbox: concatenação via variáveis (impossível com regex) | 🟡 Média | Documentado |
| BYPASS-5 | Sandbox: aliasing — `var f = FileAccess` (impossível com regex) | 🟡 Média | Documentado |
| R12 | `godot --headless --script` e `--check-only` não funcionam no Windows 4.7 | 🔴 Crítica | Documentado + workaround |

---

## Resolvidos nesta sessão

| ID | Solução |
|----|---------|
| BUG-V01 | Removida declaração `movie_path = str(movie_prefix)` não utilizada |
| BUG-V02 | Timeout agora captura `e.stdout`/`e.stderr` parcial (Python 3.11+ `TimeoutExpired`) |
| BUG-V03 | Documentada limitação: `startupinfo` só existe no Windows; MCP é primariamente Windows |
| BUG-V04 | Removido `final_path = final_path` (self-assignment) e branch `else: final_path = last_frame` redundante |
| BUG-V05 | `_step_gut` agora faz `result = dict(result)` antes de adicionar `duration_ms` |
| BUG-V06 | Removida variável `gut_failed` não utilizada; lógica equivalente via `gut_has_failures` |
