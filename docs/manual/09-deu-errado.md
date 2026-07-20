# Quando algo dá errado

Erros acontecem. Aqui estão os mais comuns, explicados
em português simples — sem linguagem técnica.

## O projeto Godot não foi encontrado na pasta atual.

Sem o projeto, o MCP não sabe onde criar cenas e scripts.
Use 'create_project' para criar um novo ou 'set_active_project' para abrir um existente.

---

## O jogo não tem uma cena principal definida.

Isso significa que o Godot não sabe qual cena abrir quando o jogo inicia — o jogo não roda.
Use 'set_main_scene' para definir a cena que abre primeiro.

---

## O jogo não tem uma cena principal definida.

Isso significa que o Godot não sabe qual cena abrir quando o jogo inicia — o jogo não roda.
Use 'set_main_scene' para definir a cena que abre primeiro.

---

## O arquivo que você tentou acessar não existe.

O jogo depende desse arquivo para funcionar — sem ele, algo vai quebrar.
Verifique se o caminho está correto ou crie o arquivo primeiro.

---

## O que você está procurando não foi encontrado no projeto.

Pode ser que esse elemento ainda não tenha sido criado.
Crie o elemento primeiro e depois tente acessá-lo.

---

## Já existe algo com esse nome no projeto.

Godot não permite dois recursos com o mesmo nome na mesma pasta — isso causaria conflitos.
Escolha outro nome ou remova o existente primeiro.

---

## O elemento que você está tentando acessar não existe na cena atual.

Isso significa que o script ou cena tenta usar algo que não está mais lá.
Use 'load_scene_tree' para ver todos os elementos disponíveis na cena.

---

## O elemento que você está tentando acessar não existe na cena atual.

Isso significa que o script ou cena tenta usar algo que não está mais lá.
Use 'add_node' para criar o elemento primeiro.

---

## O tipo de elemento que você pediu não existe no Godot 4.7.

Isso geralmente é um erro de digitação no nome da classe.
Use 'list_valid_node_types' para ver os tipos disponíveis.

---

## O código GDScript do jogo tem um erro de escrita (sintaxe).

Isso impede o jogo de rodar — o Godot não consegue entender o script.
Isso geralmente é um bug do MCP ao gerar código. Peça para a IA revisar e corrigir o script.

---

## O jogo encontrou um erro durante a execução.

Isso acontece quando uma cena tenta acessar algo que foi removido ou nunca existiu.
Use 'compile_test' para ver os erros exatos e corrija a referência quebrada.

---

## A operação demorou muito e foi cancelada por segurança.

Isso pode acontecer se o projeto estiver muito grande ou o Godot estiver sobrecarregado.
Tente de novo. Se persistir, reinicie o Godot ou reduza o tamanho do projeto.

---

## A operação demorou muito e foi cancelada por segurança.

Isso pode acontecer se o projeto estiver muito grande ou o Godot estiver sobrecarregado.
Tente de novo com um projeto menor ou reinicie o Godot.

---

## Não foi possível conectar ao editor do Godot.

Sem essa conexão, o MCP não consegue comunicar com o editor para executar operações.
Verifique se o Godot está aberto com o plugin MCP Addon ativo (Project → Project Settings → Plugins).

---

## A ponte de comunicação com o Godot não está ativa.

Sem a bridge, o MCP fica isolado — não consegue ler nem modificar o projeto.
Abra o Godot e ative o plugin MCP Addon em Project → Project Settings → Plugins.

---
