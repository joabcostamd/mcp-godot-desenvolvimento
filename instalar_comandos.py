#!/usr/bin/env python3
"""
instalar_comandos.py - Lote 2: instala os comandos /plan, /act, /handoff e /manual.

O QUE FAZ:
  1. Cria .github/prompts/ se nao existir
  2. Escreve os 4 arquivos de comando (estao embutidos aqui dentro)
  3. Confere que o Lote 1 ja foi instalado
  4. Relata o que fez

COMO USAR:
  Coloque SOMENTE este arquivo na RAIZ do repositorio e rode:

      python instalar_comandos.py --teste     (simula, nao muda nada)
      python instalar_comandos.py             (executa)

DEPOIS:
  Reinicie o VS Code. No chat do Copilot digite / e os comandos aparecem.

SEGURANCA:
  - Nao apaga nada. Se um comando ja existir com conteudo diferente,
    salva copia em journal/ antes de sobrescrever.
  - Rodar duas vezes nao duplica nada.
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTE = False
DESTINO = ".github/prompts"

DOCUMENTOS: dict[str, str] = {}

DOCUMENTOS['plan.prompt.md'] = r"""DOC0
---
description: 'Planeja a proxima fatia do roadmap. Nao implementa nada.'
mode: 'agent'
---

# /plan — Planejar a proxima fatia

Voce vai **planejar e parar**. Nao escreva codigo. Nao edite arquivo.
Nao commite. O resultado deste comando e um plano na tela, mais nada.

---

## PASSO 1 — Descubra quem voce e

```
git branch --show-current
```

| Branch | Voce e | Territorio |
|---|---|---|
| `main` | Agente 1 — Nucleo | `server.py`, `tools/`, `resources/`, `.github/`, `docs/`, raiz |
| `agente2/*` | Agente 2 — Conteudo | `behaviors/`, `blueprints/`, `seeds/`, `addons/`, `tests/`, `templates/` |
| outra | **pare e pergunte ao humano** | — |

Se so existe um agente rodando, voce e o Agente 1 e tem todos os territorios.

Declare em uma linha: `Sou o Agente N. Territorio: ...`

---

## PASSO 2 — Leia o estado

Leia, nesta ordem:

1. [AGENTS.md](../../AGENTS.md) — regras de convivencia
2. [ROADMAP_DEFINITIVO.md](../../ROADMAP_DEFINITIVO.md) — ondas e fatias
3. `.roadmap_progress.json` (Agente 1) ou `.roadmap_progress_a2.json` (Agente 2)
4. A ficha da onda atual em `.github/roadmap/ONDA_*.md`
5. [aprendizados](../instructions/aprendizados.instructions.md) — o que ja quebrou antes

Se o arquivo de progresso nao existir, crie-o mentalmente como vazio
(nao escreva ainda — escrever e trabalho do `/act`).

---

## PASSO 3 — Escolha UMA fatia

Criterios, em ordem:

1. A onda anterior precisa estar fechada. Nao pule onda.
2. A fatia precisa estar no **seu** territorio.
3. As dependencias dela precisam estar concluidas.
4. Escolha a primeira que satisfaz 1, 2 e 3. Nao escolha a mais facil.
5. **Uma so.** Nunca planeje duas.

Se nao houver fatia elegivel no seu territorio: diga isso, liste o que esta
bloqueando, e pare.

---

## PASSO 4 — Cheque conflito com o outro agente

Se existir mais de um agente (verifique com `git worktree list`):

```
git merge-tree $(git merge-base main HEAD) main HEAD
```

- Saida vazia → sem conflito, siga.
- Saida com marcadores de conflito → **pare e escale.** Nao planeje esta fatia.

Alem disso: compare a lista de arquivos da sua fatia com a da fatia que o outro
agente esta executando. Se houver **qualquer** arquivo em comum, escale.
Isolamento de pasta nao elimina conflito, so adia para o merge.

---

## PASSO 5 — Apresente o plano

Use exatamente esta ficha de 10 campos, nesta ordem:

