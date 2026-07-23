# ONDA R — RECONCILIAÇÃO

> **Portão duro.** Nenhuma outra onda começa antes desta fechar.
> Todas as fatias são `[EIXO-CENTRAL]` — um agente só, sequencial.
> Ordem estrita: R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8.
>
> **Regra herdada, sem exceção:** `concluida` só com a saída do campo 8 colada.
> Sem saída, o status é `nao verificado`. Nunca fingir verificação.

---

## Fatia R1 — Gate git real

**1. O que é**
Instalar uma trava que dispara de verdade neste ambiente: git hook em `.githooks/`,
ativado por `core.hooksPath`, porque os hooks `PreToolUse` do VS Code não disparam com
a extensão DeepSeek v0.6.2 (regra R20).

**2. Por que agora**
É a primeira fatia porque tudo depois dela depende de existir uma trava mecânica. Sem
isso, "automação total" significa a IA se auto-aprovando — exatamente o padrão que o
`PROTOCOLO_AUTOGOVERNANCA.md` §0 documenta como causa-raiz. A decisão DR-1 amarra o
commit automático a esta fatia estar fechada.

**3. Arquivos que toca**
```
.githooks/pre-commit          (novo)
scripts/gate_reorg.py         (novo)
.reorg_baseline.json          (novo, gerado)
tests/test_gate_reorg.py      (novo)
```
Não toca `server.py`. Não toca `auditar.py` (isso é a R3).

**4. Fonte obrigatória de consulta**
`git help hooks` (seção `core.hooksPath`) e `CONSTITUICAO-SISTEMA-WORKFLOW.md` §5.5 e §5.7
(contrato de hook e a regra do escape hatch `--no-verify`).

**5. Como fazer**
1. `git config core.hooksPath .githooks`
2. `.githooks/pre-commit` é um `sh` de 3 linhas que chama
   `python scripts/gate_reorg.py --pre-commit` e propaga o exit code.
3. `scripts/gate_reorg.py` verifica, nesta ordem:
   - **G1** — se `.roadmap_progress.json` ganhou entrada nova com `"status": "concluida"`,
     ela precisa ter campo `checkpoint` com hash real (não `"pendente-commit"`).
   - **G2** — se arquivo de roadmap ou `HANDOFF.md` está staged, `.roadmap_progress.json`
     também precisa estar staged (é o `par-obrigatorio.ps1` que hoje não dispara).
   - **G3** — contagem de tools por fase não pode ser **maior** que `.reorg_baseline.json`.
     Igual passa. Menor passa e **atualiza** o baseline.
4. Falha de medição **bloqueia** (fail-closed), com a mensagem dizendo para usar
   `git commit --no-verify` se for consciente. Silêncio nunca é aprovação.
5. `--no-verify` continua funcionando. Isso é intencional (§5.7).

**6. Armadilhas conhecidas**
- Hook precisa de fim de linha LF e sem BOM, senão o Git for Windows não executa.
- `core.hooksPath` é config **local** do repositório: precisa ser reaplicado em cada
  worktree. O worktree `mcp-godot-agente02` compartilha o `.git` comum — confirmar se herda.
- Se `import server` estiver quebrado, a medição falha. É por isso que a regra é bloquear,
  não liberar.
- Não usar `&&` em nenhum script.

**7. Critérios de aceite**
- [ ] `git config core.hooksPath` devolve `.githooks`
- [ ] Commit com entrada `concluida` sem `checkpoint` válido é **BLOQUEADO**
- [ ] Commit legítimo passa
- [ ] `git commit --no-verify` passa mesmo com violação
- [ ] `.reorg_baseline.json` existe com contagem por fase

**8. Como provar**
```powershell
git config core.hooksPath ; python -m pytest tests/test_gate_reorg.py -v 2>&1 | Tee-Object -FilePath prova_R1.txt ; Get-Content prova_R1.txt
```
O teste precisa conter um caso que **falha de propósito** e confirma exit code != 0.
Teste que nunca falhou pode não estar testando nada (lição §6.2 da constituição).

