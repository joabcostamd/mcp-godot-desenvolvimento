---
applyTo: '**'
---

# ONDA 1 — ACESSIBILIDADE

**Objetivo:** uma pessoa que nao e voce consegue instalar, abrir e jogar algo.
**Criterio de saida:** alguem que nao programa, sem ajuda sua, sai do zero ate um
jogo rodando em menos de 20 minutos. **Testado com gente de verdade**, nao simulado.

---

## Fatia 1.A — Instalador de um comando

**1. O que e** Um comando que instala tudo: Python, MCP, Godot, configuracao do
Copilot, projeto criado, editor aberto.

**2. Por que agora** **E o gargalo absoluto.** Um nao-programador nao instala venv,
nao edita JSON de configuracao, nao gerencia chave de API. O MCP pode ser perfeito
por dentro e continuar inutilizavel para esse publico.

**3. Arquivos** `init.py` (novo) · empacotamento · `docs/instalacao.md`

**4. Fonte** Doc do VS Code sobre configuracao de servidor MCP (`mcp.json`).
Doc do Godot sobre instalacao e templates de export.

**5. Como fazer**
Um script que executa, nesta ordem, cada passo com mensagem clara e falha explicita:

1. **Detectar** Python, Godot e VS Code. Se faltar, dizer exatamente o que baixar
   e onde — nao instalar sozinho sem avisar.
2. **Criar o ambiente** Python isolado e instalar dependencias.
3. **Escrever a configuracao do MCP** no arquivo do Copilot, sem o usuario editar
   nada. Se ja existir configuracao, **mesclar**, nunca sobrescrever.
4. **Perguntar a pasta do projeto**, com sugestao padrao fora de pasta sincronizada
   (usa a Fatia 0.I).
5. **Criar o projeto** Godot e abrir o editor.
6. **Verificar** que tudo conversa: MCP responde, bridge conecta, Godot abre.
7. **Imprimir o proximo passo**: "abra o VS Code e digite `/plan`".

Cada passo imprime `[OK]` ou `[FALHA]` com o motivo em portugues simples.
Nunca mostre stack trace ao usuario final.

**6. Armadilhas**
- Instalacao que falha no meio precisa poder ser rodada de novo sem quebrar
  (idempotente).
- Nao sobrescreva configuracao existente do Copilot — mescle.
- Caminho com espaco ou acento quebra tudo no Windows (usa a Fatia 0.J).
- Nao peca chave de API se o usuario ja tiver o Copilot funcionando.

**7. Criterios de aceite**
- Numa maquina Windows limpa, um comando leva ate o editor aberto
- Rodar duas vezes nao quebra
- Cada falha possivel tem mensagem em portugues, sem stack trace
- Configuracao existente do Copilot e preservada

**8. Como provar** Log completo da execucao numa maquina limpa (ou VM).
Prova de idempotencia: rodar duas vezes, colar as duas saidas.

**9. Regressao** Instalacao manual antiga continua funcionando.

**10. Marcacao** `[SENIOR]`

---

## Fatia 1.B — Instalar templates de export

**1. O que e** Baixar e instalar os templates de export do Godot no `init`.

**2. Por que agora** O seu proprio teste ponta a ponta falhou por falta deles.
Para nao-programador e bloqueio total: ele so descobre no fim, quando vai publicar.

**3. Arquivos** `init.py` · `tools/export_ops.py`

**4. Fonte** Doc oficial do Godot: "Exporting projects" e localizacao dos templates.

**5. Como fazer**
Verifique se os templates da versao exata do Godot estao instalados.
Se nao: baixe do endereco oficial da versao correspondente e instale na pasta
padrao do sistema. Mostre progresso — o arquivo e grande.

Adicione a verificacao ao `release_checklist`: se faltar template, o checklist
falha com mensagem clara, em vez de o export quebrar depois.

**6. Armadilhas**
- Versao dos templates precisa ser **identica** a do editor, nao "compativel".
- Download grande sem barra de progresso parece travamento.
- Se ja estiverem instalados, nao rebaixe.

**7. Criterios de aceite**
- Templates ausentes → instalados pelo `init`
- Templates presentes → pulados
- `release_checklist` acusa ausencia com mensagem clara

**8. Como provar** Os 3 cenarios, saida colada, mais um export real funcionando.

**9. Regressao** `build_export` continua funcionando.

**10. Marcacao** `[AUTO]`

---

## Fatia 1.C — Suporte a mais de um provedor de IA

**1. O que e** O `init` aceita mais de um provedor, nao so um.

**2. Por que agora** Custo baixissimo agora, altissimo depois. Se o provedor unico
mudar de preco ou de API, o produto para.