```markdown
## Fatia X.Y — <nome>

**1. O que e**
Uma frase.

**2. Por que agora**
Qual dependencia a torna possivel, ou qual dor a torna necessaria.

**3. Arquivos que toca**
Caminhos exatos, um por linha. Se um deles estiver fora do meu territorio, escalo.

**4. Fonte obrigatoria de consulta**
Qual documentacao/repositorio eu vou ler antes de escrever
(ver .github/instructions/fontes.instructions.md).

**5. Como fazer**
Passo a passo tecnico. A decisao de arquitetura ja vem tomada:
qual padrao, qual arquivo, qual funcao, qual assinatura.
Sem "vou avaliar a melhor forma" — decida agora ou escale agora.

**6. Armadilhas conhecidas**
O que quebra neste ponto especifico.

**7. Criterios de aceite**
Objetivos e verificaveis por codigo. Cada criterio vira passa/falha.
Se um criterio nao vira teste, ele nao e auto-avaliavel — marque [SENIOR].

**8. Como provar**
O comando exato que gera a evidencia.

**9. Regressao a retestar**
O que ja aprovado pode quebrar, e como confirmo que nao quebrou.

**10. Marcacao**
[AUTO] ou [SENIOR], com o motivo em uma linha.
```

**Regra da marcacao:**
- `[AUTO]` — todos os criterios do campo 7 sao verificaveis por comando.
- `[SENIOR]` — toca seguranca, arquitetura, contrato publico, migracao de dados,
  ou tem criterio que depende de julgamento. Na duvida, `[SENIOR]`.

---

## PASSO 6 — PARE

Termine com exatamente esta linha:

```
Plano pronto. Aguardando sua aprovacao para rodar /act.
```

Nao implemente. Nao pergunte se pode comecar. Nao ofereca alternativas.
Pare.

DOC0"""[len('DOC0'):-len('DOC0')]

DOCUMENTOS['act.prompt.md'] = r"""DOC1
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

DOC1"""[len('DOC1'):-len('DOC1')]

DOCUMENTOS['handoff.prompt.md'] = r"""DOC2
---
description: 'Escreve o resumo de passagem de bastao para o outro agente ou para a proxima sessao.'
mode: 'agent'
---

# /handoff — Passar o bastao

O outro agente **nao tem o seu historico de conversa**. So existe o que estiver
em arquivo. Este comando transforma o que voce sabe em algo que ele consegue ler.

Use quando: terminar uma fatia, trocar de agente, ou a sessao estiver ficando longa.

---

## PASSO 1 — Junte os fatos

```
git branch --show-current
git --no-pager log --oneline -5
git status --porcelain
```

Leia tambem `.roadmap_progress.json` e `.roadmap_progress_a2.json`
(os dois, para saber o que o outro agente andou fazendo).

---

## PASSO 2 — Escreva o arquivo

Crie ou sobrescreva `journal/HANDOFF_<agente>.md`
(exemplo: `journal/HANDOFF_agente1.md`).

Use exatamente este formato. Seja curto: quem le quer saber onde pegar, nao ler um livro.

```markdown
# HANDOFF — Agente <N> — <data>

## Onde estou
Branch: <branch>
Ultimo commit: <hash curto> <mensagem>
Arvore limpa: sim/nao

## O que eu terminei
- Fatia X.Y — <nome> — concluida e aprovada
- Fatia X.Z — <nome> — escalada, esperando decisao do humano

## O que ficou pendente
Descreva o estado exato, nao a intencao.
Errado: "vou terminar o dock"
Certo: "dock_v1.gd criado com as 3 zonas; falta ligar o botao Reverter ao git_checkpoint"

## Decisoes tomadas nesta sessao
Uma linha cada, com o motivo. Isto evita que o proximo agente desfaca sem saber.

## Armadilhas que eu encontrei
O que quebrou e como contornei. Se for regra nova, ela tambem vai para
aprendizados.instructions.md — aqui e so o aviso rapido.

## Arquivos que eu toquei
Lista de caminhos. O outro agente usa isto para checar conflito.

## Proxima fatia sugerida
X.Y — <nome> — [AUTO|SENIOR]

## Como voltar atras
git reset --hard <hash>
```

---

## PASSO 3 — Avise sobre conflito

Se voce tocou em algum arquivo do territorio do outro agente, ou em algum arquivo
de terra de ninguem (`requirements.txt`, `pyproject.toml`, `.gitignore`,
`CHANGELOG.md`), **escreva isso em negrito no topo do handoff**.

---

## PASSO 4 — Confirme

Cole o caminho do arquivo criado e as 10 primeiras linhas dele.

`journal/` esta no `.gitignore`, entao este arquivo nao vai para o repositorio
publico — e proposital. Ele e nota de trabalho, nao documentacao.

---

## Regras

- Estado, nao intencao. "Falta X" vale; "vou fazer X" nao vale.
- Nao repita o que ja esta no roadmap. Handoff e o que mudou, nao o plano inteiro.
- Nao invente progresso. Se voce nao provou, escreva "nao provado".

