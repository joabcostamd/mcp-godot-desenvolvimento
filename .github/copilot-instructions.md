
# Instruções do projeto — MCP Godot Agent

> **Local correto:** `.github/copilot-instructions.md`
> O VS Code aplica este arquivo automaticamente a todas as requisições de chat
> deste workspace. Mantenha-o curto: regra que não cabe aqui vai para
> `.github/instructions/`.

---

## 1. O QUE É ESTE PROJETO

Um servidor MCP em Python que é o **dono do processo** de desenvolvimento de um jogo
Godot inteiro — da ideia ao lançamento. Não é só uma ponte entre IA e engine: tem
travas reais (fase, verificação, export, sessão) que impedem pular etapa.

O projeto que você edita é o **próprio MCP**, não um jogo.

Estado: Godot 4.7, ~285 `Tool()` em `server.py`, máquina de estados de 6 fases
(IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR),
Saga Engine, proof ledger, `auditar.py` como portão fail-closed.
249 behaviors plugáveis, Editor Visual de BT, 4 jogos-exemplo, 5 templates.

Objetivo final: um não-programador, usando linguagem natural, começa, desenvolve
e **termina** um jogo indie.

---

## 2. LEIA NESTA ORDEM, SEMPRE

1. `AGENTS.md` — descubra qual agente você é e qual é o seu território
2. `ROADMAP_DEFINITIVO.md` — a ordem das ondas e fatias
3. `.github/roadmap/ONDA_*.md` — a ficha da fatia atual
4. `.github/instructions/aprendizados.instructions.md` — o que já quebrou antes
5. `.github/instructions/fontes.instructions.md` — onde pesquisar antes de escrever

---

## 3. AS 5 REGRAS ABSOLUTAS

**1. Uma fatia por vez.** Nunca comece N+1 antes de N estar 100% fechada e aprovada
pelo humano.

**2. Você não decide que está bom.** "Bom" é teste que passa ou falha, nunca a sua
opinião. Se um critério não vira teste de passa/falha, ele não é auto-avaliável —
escale para o humano.

**3. Prova sempre, nunca alegação.**
- `git diff --no-color` literal, com marcadores `@@` — nunca resumo ou tabela
- Código real colado em bloco — nunca "Read lines X to Y" (isso é log de ferramenta)
- Output de teste completo — nunca "passou!" sozinho
- "É bug pré-existente" / "sem relação com a fatia" exige `git blame` ou `git log -p`
  com output colado

**4. Nunca commite sozinha.** Proponha o commit com a mensagem sugerida e pare.

**5. Checkpoint antes de qualquer operação destrutiva.** Git é a rede de segurança real.

Se não tiver certeza se pode prosseguir: **pare e escale.** O custo de parar é baixo.
O custo de prosseguir errado com confiança é alto.

---

## 4. CONSULTE A FONTE ANTES DE IMPLEMENTAR

Antes de escrever código de uma feature, leia a fonte correspondente em
`.github/instructions/fontes.instructions.md` e **cite qual usou** no relatório.
Sem fonte citada, a fatia não fecha.

Motivo: a causa raiz da maioria dos erros neste projeto é a IA inventar API do Godot
que não existe (regra R9 dos aprendizados).

---

## 5. TETO DE FERRAMENTAS (nunca violar)

A precisão de escolha de tool despenca acima de 30–50 tools visíveis.

- **Rollup-first é lei.** Feature nova entra como `op` dentro de um rollup
  (`nome_manage` com parâmetro `op`), nunca como tool de topo. Exceção só com
  justificativa registrada e aprovada.
- Rollup se cria com a factory `create_manage_tool()` de `_meta_tool.py`.
  Não invente outro padrão.
- Registro: `Tool(name=..., description=..., inputSchema=...)` em `_tool_defs()`
  **e** handler correspondente em `_build_handlers()`.
- Teto: ~40 tools visíveis por fase, ~70 tools de topo no total.
- **Distinguibilidade:** nome ou descrição que se confunda com tool existente
  é falha automática. Tool ambígua degrada a escolha mais que tool a mais.
- Descrição e schema enxutos. Descrição inchada custa token em toda requisição
  e piora a escolha.

---

## 6. PADRÕES TÉCNICOS DO REPOSITÓRIO (fatos, não sugestões)

- Estado por projeto vive em `<project_root>/.mcp_<nome>_state.json`,
  **nunca** em config global do MCP.
- Escrita concorrente em arquivo compartilhado exige lock via `tools/config_lock.py`.
- Subprocess sempre por `tools/subprocess_utils.py::run_subprocess_safe()`,
  com `stdin=DEVNULL` (evita deadlock no Windows).
- Rede sempre em `127.0.0.1`. Bind em `0.0.0.0` é falha automática.
- **Visibilidade de tool ≠ bloqueio de execução.** `_tool_defs()` é filtrado por fase;
  `_build_handlers()` não é. Tool escondida ainda pode ser chamada. Não confunda
  curadoria com trava real ao avaliar se um gate é de verdade.
- Provas por `capture_proof` / `verify_proof`, rodadas **antes** do commit
  (`git_diff` fica vazio depois do commit).

---

## 7. AMBIENTE (Windows)

- PowerShell antigo não aceita `&&`. Use `;` ou `cmd /c "a && b"`.
- `git commit` / `git log` com saída grande sem feedback trava a sessão.
  Use `--oneline`, `-n`, ou redirecione.
- Falhas de rede devem ser simuladas por mock, nunca esperando timeout real.
- `godot --headless --script` e `--check-only` não funcionam no Windows com 4.7
  (regra R12). Use os workarounds documentados nos aprendizados.
- Nomes de arquivo e projeto: sem acento e sem espaço nos caminhos.

---

## 8. FLUXO

`/plan` → planejo e paro · humano aprova · `/act` → implemento uma fatia, provo,
proponho commit e paro · humano aprova · `/handoff` → escrevo o resumo.

Nunca pule `/plan`. Nunca faça duas fatias no mesmo `/act`.

---

## 9. LINGUAGEM

Responda ao humano em **português, linguagem simples e direta**. Sem jargão
desnecessário, sem preâmbulo, sem elogio, sem resumo redundante. Comando pedido
é comando entregue — sem explicação em volta.

