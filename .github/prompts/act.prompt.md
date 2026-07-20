---
description: 'Implementa UMA fatia ja planejada e aprovada. Nao commita sozinha.'
mode: 'agent'
---

# /act — Executar a fatia aprovada

Voce vai implementar **uma** fatia, provar que funciona, e parar.
Nao commite. Nao comece a proxima.

---

## PASSO 0 — Verificacao de entrada

Confirme os tres itens. Se qualquer um falhar, **pare**:

1. Existe um plano aprovado pelo humano nesta conversa? Se nao → rode `/plan` primeiro.
2. `git status --porcelain` esta limpo? Se nao → pare e avise.
3. Voce esta na branch do seu territorio? (ver `AGENTS.md`)

Declare: `Executando Fatia X.Y — <nome> — [AUTO|SENIOR]`

---

## PASSO 1 — Checkpoint

Crie o ponto de retorno antes de tocar em qualquer coisa:

```
git rev-parse HEAD
```

Guarde o hash. Ele e a sua rede de seguranca. Anuncie-o.

---

## PASSO 2 — Leia a fonte antes de escrever

Abra a fonte declarada no campo 4 do plano
(ver `.github/instructions/fontes.instructions.md`).

**Cite qual usou e o que aprendeu dela, em duas linhas.**
Sem fonte citada, a fatia nao fecha. A causa raiz da maioria dos erros
neste projeto e inventar API do Godot que nao existe.

---

## PASSO 3 — Implemente

Regras:

- **So os arquivos listados no campo 3 do plano.** Tocou outro arquivo? Pare e explique.
- Rollup-first: feature nova entra como `op` de rollup via `create_manage_tool()`,
  nunca como tool de topo.
- Tool nova exige `Tool(...)` em `_tool_defs()` **e** handler em `_build_handlers()`.
- Estado por projeto em `<project_root>/.mcp_<nome>_state.json`, nunca global.
- Escrita concorrente exige lock via `tools/config_lock.py`.
- Subprocess so via `run_subprocess_safe()`, com `stdin=DEVNULL`.
- Rede so em `127.0.0.1`.
- PowerShell: nada de `&&`. Use `;` ou `cmd /c "a && b"`.

Se durante a implementacao voce descobrir que o plano estava errado:
**pare, explique o que mudou, e peca novo `/plan`.** Nao improvise um plano novo.

---

## PASSO 4 — Rode o portao

```
python auditar.py
```

Cole a saida **completa e literal**. Se falhar, conserte e rode de novo.
Nunca prossiga com o portao vermelho. Nunca altere o `auditar.py` para
fazer a sua fatia passar — isso e falha automatica.

---

## PASSO 5 — Prove

Cole, nesta ordem, tudo literal:

1. **Diff real**
   ```
   git --no-pager diff --no-color
   ```
   Precisa aparecer com marcadores `@@`. Resumo ou tabela nao vale.
   Se a saida for grande, use `git --no-pager diff --no-color -- <arquivo>`
   arquivo por arquivo. Nunca descreva o diff em palavras.

2. **Codigo real colado em bloco.**
   Nunca escreva "Read lines X to Y" — isso e log de ferramenta, nao codigo.

3. **Output de teste completo.**
   Nunca "passou!" sem prova. Cole o texto que o teste imprimiu.

4. **Cada criterio de aceite** do campo 7, um a um, com o comando que o comprova
   e a saida dele.

5. **Regressao** do campo 9: rode e cole o resultado.

Se voce afirmar "isso e bug pre-existente" ou "nao tem relacao com a fatia",
cole `git blame` ou `git log -p` provando. Sem prova, a afirmacao nao vale
e a fatia nao fecha.

---

## PASSO 6 — Autocritica honesta

Responda as cinco, sem suavizar:

1. Algum criterio de aceite ficou parcialmente atendido? Qual?
2. Tem codigo que eu escrevi e nao testei? Qual?
3. Tem `TODO`, `pass`, `NotImplementedError` ou stub no que eu entreguei?
4. Alguma coisa que eu chamei de "funcionando" que eu nao vi funcionar?
5. Eu redefini algum criterio no meio do caminho para caber no que eu fiz?

Responder "nao" nas cinco sem ter conferido e a falha mais grave possivel
neste projeto. Confira.

---

## PASSO 7 — Registre o progresso

Escreva no arquivo do **seu** territorio:

- Agente 1 → `.roadmap_progress.json`
- Agente 2 → `.roadmap_progress_a2.json`

Nunca escreva no arquivo do outro agente.

Campos: id da fatia, status (`concluida` ou `escalada`), data, hash do checkpoint,
e uma linha do que foi feito.

---

## PASSO 8 — Feche e encadeie

**Este passo vale igual para [AUTO] e [SENIOR]. Nao pule o encadeamento.**

### Se a fatia e [AUTO] e tudo passou:

1. Proponha o commit e **pare**:
   ```
   Sugestao de commit:
   git add <arquivos exatos>
   git commit -m "<tipo>: <descricao curta>"
   ```
   Nao execute. Espere aprovacao.

2. Depois da minha aprovacao do commit, **prepare a proxima fatia**:
   leia o roadmap, identifique qual e a proxima do seu territorio,
   e apresente-a em uma linha:
   `Proxima fatia: X.Y — <nome> — [AUTO|SENIOR]. Rode /plan quando quiser.`

### Se a fatia e [SENIOR], ou algum criterio falhou:

1. **Nao proponha commit.** Escale com este pacote:
   ```
   ESCALACAO — Fatia X.Y

   O que eu fiz: ...
   O que funcionou (com prova): ...
   O que NAO funcionou ou nao consegui provar: ...
   Decisao que preciso de voce: ...
   Opcoes que eu vejo: A) ... B) ...
   Como voltar atras: git reset --hard <hash do Passo 1>
   ```

2. **Depois da minha aprovacao explicita**, faca exatamente o mesmo que o ramo
   [AUTO] faz: proponha o commit, espere aprovacao, e entao **prepare a proxima
   fatia** com a linha `Proxima fatia: ...`.

   Este era o bug do fluxo antigo: o ramo [SENIOR] terminava sem encadear,
   e toda fatia [SENIOR] morria sem preparar a seguinte. Nao repita.

---

## PASSO 9 — Aprendizado

Se algo quebrou de um jeito novo, proponha uma regra nova para
`.github/instructions/aprendizados.instructions.md`, no formato:

```
RN — <titulo curto>
Sintoma: ...
Causa: ...
Regra: ...
```

Proponha. Nao escreva sozinha.

---

## NUNCA

- Commitar sem aprovacao.
- Fazer duas fatias no mesmo `/act`.
- Editar arquivo fora do territorio ou fora do campo 3 do plano.
- Alterar `auditar.py` para passar.
- Dizer "passou" sem colar o output.
- Redefinir criterio de aceite no meio.
- Insistir num loop de tentativa. **Parar e escalar e sucesso.**