**3. Arquivos** `init.py` · documentacao

**4. Fonte** Doc do VS Code sobre modelos disponiveis no Copilot.

**5. Como fazer**
No `init`, ofereca as opcoes e escreva a configuracao correspondente.
Guarde a escolha no estado. Nao valide chave na hora da instalacao —
valide no primeiro uso, com mensagem clara se falhar.

**6. Armadilhas** Nunca grave chave de API em arquivo commitado.
Confirme com a busca de segredos que ela nao vaza.

**7. Criterios de aceite**
- Pelo menos 2 opcoes funcionam
- Nenhuma chave aparece em arquivo versionado
- Trocar de provedor nao exige reinstalar

**8. Como provar** Saida do `init` nas 2 opcoes + `git grep` por chave.

**9. Regressao** Configuracao existente continua valendo.

**10. Marcacao** `[AUTO]`

---

## Fatia 1.D — Custo de tokens visivel

**1. O que e** Mostrar quanto a sessao esta custando, com teto e aviso.

**2. Por que agora** O nao-programador paga a API. Se gastar muito sem perceber,
ele abandona e fala mal. Estava classificado como polimento — **esta errado**,
e Onda 1.

**3. Arquivos** `tools/` (op de rollup) · dock (Fatia 1.E)

**4. Fonte** Nenhuma externa.

**5. Como fazer**
Registre por sessao: chamadas de tool, tokens estimados de entrada e saida,
custo estimado. Exponha uma op que devolve o resumo.

No dock, mostre em dinheiro, nao em token: "esta sessao: R$ 0,80".
Token nao significa nada para o usuario final.

Configure um teto. Ao chegar em 80%, avise. Ao chegar em 100%, **pergunte**
antes de continuar — nunca pare em silencio.

**6. Armadilhas**
- O custo e **estimativa**. Diga isso, sempre.
- Nao calcule custo a cada chamada — acumule e reporte.

**7. Criterios de aceite**
- O total sobe conforme o uso
- O aviso de 80% dispara
- O teto pergunta antes de bloquear
- Aparece em dinheiro

**8. Como provar** Sessao simulada com chamadas, saida colada em cada marco.

**9. Regressao** Nenhuma.

**10. Marcacao** `[SENIOR]`

---

## Fatia 1.E — Dock v1

**1. O que e** Painel dentro do editor do Godot com estado, erros e 4 botoes.

**2. Por que agora** E a unica interface visual do produto. Sem ela, o
nao-programador nao sabe onde esta nem o que fazer.

**3. Arquivos** `addons/mcp_dock/plugin.cfg` · `addons/mcp_dock/plugin.gd` ·
`addons/mcp_dock/dock.tscn` · `addons/mcp_dock/dock.gd`

**4. Fonte** Doc oficial do Godot: "Making plugins" e "Running code in the editor".
**Leia as duas antes de escrever a primeira linha.**

**5. Como fazer**

Layout, 3 zonas, dock a direita:
- **Zona 1 (topo)**: nome do projeto, fase atual, barra de progresso do milestone,
  e **uma** frase de proximo passo. Uma so, nunca uma lista.
- **Zona 2 (meio)**: semaforo verde/amarelo/vermelho + erros traduzidos pelo
  `friendly_errors`, agrupados por causa, cada um com botao "Consertar".
  Stack trace fica escondido atras de "ver detalhes".
