# Regras de Processo — mcp-godot-desenvolvimento

> Regras fixas de processo. Aplicam-se a TODAS as sessões.
> Não modificar sem aprovação explícita do usuário.

---

## 1. Escopo de trabalho

- Uma feature de cada vez. Nunca múltiplos blocos grandes simultaneamente.
- Não pular fases: IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR.
- Toda mudança estrutural (nova ferramenta, refatoração) requer `advance_phase()` ou `get_next_step()` primeiro.

## 2. Entrega de código

- Toda entrega precisa de:
  - **Diff real:** `git diff --no-color` (com @@ linhas e contexto mínimo de 3 linhas).
  - **Código real colado:** nunca "Read lines X-Y" — cole o trecho relevante completo.
  - **Teste com output real:** rode o comando, cole stdout/stderr completo.

## 3. Alegações de bugs

- "Bug pré-existente", "sem relação", "já estava quebrado" — **exigem prova** via:
  - `git blame <arquivo>` no trecho acusado.
  - `git log -p -- <arquivo>` para mostrar quando foi introduzido.
- Sem prova, a alegação é ignorada e o bug é tratado como causado pela mudança atual.

## 4. Regressão

- Toda mudança que **toca código de feature já aprovada** (Fase 1, Features 1-10) exige:
  - Reteste da funcionalidade afetada.
  - Confirmação explícita no resultado: "Regressão testada: [feature] — OK".

## 5. Decisões aprovadas

- Nunca reverter decisão já aprovada pelo usuário sem avisar e justificar.
- "Já aprovado" inclui: arquitetura, fase, feature completa, política de segurança, escolha de nome/path.

## 6. Estado por projeto

- Estado por projeto em `<project_root>/.mcp_<nome>_state.json`, nunca em config global.
- Exemplos: `.mcp_phase_state.json`, `.mcp_session_started`, `.safety_policy.json`.

## 7. Nova ferramenta no server.py

- `Tool()` em `_tool_defs()` + handler em `_build_handlers()`.
- Se a ferramenta for um rollup (manage tool), usar factory `create_manage_tool()` de `_meta_tool.py`.

## 8. Session Gate

- `get_next_step()` obrigatório no início de toda sessão — libera o gate em `call_tool()`.
- Tools de infra/setup/safety (`SESSION_ALWAYS_ALLOWED`) funcionam sem gate.

## 9. Documentação

- `CONTEXTO_PROJETO_MCP_GODOT.md` atualizado ao final de cada sessão.
- `SESSION_SUMMARY_YYYY-MM-DD.md` gerado ao final de cada sessão, com resumo do que foi feito.

## 10. Formato de resposta final

- Toda resposta final (attempt_completion) deve ser um **único bloco de texto consolidado** contendo tudo que foi feito, resultados reais colados, e diffs.
- Nunca fragmentar o relatório final em múltiplas chamadas de ferramenta.
- Rode todas as ferramentas necessárias primeiro, e só então escreva o resumo final em um bloco só.