DOC2"""[len('DOC2'):-len('DOC2')]

DOCUMENTOS['manual.prompt.md'] = r"""DOC3
---
description: 'Gera o manual do usuario a partir do codigo real. Nao escreve numero a mao.'
mode: 'agent'
---

# /manual — Gerar o manual do usuario

O manual e **gerado**, nunca escrito a mao. Numero escrito a mao envelhece e mente —
foi assim que este projeto acabou com quatro contagens diferentes de ferramentas
em quatro documentos.

Publico do manual: **uma pessoa que nao programa.** Nao e o contribuidor,
nao e voce, nao sou eu.

---

## PASSO 1 — Construa o gerador, nao o texto

Se `scripts/gerar_manual.py` nao existir, crie-o. Ele deve:

| Ler de | Para produzir |
|---|---|
| `_tool_defs()` do `server.py` | o que a ferramenta sabe fazer |
| `behaviors/*/behavior.json` | o dicionario "o que eu posso pedir" |
| `blueprints/*.json` | os generos disponiveis |
| `resources/prompts.py` | os comandos prontos |
| `PHASE_TOOLSETS` + `phase_ops.py` | as 6 fases e as travas |
| `tools/friendly_errors.py` | a secao "quando algo da errado" |

Importe os modulos de verdade e leia os dados. **Nao copie numero para dentro
do script.** Se voce precisou digitar um numero, esta errado.

Saida em `docs/manual/`, um arquivo por secao.

---

## PASSO 2 — Estrutura do manual

```
docs/manual/
  00-o-que-e.md            O que esta ferramenta faz (5 linhas + imagem)
  01-instalar.md           Instalacao em 1 comando
  02-primeiro-jogo.md      Seu primeiro jogo em 10 minutos
  03-as-fases.md           As 6 fases e por que elas existem
  04-o-que-posso-pedir.md  DICIONARIO — a secao mais importante
  05-generos.md            Generos disponiveis, com frase de exemplo
  06-o-painel.md           O dock explicado, botao por botao
  07-quando-travo.md       Quando o sistema te barra e por que
  08-publicar.md           Como publicar seu jogo
  09-deu-errado.md         Erros comuns em linguagem humana
```

**A secao 04 e a que decide o produto.** Ela lista cada comportamento da
biblioteca no formato:

```
### Perseguir o jogador
Diga: "quero que o inimigo me persiga"
O que acontece: o inimigo anda na sua direcao quando te ve.
Voce pode ajustar: velocidade, distancia que ele enxerga, se ele desiste.
```

Sem nome de arquivo, sem nome de classe, sem GDScript. A pessoa nao programa.

---

## PASSO 3 — Regras de escrita

- **Frase curta.** Uma ideia por frase.
- **Sem jargao.** "no" vira "peca do jogo". "instanciar" vira "colocar no jogo".
  Se um termo tecnico for inevitavel, explique na primeira vez e nunca mais.
- **Sempre diga o que a pessoa ganha**, nao o que o sistema faz.
  Errado: "o gate de verificacao valida o pipeline".
  Certo: "antes de seguir, conferimos se o jogo ainda abre — assim voce nao
  descobre o erro tres dias depois".
- **Toda trava e explicada como protecao**, nunca como obstaculo.
- **Tempo honesto.** Se o tutorial leva 25 minutos, escreva 25, nao 10.

---

## PASSO 4 — Gere e prove

```
python scripts/gerar_manual.py
```

Cole a saida completa. Depois prove que os numeros batem:

```
python -c "import server; print(len(server._tool_defs()))"
```

O numero que aparecer no manual tem que ser igual a este. Se for diferente,
o gerador esta errado — conserte o gerador, nao o manual.

---

## PASSO 5 — Verifique com olhos de leigo

Antes de fechar, responda:

1. Alguem que nunca abriu o Godot entende a secao 02?
2. Tem alguma palavra que so quem programa entende? Liste e troque.
3. A pessoa consegue ver algo funcionando antes do minuto 10 do tutorial?
4. Toda trava esta explicada como protecao?
5. Algum numero foi digitado a mao em vez de gerado?

Se a resposta 5 for "sim", conserte antes de propor o commit.

---

## PASSO 6 — Ingles

Gere tambem `docs/manual/en/` com a mesma estrutura, e um `llms.txt` na raiz
com os fatos estruturados do projeto para agentes de IA lerem.

O publico mundial de Godot le ingles. Os documentos internos de processo
podem continuar em portugues.

---

