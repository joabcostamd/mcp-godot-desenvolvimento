#!/usr/bin/env python3
"""
instalar_roadmap.py - Lote 4: fichas detalhadas das ondas.

O QUE FAZ:
  Escreve em .github/roadmap/ as 4 fichas com o "como fazer" de cada fatia:
    ONDA_0_destravar.md
    ONDA_1_acessibilidade.md
    ONDA_2_fosso.md
    ONDA_3_4_qualidade_mundo.md

COMO USAR:
  Coloque SOMENTE este arquivo na RAIZ do repositorio e rode:

      python instalar_roadmap.py --teste
      python instalar_roadmap.py

DEPOIS:
  Reinicie o VS Code e digite /plan. A IA passa a ter o campo
  "Como fazer" ja resolvido em cada fatia - ela executa, nao improvisa.
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTE = False
DESTINO = ".github/roadmap"

DOCUMENTOS: dict[str, str] = {}

DOCUMENTOS['ONDA_0_destravar.md'] = r"""DOC0
---
applyTo: '**'
---

# ONDA 0 — DESTRAVAR

**Objetivo:** consertar o que esta quebrado ou contraditorio antes de construir por cima.
**Criterio de saida:** `auditar.py` passa, `/plan` e `/act` funcionam, zero referencia a
Cline fora de `journal/`, LICENSE existe, numeros dos documentos batem com o codigo.

Cada fatia abaixo ja vem com o campo 5 (**Como fazer**) resolvido. A IA nao improvisa
arquitetura — ela executa a decisao ja tomada. Se a fonte contradisser a ficha,
**pare e escale**: a fonte ganha.

---

## Fatia 0.A — Corrigir o bug do Passo 8

**1. O que e** O ramo `[SENIOR]` do fluxo antigo terminava sem encadear a proxima fatia.

**2. Por que agora** Ja esta corrigido no `act.prompt.md` do Lote 2. Esta fatia so
confirma que o arquivo antigo nao esta mais em uso.

**3. Arquivos** `.github/prompts/act.prompt.md` (verificar) · `journal/act-original.md` (nao usar)

**4. Fonte** Nenhuma externa.

**5. Como fazer**
Confirme que `.github/prompts/act.prompt.md` existe e que o PASSO 8 tem o encadeamento
nos **dois** ramos. Confirme que nao existe mais `.clinerules/workflows/act.md`.
Se existir, mova para `journal/`.

**6. Armadilhas** Nao edite o `act.prompt.md` do Lote 2 — ele ja esta correto.

**7. Criterios de aceite**
- `.clinerules/` nao existe (migrado para .github/)
- `grep -c "Proxima fatia" .github/prompts/act.prompt.md` retorna 2 ou mais

**8. Como provar** Cole a saida dos dois comandos acima.

**9. Regressao** Nenhuma.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.B — Auditar o fechamento da Fatia 0.9

**1. O que e** A Fatia 0.9 (cliente HTTP compartilhado) consta como concluida no
`.roadmap_progress.json`, mas foi **escalada** e tinha 3 provas pendentes.

**2. Por que agora** Se ela fechou sem as provas, o arquivo de progresso mente,
e todo o roadmap parte de uma base falsa.

**3. Arquivos** `.roadmap_progress.json` · `tools/external_client.py` (so leitura)

**4. Fonte** Historico do proprio repositorio.

**5. Como fazer**
As 3 provas exigidas e nunca entregues eram:
a) comportamento quando o limite de requisicoes estoura;
b) retry com backoff comprovado **por mock**, nao por timeout real;
c) confirmacao de que nao ha chave de API escrita no codigo.

Para cada uma, rode e cole:
```
git log --oneline -- tools/external_client.py
git --no-pager log -p -- tools/external_client.py
```
Procure no historico se as provas apareceram. Depois rode os testes existentes
do modulo e cole a saida.

Para (c), rode a busca por segredo:
```
git grep -nE "sk-|api[_-]?key\\s*=\\s*[\\"']" -- tools/
```

**6. Armadilhas** Ausencia de prova no historico **nao** significa que o codigo esta
errado — significa que nao foi comprovado. Reporte assim, sem exagerar nem suavizar.

**7. Criterios de aceite**
- As 3 provas foram localizadas no historico, OU
- Foi confirmado que faltam, e a fatia foi reaberta no `.roadmap_progress.json`

**8. Como provar** Saida literal dos comandos acima.

**9. Regressao** Nenhuma (so leitura, exceto o campo de status).

**10. Marcacao** `[SENIOR]` — decisao de reabrir fatia e do humano.

---

## Fatia 0.C — Decidir a Fatia 0.7b (teto de tools por fase)

**1. O que e** 6 fases passam de 40 tools visiveis. A fatia esta bloqueada ha tempo.

**2. Por que agora** Ela bloqueia o fechamento da Camada 0 e pode ser desnecessaria.

**3. Arquivos** `.roadmap_progress.json` · `server.py` (so leitura)

**4. Fonte** Documentacao do MCP sobre descoberta progressiva de ferramentas.

**5. Como fazer**
A decisao depende de um fato, nao de opiniao: **o fluxo real roda em modo lean ou full?**

Meça:
```
python -c "import server; d=server._tool_defs(); print('total', len(d))"
```
E conte por fase, usando `PHASE_TOOLSETS`.