- **Zona 3 (rodape)**: 4 botoes grandes — Rodar · Testar · Aprovar · Reverter.
  "Reverter" precisa dizer **para onde** volta ("volta para antes de
  'adicionar inimigos', 14h32").

As 8 regras tecnicas, sem excecao — o editor do Godot **nao e protegido contra
erro em plugin**; se o dock travar, trava o editor junto:

1. `@tool` obrigatorio, herdar de `EditorPlugin`, raiz do dock e `Control`
2. Remover dock e liberar controles no `_exit_tree()`
3. **Nunca** manipular a arvore de cena pelo dock, em especial `queue_free()`
4. Desenvolver o script **sem** `@tool` primeiro, testar, so entao anotar
5. **Zero chamada bloqueante** — comunicacao por `Timer` de 1–2 s lendo arquivo
   de estado. Uma chamada sincrona congela o editor inteiro
6. Nao depender, no `_ready()` do dock, de algo criado pelo plugin
   (ha caso reportado de dock rodando antes do plugin, causando crash)
7. Toda escrita na cena passa pelo UndoRedo nativo, via bridge existente
8. Guardar logica de editor com `Engine.is_editor_hint()`

**6. Armadilhas**
- Nao construa editor de HUD dentro do dock. Isso e reconstruir o editor do Godot
  e e onde projetos assim morrem.
- Nao mostre numero que o usuario nao pode usar ("92 tools visiveis").
- Nada pisca, nada rouba foco.

**7. Criterios de aceite**
- O dock abre e fecha sem travar o editor
- Desativar o plugin nao deixa nada para tras
- Fase e proximo passo aparecem corretos
- Os 4 botoes funcionam
- Com o MCP desligado, o dock mostra "desconectado" e **nao** trava

**8. Como provar** Video ou sequencia de screenshots dos 5 cenarios,
mais o log do editor sem erro.

**9. Regressao** O editor abre normalmente com e sem o plugin ativo.

**10. Marcacao** `[SENIOR]`

---

## Fatia 1.F — Erro amigavel universal

**1. O que e** Garantir que **todo** erro que chega ao usuario passa pelo tradutor.

**2. Por que agora** `friendly_errors.py` ja existe, mas cobre so parte dos casos.
Erro cru e o momento em que o nao-programador desiste.

**3. Arquivos** `tools/friendly_errors.py` · pontos de saida de erro

**4. Fonte** Nenhuma externa.

**5. Como fazer**
Mapeie os pontos onde erro chega ao usuario e faca todos passarem por uma funcao
unica de traducao. Formato da mensagem, sempre 3 partes:
1. o que aconteceu, em portugues
2. o que isso significa para o jogo dele
3. o que fazer agora

Erro sem traducao cadastrada vira: "algo deu errado em X. Detalhe tecnico: ...",
nunca stack trace puro.

**6. Armadilhas** Nao esconda o detalhe tecnico — guarde atras de "ver detalhes".
A IA agentica precisa dele.

**7. Criterios de aceite**
- Nenhum caminho de erro devolve stack trace direto ao usuario
- Erro desconhecido tem formato padrao
- O detalhe tecnico continua acessivel

**8. Como provar** Provoque 5 erros diferentes, cole as 5 mensagens.

**9. Regressao** Log tecnico continua completo.

**10. Marcacao** `[AUTO]`

---

## Fatia 1.G — Executar a reestruturacao documental

**1. O que e** As 5 fatias R1–R5 do `PLANO_REESTRUTURACAO_DOCS.md`.

**2. Por que agora** O instalador ja moveu a estrutura; falta o conteudo.

**3. Arquivos** ver o plano

**4. Fonte** `PLANO_REESTRUTURACAO_DOCS.md`

**5. Como fazer** Siga o plano, uma fatia R por vez. **Mover e mover** —
melhoria de texto e fatia separada, exceto no expurgo de Cline (0.D).

**6. Armadilhas** A IA adora "melhorar" texto ao mover, e regras que custaram
meses somem. Nao reescreva.

**7. Criterios de aceite** Os criterios de cada fatia R no plano.

**8. Como provar** `git status` mostrando renomeacoes, nao exclusao + criacao.

**9. Regressao** `/plan` e `/act` continuam funcionando.

**10. Marcacao** `[SENIOR]`

---

## Fatias 1.H a 1.Q — fichas resumidas

Estas serao expandidas pelo `/plan` quando chegar a vez. Ficha detalhada de fatia
distante envelhece antes de ser usada.

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 1.H | Manual gerado por codigo | Use `/manual`. Nenhum numero digitado a mao | `[AUTO]` |
| 1.I | Tutoriais 1 a 4 | **So depois do instalador existir.** Cada tutorial vira teste de CI | `[SENIOR]` |
| 1.J | `quick_start` | Frase → esqueleto **jogavel** em 10 min. Meta de produto, nao de codigo | `[SENIOR]` |
| 1.K | Modo remix | Clonar jogo-semente em vez de pagina em branco. Comeca pelo Breakout | `[AUTO]` |
| 1.L | Vitrine de generos | Os `game_patterns` viram frases prontas visiveis no README e no modo guiado | `[AUTO]` |
| 1.M | Skills e modo guiado | MCP expoe as skills; o `init` copia para a pasta de regras do cliente | `[SENIOR]` |
| 1.N | `llms.txt` e README bilingue | README de produto: o que e, para quem, GIF, 3 comandos, generos | `[AUTO]` |
| 1.O | Degradacao sem internet | O que funciona offline continua funcionando, com aviso | `[AUTO]` |
| 1.P | Telemetria opt-in | Onde as pessoas travam. **Consentimento explicito, nunca ligado por padrao** | `[SENIOR]` |
| 1.Q | Historico de versoes jogaveis | Escolher por screenshot e data, nao por hash. Aposta de recurso mais amado | `[SENIOR]` |