## PASSO 7 — Proponha o commit e pare

```
Sugestao de commit:
git add scripts/gerar_manual.py docs/manual/ llms.txt
git commit -m "docs: gera manual do usuario a partir do codigo"
```

Nao commite. Espere aprovacao.

DOC3"""[len('DOC3'):-len('DOC3')]


feitos: list[str] = []
avisos: list[str] = []


def log(m: str) -> None:
    print(m)


def ok(m: str) -> None:
    feitos.append(m)
    print(f"  [OK] {m}")


def aviso(m: str) -> None:
    avisos.append(m)
    print(f"  [!!] {m}")


def passo_1_prereq() -> bool:
    log("\n[1/3] Conferindo o Lote 1")
    faltando = []
    for esperado in ["ROADMAP_DEFINITIVO.md", "AGENTS.md",
                     ".github/copilot-instructions.md"]:
        if not (ROOT / esperado).exists():
            faltando.append(esperado)
    if faltando:
        aviso("Lote 1 nao esta instalado. Faltam: " + ", ".join(faltando))
        aviso("Rode 'python instalar.py' antes deste script.")
        return False
    ok("Lote 1 encontrado")
    return True


def passo_2_escrever() -> None:
    log("\n[2/3] Escrevendo os comandos")
    pasta = ROOT / DESTINO
    if not pasta.exists():
        if TESTE:
            ok(f"[teste] criaria {DESTINO}/")
        else:
            pasta.mkdir(parents=True, exist_ok=True)
            ok(f"{DESTINO}/ criada")

    for nome, conteudo in DOCUMENTOS.items():
        conteudo = conteudo.lstrip()
        destino = pasta / nome
        if destino.exists():
            atual = destino.read_text(encoding="utf-8", errors="replace")
            if atual.strip() == conteudo.strip():
                ok(f"{nome} ja esta atualizado")
                continue
            if not TESTE:
                bkp = ROOT / "journal" / (nome + ".anterior")
                bkp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destino, bkp)
                aviso(f"{nome} existia - copia em journal/{bkp.name}")
        if TESTE:
            ok(f"[teste] escreveria {DESTINO}/{nome} ({len(conteudo)} chars)")
            continue
        destino.write_text(conteudo, encoding="utf-8")
        ok(f"{DESTINO}/{nome} ({len(conteudo)} chars)")


def passo_3_verificar() -> None:
    log("\n[3/3] Verificando")
    pasta = ROOT / DESTINO
    if TESTE:
        ok("[teste] verificacao pulada")
        return
    for nome in DOCUMENTOS:
        arq = pasta / nome
        if not arq.exists():
            aviso(f"{nome} nao foi criado")
            continue
        txt = arq.read_text(encoding="utf-8", errors="replace")
        if not txt.lstrip().startswith("---"):
            aviso(f"{nome} sem frontmatter - o Copilot pode nao reconhecer")
        else:
            ok(f"{nome} valido")


def relatorio() -> None:
    log("\n" + "=" * 62)
    log(f"  CONCLUIDO - {len(feitos)} acao(oes), {len(avisos)} aviso(s)")
    log("=" * 62)
    if avisos:
        log("\nAVISOS:")
        for a in avisos:
            log(f"  - {a}")
    log("""
PROXIMOS PASSOS:

  1. Confira:    git status
  2. Commite:    git add -A
                 git commit -m "chore: comandos /plan /act /handoff /manual"
  3. REINICIE O VS CODE (obrigatorio - o Copilot le os comandos na inicializacao)
  4. No chat do Copilot, digite /  e veja se aparecem:
       /plan  /act  /handoff  /manual

  Se nao aparecerem: confira em Settings se
  'chat.promptFiles' esta habilitado.

  Para comecar: digite /plan
""")


def main() -> int:
    global TESTE
    ap = argparse.ArgumentParser(description="Lote 2 - comandos do Copilot")
    ap.add_argument("--teste", action="store_true", help="simula, nao altera nada")
    args = ap.parse_args()
    TESTE = args.teste

    log("=" * 62)
    log("  INSTALADOR DE COMANDOS - Lote 2")
    log(f"  Pasta: {ROOT}")
    if TESTE:
        log("  MODO TESTE - nada sera alterado")
    log("=" * 62)

    if not passo_1_prereq() and not TESTE:
        log("\nAbortado. Instale o Lote 1 primeiro.")
        return 1

    passo_2_escrever()
    passo_3_verificar()
    relatorio()
    return 0


if __name__ == "__main__":
    sys.exit(main())
