---
applyTo: '**'
---

# ONDA 0 — DESTRAVAR

**Objetivo:** consertar o que esta quebrado ou contraditorio antes de construir por cima.
**Criterio de saida:** `auditar.py` passa, `/plan` e `/act` funcionam, zero referencia a
IA agêntica (Copilot) fora de `journal/`, LICENSE existe, numeros dos documentos batem com o codigo.

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
nos **dois** ramos. Confirme que nao existe mais `.github/instructions/workflows/act.md`.
Se existir, mova para `journal/`.

**6. Armadilhas** Nao edite o `act.prompt.md` do Lote 2 — ele ja esta correto.

**7. Criterios de aceite**
- `.github/instructions/` nao existe
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

## Fatia 0.D — Migracao `.github/instructions` e expurgo de IA agêntica (Copilot)

**1. O que e** Trocar toda mencao a IA agêntica (Copilot) por "IA agentica (Copilot)".

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
- `.github/instructions` → `.github/instructions`
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