**9. Regressão a retestar**
`$HOME\.copilot\hooks\scripts\autoteste.ps1` continua passando 4/4 (o gate novo não
substitui o antigo, soma-se a ele). Colar a saída.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]` — instala trava de segurança; exige revisão humana.

---

## Fatia R2 — Estado único

**1. O que é**
Fazer valer a regra que já existe: `.roadmap_progress.json` é a única fonte de status.
`.reorg_progress.json` e `.roadmap_progress_a2.json` viram arquivo morto.

**2. Por que agora**
O sinal S4 do `PROTOCOLO_AUTOGOVERNANCA.md` manda **PARAR** quando dois arquivos de estado
divergem. Hoje são três. Enquanto isso não resolver, todo `/plan` pode partir do arquivo errado.

**3. Arquivos que toca**
```
.roadmap_progress.json                     (recebe as entradas herdadas)
journal/estado-antigo/                     (novo, destino)
.reorg_progress.json                       (movido)
.roadmap_progress_a2.json                  (movido)
```

**4. Fonte obrigatória de consulta**
`CONSTITUICAO-SISTEMA-WORKFLOW.md` §5.2 e `PROTOCOLO_AUTOGOVERNANCA.md` §6 (sinal S4).

**5. Como fazer**
1. Backup datado de `.roadmap_progress.json` (convenção §7.3).
2. Ler os outros dois. Para cada chave: se não existir no principal, copiar **prefixada**
   com `arquivado_a2_` ou `arquivado_reorg_`. Nunca sobrescrever entrada existente.
3. Se uma mesma fatia aparecer nos dois com status diferente, **não escolher** — registrar
   as duas e marcar a divergência em `SUTURE_ISSUES.md`. S4 proíbe escolher em silêncio.
4. Mover os dois arquivos para `journal/estado-antigo/`.
5. Adicionar os dois nomes ao `.gitignore` para não voltarem por engano.

**6. Armadilhas conhecidas**
- `.roadmap_progress.json` tem 77 KB e é histórico. **Editar entrada antiga é falsificar.**
  Só adicionar.
- Encoding: o arquivo tem acento corrompido em vários pontos. Ler e escrever em UTF-8
  explícito, sem "consertar" texto de passagem.

**7. Critérios de aceite**
- [ ] Só existe 1 arquivo `*roadmap_progress*.json` na raiz
- [ ] Backup datado existe
- [ ] Nenhuma chave pré-existente foi alterada
- [ ] Divergências (se houver) registradas em `SUTURE_ISSUES.md`

**8. Como provar**
```powershell
Get-ChildItem -Filter "*progress*.json" | Select-Object Name,Length ; Get-ChildItem journal\estado-antigo | Select-Object Name ; python -c "import json;d=json.load(open('.roadmap_progress.json',encoding='utf-8'));print('chaves',len(d))" 2>&1 | Tee-Object -FilePath prova_R2.txt ; Get-Content prova_R2.txt
```

**9. Regressão a retestar**
`/plan` ainda lê o arquivo e lista fatia pendente. Rodar e colar as 5 primeiras linhas.

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]` — verificável por comando.

---

## Fatia R3 — Consertar o auditor

**1. O que é**
Fechar os dois vazamentos do `auditar.py`: a tolerância de 5 tools no C1 (DR-6) e a flag
`--skip-c5` (DR-5).

**2. Por que agora**
`auditar.py` é o portão que todo `/act` roda no PASSO 4. Um portão com vazamento aprova
tudo o que vem depois. `passed = len(added) <= 5` deixou passar 5 tools por fatia sem
alarme; `--skip-c5` desligou o teto dezenas de vezes com uma desculpa fixa citando
`f056aed8`.

**3. Arquivos que toca**
```
auditar.py
.reorg_baseline.json          (lido, criado na R1)
tests/test_auditar_gate.py    (novo)
```

**4. Fonte obrigatória de consulta**
O próprio `auditar.py` (funções `_run_c1` e `_run_c5`) e `PROTOCOLO_AUTOGOVERNANCA.md` §4
(as 3 perguntas antes de aceitar queda de métrica).

