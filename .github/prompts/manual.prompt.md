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