- Se o modo **lean** e o padrao efetivo (so `catalog_search`, `describe_tool`,
  `invoke_by_name` + rollups visiveis), o teto quase deixa de importar →
  rebaixe 0.7b para `[MARGINAL]` e registre o motivo.
- Se o modo **full** e o padrao, 0.7b e a proxima fatia real → mantenha bloqueante.

**6. Armadilhas** Nao "resolva" o teto apagando tools. Tool removida quebra fluxo
existente. A solucao correta e visibilidade, nao exclusao.

**7. Criterios de aceite**
- A contagem por fase esta colada, medida do codigo
- A decisao esta registrada no `.roadmap_progress.json` com o motivo

**8. Como provar** Saida da medicao + trecho do JSON alterado.

**9. Regressao** Nenhuma.

**10. Marcacao** `[SENIOR]`

---

## Fatia 0.D — Migracao de estrutura e expurgo de IA agentica

**1. O que e** Trocar toda mencao a IA agentica por "IA agentica (Copilot)".

**2. Por que agora** A estrutura ja foi movida pelo instalador; falta o texto interno.

**3. Arquivos** `.github/instructions/*.md` · `.github/copilot-instructions.md` ·
`docs/**` · `README.md`

**4. Fonte** `PLANO_REESTRUTURACAO_DOCS.md`, secao 3.5.

**5. Como fazer**
```
git grep -ril "IA agentica" -- .github docs README.md
```
Para cada arquivo, troque:
- `IA agêntica (Copilot)` → `IA agentica (Copilot)`
- `.clinerules` → `.github/instructions`
- `mcp.json` → `mcp.json` (config do Copilot)

**Nao toque em `journal/`** — la e arquivo historico, e deve continuar como estava.

**6. Armadilhas** Trocar so a palavra pode deixar frase sem sentido
("no IA agêntica (Copilot), use o botao X" nao tem equivalente). Leia a frase inteira; se ela so
faz sentido no IA agêntica (Copilot), reescreva ou remova. **Esta e a unica excecao a regra
"mover e mover"** — aqui a edicao e o objetivo da fatia.

**7. Criterios de aceite**
- `git grep -ril "IA agentica" -- .github docs README.md` retorna vazio (fatia 0.D concluida)
- Nenhuma frase ficou sem sentido (revisao humana)

**8. Como provar** Saida do grep antes e depois + `git diff` completo.

**9. Regressao** Reinicie o VS Code e confirme que `/plan` ainda aparece.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.E — LICENSE e arquivos de comunidade