**5. Como fazer**
1. `_run_c1`: trocar `len(added) <= 5` por `len(added) == 0`. Adição de tool passa a exigir
   `--justificar-tool "<nome>: <motivo>"`, que fica registrado no `audit_result.json`.
2. `_run_c5`: remover a flag `--skip-c5` e o bloco `pre_existente`. No lugar, comparar com
   `.reorg_baseline.json`: **maior falha, igual passa, menor passa e atualiza o baseline.**
3. Não mexer em C2, C3, C4, C6, C7. Fora de escopo.

**6. Armadilhas conhecidas**
- Remover `--skip-c5` seco trava tudo: 5 de 6 fases estão acima do teto **hoje**. Por isso
  o baseline, não o teto absoluto. Isso é DR-5, não improviso.
- Chamadas antigas com `--skip-c5` passam a dar erro de argumento. Buscar com `findstr` em
  `.md` e `.py` antes de fechar a fatia.
- Não alterar `auditar.py` para fazer nenhuma outra fatia passar — isso é falha automática
  pela regra do `/act`.

**7. Critérios de aceite**
- [ ] `--skip-c5` não existe mais em `auditar.py`
- [ ] C1 com 1 tool nova e sem justificativa → **FAIL**
- [ ] C1 com 1 tool nova e com justificativa → PASS, e a justificativa aparece no JSON
- [ ] C5 acima do baseline → FAIL; igual → PASS; abaixo → PASS e baseline atualizado
- [ ] Nenhum arquivo do repositório ainda chama `--skip-c5`

**8. Como provar**
```powershell
python -m pytest tests/test_auditar_gate.py -v 2>&1 | Tee-Object -FilePath prova_R3.txt ; findstr /S /N /C:"skip-c5" *.py *.md >> prova_R3.txt ; Get-Content prova_R3.txt
```