**1. O que e** Criar `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.

**2. Por que agora** **Bloqueio absoluto.** Sem LICENSE nao da para publicar na
AssetLib, nao da para receber contribuicao, e ninguem pode legalmente usar o projeto.
Ironia: o proprio `release_checklist` do MCP cobra LICENSE dos jogos.

**3. Arquivos** `LICENSE` · `CONTRIBUTING.md` · `CODE_OF_CONDUCT.md` · `SECURITY.md`

**4. Fonte** Texto padrao da licenca MIT · Contributor Covenant.

**5. Como fazer**
- `LICENSE`: MIT, com o ano corrente e o nome do autor. MIT e o padrao do
  ecossistema Godot e o que permite adocao maxima.
- `CONTRIBUTING.md`: como rodar os testes, o padrao de commit, a regra de
  uma fatia por vez, e o link para `AGENTS.md`.
- `CODE_OF_CONDUCT.md`: Contributor Covenant padrao.
- `SECURITY.md`: como reportar vulnerabilidade em privado.

**6. Armadilhas** Nao invente texto de licenca. Use o texto oficial, literal.

**7. Criterios de aceite**
- Os 4 arquivos existem
- `release_checklist` do proprio MCP reconhece o LICENSE

**8. Como provar** `ls` dos arquivos + saida do `release_checklist`.

**9. Regressao** Nenhuma.

**10. Marcacao** `[AUTO]` — mas a escolha da licenca e decisao do humano. Pergunte antes.

---

## Fatia 0.F — `docs_sync`: numeros gerados, nunca a mao

**1. O que e** Script que extrai numeros reais do codigo e injeta nos documentos.

**2. Por que agora** Existem 4 contagens diferentes de ferramentas em 4 documentos.
A causa e numero digitado a mao. A correcao e estrutural, nao manual.

**3. Arquivos** `scripts/docs_sync.py` (novo) · documentos gerados

**4. Fonte** Codigo do proprio `server.py`.

**5. Como fazer**
Crie `scripts/docs_sync.py` que:
1. importa `server` e le `len(server._tool_defs())`
2. le a versao de onde ela realmente vive no codigo
3. conta rollups e ops
4. substitui marcadores nos documentos, no formato:
   `<!--DOCS_SYNC:tools-->204<!--/DOCS_SYNC-->`

Regra: o script **le do codigo**. Se voce digitou um numero dentro do script,
esta errado.

Adicione a chamada ao `auditar.py` como verificacao: se um documento tiver
numero fora do marcador que contradiga o codigo, falha.

**6. Armadilhas** Importar `server` pode ter efeito colateral (abrir porta, criar
arquivo). Use import protegido ou leia por AST se necessario.

**7. Criterios de aceite**
- `python scripts/docs_sync.py` roda sem erro
- Todas as contagens em documentos batem com `len(server._tool_defs())`
- Rodar duas vezes nao muda nada (idempotente)

**8. Como provar** Saida do script + `git diff` + o comando de contagem direta.

**9. Regressao** `python auditar.py` continua passando.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.G — Expurgo de caminhos pessoais

**1. O que e** Remover `C:\\Users\\<usuario>\\...` dos documentos publicos.

**2. Por que agora** Aparece dezenas de vezes. Guia publico nao pode conter o
disco de ninguem.

**3. Arquivos** `docs/**` · `README.md` · `.github/**`

**4. Fonte** Nenhuma.

**5. Como fazer**
```
git grep -nE "C:\\\\Users|OneDrive" -- docs .github README.md
```
Troque por placeholder: `<CAMINHO_DO_PROJETO>` ou `%USERPROFILE%`.
Confirme que `journal/` esta no `.gitignore` (o instalador ja fez).

**6. Armadilhas** Nao troque dentro de `journal/`.

**7. Criterios de aceite** O grep retorna vazio fora de `journal/`.

**8. Como provar** Saida do grep antes e depois.

**9. Regressao** Nenhuma.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.H — Protocolo anti-conflito MCP e editor aberto

**1. O que e** Impedir que o MCP escreva num arquivo que o editor do Godot tem
aberto com alteracoes nao salvas.

**2. Por que agora** **E o furo mais perigoso do sistema.** Se o usuario tem a cena
com mudanca pendente e o MCP escreve no `.tscn`, um dos dois perde trabalho — e o
Godot pode salvar por cima depois.

**3. Arquivos** `tools/` (novo modulo ou op em rollup existente) · Addon Bridge

**4. Fonte** Doc oficial do Godot: `EditorInterface`, estado de cena nao salva.

**5. Como fazer**
Antes de **qualquer** escrita em `.tscn`, `.tres` ou `.gd`, o MCP pergunta ao addon:
"esta cena tem alteracao nao salva?".

Três respostas possiveis:
- **Nao ha alteracao pendente** → escreva normalmente.
- **Ha alteracao pendente** → recuse a escrita e devolva mensagem clara:
  "o arquivo X esta aberto no Godot com mudancas nao salvas. Salve (Ctrl+S) e
  peca de novo."
- **Addon nao responde** (Godot fechado ou bridge caido) → escreva, mas registre
  aviso. Godot fechado nao tem conflito.

Implemente como funcao unica por onde toda escrita passa. Nao espalhe a checagem.

**6. Armadilhas**
- Nao tente salvar pelo usuario sem avisar — isso e o mesmo desastre por outro caminho.
- Timeout curto (1–2 s). Se o addon demorar, trate como "nao responde".
- Nao bloqueie o servidor esperando resposta.

**7. Criterios de aceite**
- Com Godot fechado: escrita funciona
- Com Godot aberto e cena limpa: escrita funciona
- Com Godot aberto e cena suja: escrita e recusada com mensagem clara
- Com bridge derrubado: escrita funciona com aviso

**8. Como provar** Os 4 cenarios acima, com saida colada de cada um.

**9. Regressao** Todas as tools que escrevem arquivo continuam funcionando.
Rode a suite existente.

**10. Marcacao** `[SENIOR]` — toca o caminho de escrita de tudo.

---

## Fatia 0.I — Detectar pasta sincronizada em nuvem

**1. O que e** Avisar quando o projeto esta dentro de OneDrive, Dropbox ou Google Drive.

**2. Por que agora** Sincronizacao em cima da pasta `.godot` (cache e import) causa
corrupcao e reimport infinito. O seu proprio ambiente esta assim.

**3. Arquivos** `install.py` ou o futuro `init` · verificacao no start do servidor

**4. Fonte** Doc do Godot sobre a pasta `.godot`.

**5. Como fazer**
Detecte por caminho e por marcador:
- caminho contendo `OneDrive`, `Dropbox`, `Google Drive`, `iCloud`
- presenca de `.dropbox`, `desktop.ini` com CLSID de sincronizacao

Ao detectar, **avise, nao bloqueie**:
"Este projeto esta numa pasta sincronizada. Isso pode corromper o cache do Godot.
Recomendado: mover para `C:\\Projetos\\`. Quer continuar mesmo assim?"

Ofereca tambem adicionar `.godot/` a exclusao de sincronizacao, se possivel.

**6. Armadilhas** Nao mova a pasta do usuario sozinha, nunca.

**7. Criterios de aceite**
- Projeto em pasta sincronizada → aviso aparece
- Projeto em pasta normal → nenhum aviso
- O aviso nao impede o uso

**8. Como provar** Os 2 cenarios, com saida colada.

**9. Regressao** Nenhuma.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.J — Normalizacao de nome com acento e espaco

**1. O que e** "Meu Jogo Legal" e `coracao.tscn` quebram caminho, import e export.

**2. Por que agora** O usuario brasileiro **vai** fazer isso no primeiro minuto.

**3. Arquivos** onde nome de projeto e de arquivo sao criados

**4. Fonte** Convencoes de nomenclatura do Godot.

**5. Como fazer**
Separe **rotulo** de **identificador**:
- rotulo: o que o usuario digitou, guardado no estado e mostrado na tela
- identificador: normalizado — sem acento (`unicodedata.normalize('NFKD')`),
  sem espaco (vira `_`), minusculo, so `[a-z0-9_]`

Use o identificador para pasta, arquivo e classe. Use o rotulo para exibir.

Avise uma vez: "vou salvar como `meu_jogo_legal`, mas o nome do jogo continua
'Meu Jogo Legal'".

**6. Armadilhas** Colisao: dois rotulos diferentes podem gerar o mesmo identificador.
Trate com sufixo numerico.

**7. Criterios de aceite**
- "Meu Jogo Legal" → `meu_jogo_legal`
- "Coração 2" → `coracao_2`
- Colisao gera `_2`, nao sobrescreve
- O rotulo original aparece na interface

**8. Como provar** Teste unitario com os 3 casos, output colado.

**9. Regressao** Projetos existentes continuam abrindo.

**10. Marcacao** `[AUTO]`

---

## Fatia 0.K — Guarda de propriedade intelectual de terceiros

**1. O que e** Impedir que o MCP gere jogo com personagem ou marca de terceiros.

**2. Por que agora** "Faz um jogo do Mario" vai acontecer no primeiro dia.
Sem trava, o usuario fica exposto juridicamente e voce junto.

**3. Arquivos** `project_brief` · gerador de arte · `license_audit`

**4. Fonte** Nenhuma externa.

**5. Como fazer**
No momento em que o brief do projeto e definido, verifique mencao a personagem,
franquia ou marca conhecida. Ao detectar, **nao recuse secamente** — redirecione:

"Nao posso usar personagens de outras empresas, porque voce nao poderia publicar
o jogo depois. Mas posso fazer algo com a mesma sensacao: um encanador que pula
em canos, com personagem original. Serve?"

Registre a decisao no estado do projeto, para nao perguntar de novo.

**6. Armadilhas**
- Nao vire censor. Inspiracao em genero e legitima; copia de personagem nao e.
- Lista de nomes envelhece e nunca sera completa. Trate como rede grossa,
  nao como garantia — e diga isso ao usuario.

**7. Criterios de aceite**
- Brief com personagem conhecido → redirecionamento com alternativa
- Brief com genero ("plataforma", "roguelike") → passa sem atrito
- A decisao fica registrada

**8. Como provar** Os 2 cenarios, saida colada.

**9. Regressao** Criacao de projeto normal continua fluida.

**10. Marcacao** `[SENIOR]`

---

## Fatia 0.L — Bug `set_node_property` / `get_node_property`

**1. O que e** `set_node_property` escreve no `.tscn`, mas `get_node_property`
retorna null.

**2. Por que agora** A IA depende de leitura confiavel. Se ela escreve e nao consegue
ler de volta, ela **fabrica** o estado — que e o problema numero um do projeto.

**3. Arquivos** os modulos das duas tools

**4. Fonte** Doc oficial do Godot sobre formato `.tscn`.

**5. Como fazer**
Primeiro **diagnostique**, nao conserte:
1. Rode `set_node_property` e cole o `.tscn` antes e depois
2. Rode `get_node_property` e cole a saida
3. Determine onde a leitura falha: parser do `.tscn`, caminho do no, ou cache

So depois proponha a correcao, com a causa raiz nomeada.

**6. Armadilhas**
- Nao "conserte" fazendo `get` ler do cache do `set` — isso esconde o bug.
- Propriedade herdada de cena instanciada nao aparece no `.tscn` filho.
  Pode ser este o caso — verifique antes de chamar de bug.

**7. Criterios de aceite**
- Escrever e ler de volta devolve o mesmo valor
- Teste automatizado cobrindo escrita e leitura
- A causa raiz esta nomeada no relatorio

**8. Como provar** Teste com output completo + `.tscn` antes e depois.

**9. Regressao** Outras tools de no continuam funcionando.

**10. Marcacao** `[SENIOR]`

DOC0"""[len('DOC0'):-len('DOC0')]

DOCUMENTOS['ONDA_1_acessibilidade.md'] = r"""DOC1
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
melhoria de texto e fatia separada, exceto no expurgo de IA agentica (0.D).

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

DOC1"""[len('DOC1'):-len('DOC1')]

DOCUMENTOS['ONDA_2_fosso.md'] = r"""DOC2
---
applyTo: '**'
---

# ONDA 2 — O FOSSO

**Objetivo:** derrubar a barreira dos 70% — o ponto em que codigo gerado por IA
parece bom no primeiro rascunho e comeca a quebrar conforme features sao somadas.
**Criterio de saida:** 30 comportamentos com teste passando, 3 blueprints de genero,
3 jogos-semente, e taxa de correcao manual abaixo de 15% num jogo novo do zero.

Esta e a onda mais longa e a mais valiosa. Ela e o que nenhum concorrente tem.

---

## A ideia central (leia antes de qualquer fatia desta onda)

A IA nao deve **gerar codigo do zero** para coisas que ja se sabe como fazer.
Ela deve **instanciar e parametrizar blocos ja verificados**.

```
1. BLUEPRINT (genero)   JSON: loop, sistemas, criterios de pronto
2. BEHAVIOR (termo)     cena + script + parametros + TESTE
3. SEED (semente)       jogo minimo completo, clonavel
```

Regra estrutural: **comportamento e componente, nao heranca.** Um componente de
vida e um no filho que se pluga em qualquer coisa. E isso que permite combinar
30 termos em milhares de jogos. Classe gigante e o erro que a IA comete sozinha.

---

## Fatia 2.A — Formato canonico e o primeiro termo

**1. O que e** Definir o formato de um comportamento e implementar **um** a mao,
completo, como padrao-ouro.

**2. Por que agora** Sem padrao-ouro, os 30 termos saem em 30 formatos diferentes.

**3. Arquivos** `behaviors/health/` (novo) · `schemas/behavior.schema.json`

**4. Fonte** *Game Development Patterns with Godot 4* (composicao sobre heranca) ·
`godot-demo-projects` · Nodot.

**5. Como fazer**

Estrutura de cada termo:
```
behaviors/<nome>/
  behavior.json     nome, descricao em linguagem natural, sinonimos PT/EN,
                    parametros (tipo, faixa, padrao), sinais emitidos,
                    dependencias, generos aplicaveis, conflitos
  <nome>.tscn       o componente
  <nome>.gd         o script
  test_<nome>.gd    teste obrigatorio
  README.md         1 paragrafo, para busca semantica
```

O `behavior.json` e o coracao: e ele que liga **linguagem natural → componente
verificado**. "Quero que o inimigo morra em 3 tiros" → busca → `health` com
`max_hp: 3`.

Implemente `health` inteiro, a mao, com teste rodando. Ele vira o molde.

**6. Armadilhas**
- Nao use heranca. Componente e no filho.
- Parametro sem faixa declarada gera valor absurdo depois.
- Nome que se confunde com outro termo degrada a busca — exija distinguibilidade.

**7. Criterios de aceite**
- `behavior.json` valida contra o schema
- O componente funciona numa cena de teste
- O teste passa com output colado
- O termo e parametrizavel sem editar codigo

**8. Como provar** Teste rodando + cena de demonstracao + JSON validado.

**9. Regressao** Nenhuma (codigo novo).

**10. Marcacao** `[SENIOR]` — define o padrao de tudo que vem depois.

---

## Fatia 2.B — Adotar o framework de teste

**1. O que e** GdUnit4 como framework oficial dos comportamentos.

**2. Por que agora** 30 termos sem teste sao 30 formas novas de quebrar.

**3. Arquivos** `addons/gdUnit4/` · `tests/` · configuracao de CI

**4. Fonte** Documentacao oficial do GdUnit4, em especial **Scene Runner**
e o tratamento de **teste instavel**.

**5. Como fazer**
Instale o framework. Configure execucao por linha de comando com relatorio.

Quatro niveis de teste por termo:
1. **Estatico** — JSON valida, script compila, nome nao colide
2. **Unitario** — logica pura (vida chega a zero → emite sinal)
3. **De cena (Scene Runner)** — simula input real e espera o sinal.
   E aqui que se prova que funciona **no jogo**
4. **De composicao** — o termo junto de outros 3 nao quebra.
   E o teste que ninguem faz e que evita a barreira dos 70%

Ligue o tratamento de teste instavel desde o inicio: jogo tem fisica e tempo,
teste que passa 9 de 10 vezes destroi a confianca na trava.

**6. Armadilhas** Teste que passaria mesmo com implementacao vazia nao vale nada.
Todo teste precisa de assert sobre comportamento, nao sobre existencia.

**7. Criterios de aceite**
- Os 4 niveis rodam no termo `health`
- Roda por linha de undo e gera relatorio
- Teste instavel e marcado, nao mascarado

**8. Como provar** Saida completa da suite.

**9. Regressao** Testes Python existentes continuam passando.

**10. Marcacao** `[SENIOR]`

---

## Fatia 2.C — Portao para comportamentos

**1. O que e** Criterio novo no `auditar.py`.

**5. Como fazer**
Adicione verificacao fail-closed: todo diretorio em `behaviors/` precisa ter
`behavior.json` valido, teste existente, e nome distinguivel dos demais
(distancia minima de similaridade). Falta qualquer um → falha.

**7. Criterios de aceite** Termo sem teste faz `auditar.py` falhar.
**8. Como provar** Crie um termo incompleto de proposito e cole a falha.
**10. Marcacao** `[AUTO]`

---

## Fatia 2.D — Parametros em recurso de dados

**1. O que e** Cada comportamento expoe seus numeros num `.tres`, nao no script.

**2. Por que agora** **E o pre-requisito do ajuste ao vivo (2.AI).** Escrever num
arquivo de dados e seguro; reescrever codigo a partir de estado de runtime nao e.

**3. Arquivos** `behaviors/*/`

**4. Fonte** Doc oficial do Godot: `Resource` e `@export`.

**5. Como fazer**
Crie um `Resource` por comportamento com os parametros exportados.
O componente le do recurso. O jogo rodando le do mesmo recurso.
Assim, mudar um numero e alterar **dados**, nunca codigo.

**6. Armadilhas** Sub-recurso pode ser substituido pela versao em cache ao salvar,
apagando a edicao. Nunca salve com o jogo rodando (ver 2.AI).

**7. Criterios de aceite** Trocar valor no `.tres` muda o jogo sem editar script.
**8. Como provar** Antes e depois, com o `.tres` colado.
**10. Marcacao** `[SENIOR]`

---

## Fatias 2.E a 2.Z — os 30 comportamentos

**Uma fatia por termo. Nunca em lote.**

Pedir "crie 30 comportamentos" produz 30 esqueletos falsos — e o padrao de falha
ja conhecido deste projeto.

**Processo por termo:**
1. Leia a implementacao de referencia na fonte (demo oficial ou GDQuest)
2. Escreva a sua versao no formato de 2.A
3. Escreva os 4 niveis de teste
4. Rode e cole o output
5. Cite a fonte que usou

**Lista inicial (30):**

| Grupo | Termos |
|---|---|
| Movimento | plataforma · top-down · primeira pessoa · veiculo |
| Combate | vida/dano · hitbox/hurtbox · projetil · cadencia · knockback · invulnerabilidade temporaria |
| Inimigo | perseguir · patrulhar · linha de visao · spawner de ondas · maquina de estados |
| Progressao | inventario · coleta · XP/nivel · upgrade · moeda |
| Sistema | save/load · pausa · menu principal · transicao de cena · audio com bus · configuracoes |
| Feedback | screen shake · texto flutuante · particula de impacto · hit stop |
| Estrutura | timer de rodada · condicao de vitoria · condicao de derrota |

**30 termos com teste valem mais que 130 sem.** Nao acelere pulando teste.

Ritmo realista: 1 a 2 termos por sessao.

**Marcacao:** `[AUTO]` para termos simples, `[SENIOR]` para os que envolvem fisica,
maquina de estados ou persistencia.

---

## Fatias 2.AA a 2.AC — composicao, blueprints e sementes

| # | Fatia | Essencial |
|---|---|---|
| 2.AA | Teste de composicao e contrato | Termos combinados nao quebram. Se um termo muda parametro, o CI acusa em todos os blueprints que o usam. Estenda o `contract_snapshot.py` existente |
| 2.AB | Blueprints de genero (3) | JSON declarativo: loop, sistemas, criterios de pronto. Reaproveite os `game_patterns` que ja existem |
| 2.AC | Jogos-semente (3) | Jogo minimo completo e comentado por genero. O Breakout ja e o primeiro |

---

## Fatias 2.AD a 2.AU — fichas resumidas

Serao expandidas pelo `/plan` quando chegar a vez.

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 2.AD | Versionamento de behaviors | Mudar um termo quebra jogos ja criados. Versao por termo + migracao | `[SENIOR]` |
| 2.AE | Memoria semantica (RAG local) | Indexar GDD, decisoes e codigo. Elimina o ritual de colar documentos | `[SENIOR]` |
| 2.AF | Indice de entidades | Mapa "inimigo" → quais nos. Sem isso, "deixa os inimigos mais rapidos" nao funciona | `[SENIOR]` |
| 2.AG | Docs do Godot offline | Ataca a causa raiz de inventar API. Complementa o `classdb_cache` | `[AUTO]` |
| 2.AH | Classificador editar-ao-vivo | Valor → arvore remota, sem reiniciar. Estrutura → reiniciar. Hoje a IA reinicia sempre | `[SENIOR]` |
| 2.AI | Ajuste ao vivo (codigo inverso) | Capturar → acumular → mostrar → **humano aprova** → parar o jogo → checkpoint → escrever no `.tres` → verificar. **Nunca escrever com o jogo rodando** | `[SENIOR]` |
| 2.AJ | Captura de erro em tempo real | `EditorDebuggerPlugin` (estruturado) + autoload de log + LSP (antes de rodar) | `[SENIOR]` |
| 2.AK | Receitas de conserto | 7 receitas cobrem a maioria: no nao encontrado · sinal para metodo inexistente · tipo incompativel · recurso ausente · autoload faltando · divisao por zero · null por ordem de init. **Automatize so a confirmacao, nunca a aplicacao** | `[SENIOR]` |
| 2.AL | Pacote de assets | Pasta + manifesto com licenca e style kit (paleta, resolucao, pivo). Fora do repo principal | `[SENIOR]` |
| 2.AM | Seguranca de asset externo | Verificar origem. A sandbox de GDScript tem bypasses conhecidos e documentados | `[SENIOR]` |
| 2.AN | Unificar taxonomias | Hoje sao 4 paralelas. Uma so, por **intencao**, 5–7 grupos: descobrir · criar · ver · testar · consertar · publicar · processo | `[SENIOR]` |
| 2.AO | Auditoria de descricoes | Descricao inchada custa token em toda requisicao e piora a escolha. Modo lean como padrao | `[AUTO]` |
| 2.AP | Ops de roteiro | "Criar inimigo completo" = 6 passos internos, 1 chamada | `[AUTO]` |
| 2.AQ | Compactacao de contexto | Resumo rolante automatico. Evita degradacao em projeto de mais de um mes | `[SENIOR]` |
| 2.AR | Roteamento de modelo | Tarefa simples no modelo barato, diagnostico no bom | `[SENIOR]` |
| 2.AS | Semente de reprodutibilidade | Mesma frase, mesmo resultado. Permite testar regressao de comportamento | `[AUTO]` |
| 2.AT | Unificar os 3 desfazer | UndoRedo + git + botao Reverter sao 3 historicos independentes hoje. Definir quem manda e mostrar **um** historico | `[SENIOR]` |
| 2.AU | Orcamento de tempo por gate | Gate de 3 minutos ninguem usa. Teto de tempo + modo rapido/completo | `[AUTO]` |

DOC2"""[len('DOC2'):-len('DOC2')]

DOCUMENTOS['ONDA_3_4_qualidade_mundo.md'] = r"""DOC3
---
applyTo: '**'
---

# ONDAS 3 e 4 — QUALIDADE DE JOGO e MUNDO

---

# ONDA 3 — QUALIDADE DE JOGO

**Objetivo:** o MCP passa a opinar se o jogo esta **bom**, nao so se compila.
**Criterio de saida:** o relatorio automatico acusa pelo menos um problema real
de design num jogo de teste, confirmado depois por playtest humano.

Este e o segundo fosso do produto. Todo concorrente verifica codigo.
Nenhum critica design.

---

## O que a pesquisa estabelece (base das fatias 3.A a 3.G)

**Playtest manual nao escala.** Testar um jogo grande a mao chega a centenas de
milhares de horas. Bots por script tambem tem teto: nao aprendem, exigem
especialista para escrever, e certos casos nao sao scriptaveis.

**Agentes conseguem substituir parte do playtest humano.** Agentes de IA jogando
funcionam como proxy de testador para mapear curva de dificuldade e balanceamento,
com desempenho correlacionado as avaliacoes humanas.

**Nao existe medidor de diversao — existem proxies.** O mais forte e a relacao
entre **taxa de abandono** e **taxa de aprovacao** de fase. Prever abandono medio
serve para corrigir fases pouco engajantes **antes** de lancar.

**O vale e mais perigoso que o pico.** Trecho sem desafio esvazia o engajamento em
silencio: o jogador nao abandona com raiva, ele se afasta. Esse abandono por tedio
e mais lento e mais dificil de diagnosticar que o por frustracao.
O relatorio precisa acusar **os dois**.

**A curva inicial decide tudo.** Retencao dos primeiros dias correlaciona
fortemente com como se sentem as primeiras sessoes.

---

## Fatia 3.A — Playtest camada 1: smoke automatico

**5. Como fazer** Rodar o jogo sem interface grafica e verificar: abre, nao trava,
FPS minimo, console sem erro. Custo quase zero — a maior parte ja existe no MCP.

**7. Criterios** Jogo quebrado e reprovado; jogo saudavel passa. **Marcacao** `[AUTO]`

---

## Fatia 3.B — Playtest camada 2: personas scriptadas

**5. Como fazer** Use o Scene Runner do GdUnit4 para simular input real e esperar
sinais. Tres personas fixas: **apressado** (avanca sempre), **cauteloso**
(espera, evita risco), **explorador** (testa os limites do cenario).

Cada persona gera: terminou ou nao, tempo, tentativas, caminho percorrido.

Isto sozinho cobre a maior parte do valor do playtest automatizado.

**6. Armadilhas** Teste instavel e regra, nao excecao — ligue o tratamento de
flaky desde o inicio.

**7. Criterios** As 3 personas rodam num jogo-semente e produzem metrica.
**Marcacao** `[SENIOR]`

---

## Fatia 3.C — Playtest camada 3: agente LLM pontual

**5. Como fazer** O MCP envia screenshot e estado; o modelo decide a acao.
Caro em token → use pontualmente (validar um nivel novo), **nunca** continuamente.

**Aprendizado por reforco fica fora de escopo permanente:** custo altissimo,
retorno baixo para jogo indie pequeno.

**7. Criterios** Roda sob demanda, com custo estimado antes de comecar.
**Marcacao** `[SENIOR]`

---

## Fatia 3.D — `fun_report`

**1. O que e** Relatorio com os quatro sinais medidos por agentes, sem jogador humano.

**5. Como fazer**

| Sinal | Como medir | O que indica |
|---|---|---|
| Taxa de aprovacao | % de agentes que terminam | Facil demais (>95%) ou frustrante (<20%) |
| Tentativas ate vencer | media e desvio | Pico de dificuldade escondido |
| Variedade de estrategia | quantas rotas distintas vencem | Estrategia degenerada (uma domina) |
| Escalada | comparar inicio, meio e fim | Repeticao sem progressao |

Os quatro mapeiam exatamente nos quatro modos de falha do core loop:
**sem escalada · sem escolha real · recompensa distante demais · estrategia degenerada.**

O relatorio **nomeia o modo de falha**, nao diz "esta chato".
Errado: "o nivel 3 esta ruim".
Certo: "nivel 3 sem escalada: a decima onda e igual a primeira".

**6. Armadilhas — honestidade e vantagem competitiva.**
O relatorio precisa dizer, com todas as letras: *isto mede indicios de engajamento,
nao diversao; playtest humano continua necessario.* Quem promete "medidor de
diversao" perde credibilidade no primeiro teste.

Acuse tambem o **vale**, nao so o pico.

**7. Criterios** Num jogo com problema plantado de proposito, o relatorio acusa
o modo de falha certo. **Marcacao** `[SENIOR]`

---

## Fatia 3.E — Gate dos primeiros 5 minutos

**2. Por que** E a maior alavanca de retencao que existe.

**5. Como fazer** Rodar as personas so no comeco do jogo e exigir: a pessoa
entende o que fazer, tem uma vitoria pequena, e nao morre repetidamente antes
de entender. Bloqueia avanco de fase se falhar.

**Marcacao** `[SENIOR]`

---

## Fatias 3.F a 3.K — resumidas

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 3.F | Gate de divida de complexidade | Codigo assistido por IA acumula complexidade e warnings que nao voltam a cair. Medir por fase e travar crescimento sem justificativa | `[SENIOR]` |
| 3.G | Gate de design do core loop | Os 4 modos de falha viram checklist automatico | `[SENIOR]` |
| 3.H | Modo professor | Depois de gerar, explicar em 3 linhas o que foi feito e por que. Reduz dependencia da IA | `[AUTO]` |
| 3.I | O "primeiro nao" bem feito | "MMO open world" nao pode receber "nao da". Recebe: "isso sao 2 anos; a versao de 2 semanas e X — topa?" | `[SENIOR]` |
| 3.J | Disclosure de conteudo IA | A Steam exige declarar uso de IA na publicacao. O produto inteiro gera conteudo por IA. Sem isso, voce entrega usuarios a uma rejeicao | `[AUTO]` |
| 3.K | Modo revisor adversarial | Em fatia critica, o Agente 2 audita em vez de implementar. Metade da velocidade, ataca o problema numero um: evidencia fabricada | `[SENIOR]` |

---

# ONDA 4 — MUNDO

**Objetivo:** outras pessoas descobrem, usam e sustentam o projeto.
**Criterio de saida:** 3 jogos publicados por pessoas que nao sao voce.

---

## O que a pesquisa estabelece

**Comunidade nao cresce por feature, cresce por prova.** A coisa mais persuasiva
nao e documentacao: e **publicar um jogo feito com a ferramenta**. Ferramenta de
gamedev se vende pelo jogo que produziu.

**Canais que funcionam:** AssetLib oficial (instalacao de dentro do editor, exige
licenca aberta) · itch.io (publicar sem custo, "pague quanto quiser") ·
redes com GIF curto de gameplay · comunidades de Godot e gamedev · game jam.

**Monetizacao viavel para solo:** patrocinio recorrente com camadas **especificas**
("resposta a issue em 48h" converte muito mais que "apoie meu trabalho") ·
open core (nucleo aberto, pacotes de assets e blueprints pagos) · venda de assets
fora da AssetLib, que so aceita licenca aberta.

**Nao viavel agora:** servico hospedado e consultoria — consomem o tempo que
voce nao tem.

---

## Fatias 4.A a 4.G

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 4.A | Publicar na AssetLib | **Bloqueado ate a Fatia 0.E (LICENSE) existir** | `[AUTO]` |
| 4.B | itch.io | Pacotes de assets e templates. Canal para o que nao cabe na AssetLib | `[AUTO]` |
| 4.C | Patrocinio com camadas | Beneficio nomeado, nunca generico | `[AUTO]` |
| 4.D | Nome e identidade | `mcp-godot-desenvolvimento` descreve, nao vende, e nao e pesquisavel | `[SENIOR]` |
| 4.E | Publicar o Shardbreaker | **A prova mais forte que existe.** Publique o jogo e mostre o processo | `[SENIOR]` |
| 4.F | Canal de comunidade | Discussions ou Discord + `CONTRIBUTING` (ja feito em 0.E) | `[AUTO]` |
| 4.G | Metrica de produto | **Quantas pessoas terminam um jogo.** Definir e medir. Terminar vale mais que gerar | `[SENIOR]` |

---

## Ordem sugerida da Onda 4

1. LICENSE (ja na Onda 0) — destrava tudo
2. Publicar o Shardbreaker — a prova
3. AssetLib — o canal de instalacao
4. Comunidade — onde as pessoas pedem socorro
5. Patrocinio — so depois de existir gente usando
6. Nome — quando houver o que nomear

Patrocinio antes de usuario nao funciona. Nome antes de produto tambem nao.

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
    log("\n[1/3] Conferindo os lotes anteriores")
    faltam = []
    if not (ROOT / "ROADMAP_DEFINITIVO.md").exists():
        faltam.append("Lote 1 (instalar.py)")
    if not (ROOT / ".github/prompts/plan.prompt.md").exists():
        faltam.append("Lote 2 (instalar_comandos.py)")
    if not (ROOT / ".github/instructions/fontes.instructions.md").exists():
        faltam.append("Lote 3 (instalar_personas.py)")
    if faltam:
        aviso("Faltam: " + ", ".join(faltam))
        return False
    ok("Lotes 1, 2 e 3 encontrados")
    return True


def passo_2_escrever() -> None:
    log("\n[2/3] Escrevendo as fichas das ondas")
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
    if TESTE:
        ok("[teste] verificacao pulada")
        return
    for nome in DOCUMENTOS:
        arq = ROOT / DESTINO / nome
        if not arq.exists():
            aviso(f"{nome} nao foi criado")
            continue
        txt = arq.read_text(encoding="utf-8", errors="replace")
        if not txt.startswith("---"):
            aviso(f"{nome} sem frontmatter na primeira linha")
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
INSTALACAO COMPLETA - os 4 lotes estao no lugar.

PROXIMOS PASSOS:

  1. Confira:   git status
  2. Commite:   git add -A
                git commit -m "docs: fichas detalhadas das ondas"
  3. REINICIE O VS CODE

  COMO COMECAR:
    No chat do Copilot, escolha o agente 'implementador'
    e digite:  /plan

    A IA vai ler o roadmap, escolher a Fatia 0.A e te apresentar
    o plano. Voce aprova, ela roda /act.

  PRIMEIRA FATIA: 0.A - confirmar a correcao do bug do Passo 8.
""")


def main() -> int:
    global TESTE
    ap = argparse.ArgumentParser(description="Lote 4 - fichas das ondas")
    ap.add_argument("--teste", action="store_true", help="simula, nao altera nada")
    args = ap.parse_args()
    TESTE = args.teste

    log("=" * 62)
    log("  INSTALADOR DO ROADMAP - Lote 4")
    log(f"  Pasta: {ROOT}")
    if TESTE:
        log("  MODO TESTE - nada sera alterado")
    log("=" * 62)

    if not passo_1_prereq() and not TESTE:
        log("\nAbortado. Instale os lotes anteriores primeiro.")
        return 1

    passo_2_escrever()
    passo_3_verificar()
    relatorio()
    return 0


if __name__ == "__main__":
    sys.exit(main())