**9. Regressão a retestar**
`python auditar.py --fatia R3` roda inteiro e grava `audit_result.json` sem exceção.
Colar a saída completa.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]` — mexe no portão de todas as fatias.

---

## Fatia R4 — Caminhos e contradição dos comandos

**1. O que é**
Consertar o que faz `/seguir-roadmap` morrer no primeiro passo, e resolver a contradição
entre ele e o `/act` — pela decisão DR-4, **`/act` vence**.

**2. Por que agora**
`/seguir-roadmap` ETAPA 0 manda ler `docs/ROADMAP_DEFINITIVO.md`; esse arquivo não aparece
na raiz nem em `docs/` (bloco 23 do recon). `/plan` aponta para outro caminho. E o
`/seguir-roadmap` manda marcar ✅ dentro do `.md` (ETAPA 5.16) e commitar sozinho (5.19) —
proibido por §5.2 da constituição e pelo `/act`.

**3. Arquivos que toca**
```
docs/ROADMAP_DEFINITIVO.md         (criado ou reconciliado — aponta para REORG_ROADMAP.md)
ROADMAP_DEFINITIVO.md              (ponteiro de 3 linhas na raiz)
.github/prompts/*.prompt.md        (movidos para journal/prompts-locais/)
%APPDATA%\Code\User\settings.json  (1 chave, com backup datado)
SUTURE_ISSUES.md                   (registra a contradição do /seguir-roadmap)
```
**Não reescreve nenhum dos 6 comandos globais.** A contradição é registrada e o
`/seguir-roadmap` fica **suspenso** até a ONDA 10 — o ciclo usado é `/plan` → `/act`.

**4. Fonte obrigatória de consulta**
`CONSTITUICAO-SISTEMA-WORKFLOW.md` §5.1 (prompts locais eliminados), §9.3.1 (proibição de
recriar) e §3.1.3 (chaves críticas do `settings.json`).

**5. Como fazer**
1. Mover os 4 `.prompt.md` untracked de `.github/prompts/` para `journal/prompts-locais/`.
   Mover, não deletar.
2. Corrigir `chat.instructionsFilesLocations`: hoje aponta para `.github/prompts`
   (pasta de comandos), quando deveria apontar para `.github/instructions` (pasta de
   contexto, que existe e não está sendo carregada). Backup datado antes.
3. Criar `docs/ROADMAP_DEFINITIVO.md` com o conteúdo canônico apontando para
   `REORG_ROADMAP.md`, e um ponteiro de 3 linhas na raiz. Um conteúdo só, dois caminhos
   satisfeitos, zero duplicação.
4. Registrar em `SUTURE_ISSUES.md`: `/seguir-roadmap` contradiz `/act` em 2 pontos;
   suspenso até a ONDA 10.

**6. Armadilhas conhecidas**
- `settings.json` é sincronizado pelo Settings Sync, que **já corrompeu** config deste
  sistema uma vez. Backup datado é obrigatório.
- Não remover `chat.hookFilesLocations` — é a dependência mais perigosa do sistema (§8).
- Recriar prompt local é proibição explícita 9.3.1. Esta fatia **remove**, nunca cria.

**7. Critérios de aceite**
- [ ] `.github/prompts/` sem nenhum `.prompt.md`
- [ ] `chat.instructionsFilesLocations` aponta para `.github/instructions`
- [ ] `chat.hookFilesLocations` intacto
- [ ] Backup do `settings.json` existe
- [ ] `docs/ROADMAP_DEFINITIVO.md` existe e é legível
- [ ] Contradição registrada em `SUTURE_ISSUES.md`

**8. Como provar**
```powershell
Get-ChildItem .github\prompts -ErrorAction SilentlyContinue | Select-Object Name ; Test-Path docs\ROADMAP_DEFINITIVO.md ; python -c "import json,os;p=os.path.expandvars(r'%APPDATA%\Code\User\settings.json');d=json.load(open(p,encoding='utf-8-sig'));print('instructions=',d.get('chat.instructionsFilesLocations'));print('hooks=',d.get('chat.hookFilesLocations'))" 2>&1 | Tee-Object -FilePath prova_R4.txt ; Get-Content prova_R4.txt
```

**9. Regressão a retestar**
Digitar `/` no chat e confirmar que os 6 comandos aparecem **uma vez cada**. Este critério
depende de olho humano — por isso a fatia é `[SÊNIOR]`.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]` — mexe em config global e tem critério não automatizável.

---

## Fatia R5 — Reauditar o que está marcado como concluído

**1. O que é**
Conferir cada fatia marcada `concluida` no `.roadmap_progress.json` contra o critério de
aceite real dela. Corrigir o status onde não bater.

**2. Por que agora**
F5.1 a F5.13 estão `concluida`, mas o critério da F1 exige que `server.py` não contenha
`Tool(`, `TOOLSETS`, `PHASE_TOOLSETS`, `TOOL_PROFILES` — e os quatro estão lá (bloco 29).
F5 depende de F4 → F3 → F2 → F1. Nenhuma fechou. É o mesmo erro da Fatia 0.A, agora em
escala. Este é o `/plan` PASSO N aplicado retroativamente.

**3. Arquivos que toca**
```
.roadmap_progress.json      (só correção de status, nunca de histórico)
SUTURE_ISSUES.md            (registra cada divergência)
RECONCILIACAO_R5.md         (novo — a tabela do que foi reauditado)
```
Nenhum arquivo de código é alterado nesta fatia. É auditoria, não correção.

**4. Fonte obrigatória de consulta**
`MASTER_IMPLEMENTATION_ROADMAP.md` §17 (critérios de aceite originais de F1, F2, F3, F4, F5)
e `PROTOCOLO_AUTOGOVERNANCA.md` §2 (AUTO-CHECKPOINT AC1–AC9).

**5. Como fazer**
Para cada fatia `F1.*`, `F2.*`, `F3.*`, `F4.*`, `F5.*` marcada `concluida`:
1. Ler o critério de aceite no MASTER.
2. **Executar** o comando que o comprova. Não ler código — executar (Nível 1 da §3).
3. Passou → mantém `concluida`. Não passou → muda para `nao verificado` e registra por quê.
4. Nunca mudar para `escalada` sem dizer qual decisão humana falta.
5. Produzir `RECONCILIACAO_R5.md`: uma linha por fatia, com o comando e a saída literal.

**6. Armadilhas conhecidas**
- A tentação vai ser "isso já estava assim antes". Isso é o AC7: exige `git blame` ou
  `git log -p` colado, sempre.
- Rebaixar status parece regressão, mas não é: é a única forma de o `/plan` voltar a
  funcionar. Estado falso é pior que estado ruim.
- Não corrigir código aqui. Cada correção vira fatia da onda correspondente.

**7. Critérios de aceite**
- [ ] Toda fatia F1–F5 `concluida` foi reauditada, com comando e saída
- [ ] `RECONCILIACAO_R5.md` tem uma linha por fatia
- [ ] Toda mudança de status tem motivo escrito
- [ ] Nenhum arquivo de código foi alterado (`git diff --stat` só mostra `.md` e o `.json`)

**8. Como provar**
```powershell
git --no-pager diff --stat 2>&1 | Tee-Object -FilePath prova_R5.txt ; python -c "import json;d=json.load(open('.roadmap_progress.json',encoding='utf-8'));c={};[c.__setitem__(v.get('status','?'),c.get(v.get('status','?'),0)+1) for v in d.values() if isinstance(v,dict)];print(c)" >> prova_R5.txt ; Get-Content prova_R5.txt
```

**9. Regressão a retestar**
`python auditar.py --fatia R5` continua verde depois da mudança de status (mudar status não
pode quebrar o portão). Colar a saída.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]` — rebaixar status aprovado exige decisão humana.

---

## Fatia R6 — Branch do Agente 2

**1. O que é**
Executar a decisão DR-2: preservar `agente2/behaviors-onda2` como arquivo morto, com prova
de que o merge seria destrutivo. **Sem mergear.**

**2. Por que agora**
`git diff --stat main..agente2/behaviors-onda2` deu 7.386 inserções contra **31.705
remoções**. A branch remove `registry/`, os 38 `domains/`, `adapters/transport.py`,
`experimental/`, `scripts/audit_fase.py` e o próprio roadmap. Ela divergiu antes da reorg.
Os 249 behaviors já estão na main. Enquanto essa branch estiver aberta como "pendência de
merge", todo handoff vai continuar propondo mergear.

**3. Arquivos que toca**
```
(nenhum arquivo de código)
tags git                    (criação)
SUTURE_ISSUES.md            (registra a decisão e a prova)
AGENTS.md                   (corrige o aviso de "160 commits não mergeados")
```

**4. Fonte obrigatória de consulta**
`CONSTITUICAO-SISTEMA-WORKFLOW.md` §5.8 — padrão de merge seguro e a proibição de mergear
sem aprovação explícita.

**5. Como fazer**
1. Prova sem executar de verdade:
   `git merge --no-commit --no-ff agente2/behaviors-onda2` → capturar a saída →
   **`git merge --abort` imediatamente.** Nunca commitar.
2. Confirmar que os behaviors já estão na main:
   `git ls-tree -r main --name-only -- behaviors | Measure-Object -Line`
3. Criar a tag: `git tag -a arquivo-morto/behaviors-onda2 agente2/behaviors-onda2 -m "..."`
4. Registrar em `SUTURE_ISSUES.md` a decisão, a prova e como recuperar depois.
5. Corrigir o parágrafo do `AGENTS.md` que trata a branch como pendência.
6. **Não deletar a branch.** A constituição proíbe (9.3.8).

**6. Armadilhas conhecidas**
- Se o `merge --no-commit` der conflito, o `--abort` é obrigatório e imediato. Nunca tentar
  resolver — §5.8 exige decisão humana.
- Tag não substitui branch. As duas ficam.
- Confirmar working tree limpo antes de começar, senão o `--abort` pode levar trabalho junto.

**7. Critérios de aceite**
- [ ] Saída do `merge --no-commit` colada, seguida do `--abort`
- [ ] `git status` limpo depois
- [ ] Tag `arquivo-morto/behaviors-onda2` existe
- [ ] Branch **não** deletada
- [ ] Contagem de behaviors na main colada
- [ ] `AGENTS.md` corrigido

**8. Como provar**
```powershell
git status --porcelain 2>&1 | Tee-Object -FilePath prova_R6.txt ; git tag -l "arquivo-morto/*" >> prova_R6.txt ; git branch -a >> prova_R6.txt ; git ls-tree -r main --name-only -- behaviors | Measure-Object -Line >> prova_R6.txt ; Get-Content prova_R6.txt
```

**9. Regressão a retestar**
`git worktree list` continua mostrando os 2 worktrees intactos. Colar.

**10. Marcação**
`[SÊNIOR]` `[EIXO-CENTRAL]` — decisão irreversível sobre histórico.

---

## Fatia R7 — Medição real

**1. O que é**
O antigo F0 do MASTER, agora com os nomes de função corretos, descobertos no recon:
`_get_phase_tools()` (server.py l.544), `_tool_defs()`, `_raw_tool_defs()`, `list_tools()`.

**2. Por que agora**
Existem 8 contagens diferentes circulando (33, 143, 171, 189, 191, 236, 248, 272, 287).
O HANDOFF diz DESIGN=82; `PHASE_TOOLSETS` cru diz 45. Nenhum dos dois é o que o modelo vê —
o que importa é o que sai de `tools/list`. Enquanto isso não for medido, toda fatia adiante
otimiza um número que ninguém sabe qual é.

**3. Arquivos que toca**
```
scripts/medir_wire.py        (novo)
MEDICAO_R7.md                (novo — a saída)
.reorg_baseline.json         (atualizado com o número real)
```

**4. Fonte obrigatória de consulta**
`MASTER_IMPLEMENTATION_ROADMAP.md` §17 FASE 0 (a lista de 8 categorias a medir) e
`server.py` linhas 530–580 (`PHASE_TOOLS_CORE` e `_get_phase_tools`).

**5. Como fazer**
`scripts/medir_wire.py` mede e imprime, com nome e não só contagem:
1. Por fase: `len(_get_phase_tools())` com `.mcp_phase_state.json` apontando para cada fase
   — o número que o modelo realmente vê, não a declaração.
2. `SEM_HANDLER`, `SEM_DEF`, `DUPLICADOS_NS`, `NS_FANTASMA`, `PHASE_FANTASMA`, `SEM_FASE`,
   `COLISAO_ROLLUP`.
3. Tokens por fase, reaproveitando `estimate_definition_tokens` de `test_budget_gate.py`.
4. Registrar o valor de `github.copilot.chat.virtualTools.threshold` do `settings.json`:
   se estiver ligada, o VS Code agrupa tools sozinho e a contagem vista no cliente **não é**
   a do servidor. Medir sempre no servidor.
5. Rodar duas vezes: a saída tem que ser idêntica (determinismo).

**6. Armadilhas conhecidas**
- As contagens antigas do catálogo somam CORE sobre listas que já contêm CORE — IDEIA e
  DESIGN aparecem inflados. Medir a **união**, não a soma.
- `_get_phase_tools()` lê `.mcp_phase_state.json` do projeto ativo. Sem projeto ativo, ele
  devolve só o CORE. Fixar um projeto de teste antes de medir.
- `config.local.json` não existe (bloco 43). Se a resolução de projeto ativo depender dele,
  a medição quebra — nesse caso, criar um mínimo e registrar isso.

**7. Critérios de aceite**
- [ ] `MEDICAO_R7.md` com número **e** nomes, por fase
- [ ] Duas execuções com saída idêntica
- [ ] Zero `~` e zero "a verificar" no arquivo
- [ ] `virtualTools.threshold` registrado
- [ ] Divergência maior que 20% contra o `REORG_ROADMAP.md` → **escalar antes da ONDA 1**

**8. Como provar**
```powershell
python scripts\medir_wire.py > MEDICAO_R7.md 2>&1 ; python scripts\medir_wire.py > _m2.txt 2>&1 ; fc MEDICAO_R7.md _m2.txt ; Get-Content MEDICAO_R7.md
```

**9. Regressão a retestar**
`python auditar.py --fatia R7` verde, agora com o C5 lendo o baseline novo da R3.

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]` — só leitura, tudo verificável por comando.

---

## Fatia R8 — Gerar as fichas das ondas seguintes

**1. O que é**
Produzir `.github/roadmap/ONDA_1_*.md` até `ONDA_P_*.md`, no formato de 10 campos, usando
os números reais medidos na R7.

**2. Por que agora**
Escrever essas fichas antes da R7 seria escrever sobre número estimado — exatamente o que
o AVISO DE BLOQUEIO do MASTER proíbe. Depois da R7 elas nascem certas.

**3. Arquivos que toca**
```
.github/roadmap/ONDA_1_registry.md
.github/roadmap/ONDA_2_conformidade.md
.github/roadmap/ONDA_3_rollups.md
.github/roadmap/ONDA_4_descoberta.md
.github/roadmap/ONDA_8_curadoria.md
.github/roadmap/ONDA_9_quarentena.md
.github/roadmap/ONDA_10_congelar.md
.github/roadmap/ONDA_P_pendencias.md
.roadmap_progress.json    (entradas novas, todas `nao verificado`)
```

**4. Fonte obrigatória de consulta**
`REORG_ROADMAP.md` §4 (o conteúdo de cada onda), `MEDICAO_R7.md` (os números) e
`plan.prompt.md` PASSO 5 (o formato exato dos 10 campos).

**5. Como fazer**
1. Uma fatia por feature. Nunca lote.
2. Todo campo 8 é um comando executável em PowerShell, sem `&&`, com `Tee-Object`.
3. Toda fatia recebe as duas marcações: `[AUTO]`/`[SÊNIOR]` e `[EIXO-CENTRAL]`/`[PERIFERIA]`.
4. Registrar cada fatia no `.roadmap_progress.json` com status `nao verificado`.
   Nunca nascer `concluida`.
5. A ONDA P entra completa: Feature 9, Feature 10, `set_node_property`/`get_node_property`,
   INV-03 com prova, 362×166 testes, `AGENTS.md`, `config.local.json`, consistência dos 38
   domínios, `.mcp_proof`, resíduos de "cline", `ruff`.

**6. Armadilhas conhecidas**
- Se a R7 divergir mais de 20% do previsto, **corrigir o `REORG_ROADMAP.md` antes** de gerar
  as fichas. Gerar em cima de premissa errada é repetir o erro que criou esta onda.
- Fatia sem campo 8 executável não pode existir: sem ele, o `/act` nunca marca `concluida`.

**7. Critérios de aceite**
- [ ] 8 arquivos `ONDA_*.md` criados
- [ ] Toda fatia com os 10 campos preenchidos
- [ ] Todo campo 8 é comando executável
- [ ] Toda fatia com as 2 marcações
- [ ] Toda entrada nova no `.json` está `nao verificado`

**8. Como provar**
```powershell
Get-ChildItem .github\roadmap\ONDA_*.md | Select-Object Name,Length 2>&1 | Tee-Object -FilePath prova_R8.txt ; Select-String -Path .github\roadmap\ONDA_*.md -Pattern "^\*\*8\. Como provar\*\*" | Measure-Object -Line >> prova_R8.txt ; Select-String -Path .github\roadmap\ONDA_*.md -Pattern "^## Fatia" | Measure-Object -Line >> prova_R8.txt ; Get-Content prova_R8.txt
```
A contagem de "Como provar" tem que ser **igual** à contagem de "Fatia".

**9. Regressão a retestar**
`/plan` roda, lê os arquivos novos e escolhe a primeira fatia da ONDA 1 sem erro.

**10. Marcação**
`[AUTO]` `[EIXO-CENTRAL]` — só escrita de documento, verificável por contagem.

---

## FECHAMENTO DA ONDA R

A onda só fecha com o relatório de 9 seções do `PROTOCOLO_AUTOGOVERNANCA.md` §7, mais:

- [ ] R1 a R8 com status final no `.roadmap_progress.json`
- [ ] `python auditar.py --fatia R-fechamento` → exit code 0, saída colada
- [ ] Gate git provado bloqueando pelo menos uma vez
- [ ] Um único arquivo de progresso na raiz
- [ ] `MEDICAO_R7.md` como novo baseline de todos os números do projeto

**Só depois disso a ONDA 1 começa.**
