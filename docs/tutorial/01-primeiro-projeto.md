# Tutorial 1: Seu primeiro projeto

**Tempo estimado:** 10 minutos
**Pré-requisito:** nenhum
**O que você vai ter no final:** Um projeto Godot aberto, com o MCP conectado e pronto para começar.

---

## Antes de começar

Você precisa do arquivo `init.py`. Ele está na pasta do MCP Godot Agent.

**Se você ainda não tem a pasta no seu computador:**

1. Vá até https://github.com/seu-usuario/mcp-godot-desenvolvimento
2. Clique no botão verde **Code** e depois em **Download ZIP**
3. Extraia o ZIP para uma pasta (ex: `C:\MeuJogo`)
4. Abra o terminal **dentro dessa pasta**

**Se você já tem a pasta**, abra o terminal dentro dela e pule para o Passo 1.

---

## Passo 1: Instalar tudo

Abra o terminal (PowerShell) e cole:

```
python init.py
```

**O que vai acontecer:** O instalador procura Godot e Python no seu computador,
cria o ambiente, configura a conexão com o VS Code, e abre o editor do Godot.

**Confira:** Você deve ver `[OK]` em cada linha. Se aparecer `[FALHA]`, leia a
mensagem — ela explica o que fazer em português.

---

## Passo 2: Ver o estado inicial

No chat do VS Code, diga:

```
qual e o proximo passo?
```

**O que vai acontecer:** O MCP mostra a fase atual do projeto, o que já
foi feito, e qual é o próximo passo.

**Confira:** A resposta deve mostrar `fase: IDEIA` e uma mensagem de boas-vindas.

---

## Passo 3: Descrever seu jogo

No chat, descreva o jogo que você quer fazer. Use linguagem natural — escreva
como se estivesse contando para um amigo. Por exemplo:

> "Quero um jogo de plataforma 2D com um herói que pula e atira. O jogo tem
> 5 fases, cada uma com um chefão no final. O visual é pixel art colorido."

**O que vai acontecer:** O MCP entende sua ideia e monta um plano inicial.

**Confira:** O MCP responde com um resumo do que entendeu. Se algo estiver
errado, diga "não, eu queria..." e explique de novo.

---

## Passo 4: Ver o plano

Digite:

```
/plan
```

**O que vai acontecer:** O MCP mostra o plano completo: o que vai construir,
em que ordem, e quais ferramentas vai usar.

**Confira:** Você vê a lista de etapas na tela. Leia com calma — é aqui que
você decide se o plano faz sentido antes de começar a construir.

---

## Passo 5: Começar

Se o plano estiver bom, digite:

```
/act
```

**O que vai acontecer:** O MCP começa a construir. O painel do Godot (lado direito)
mostra o progresso — a fase atual, o que está sendo feito, e o próximo passo.

**Confira:** O painel do Godot mostra a fase atual e o semáforo está verde.

---

## Se algo der errado

- **O terminal diz que não encontrou o Python:** Você precisa instalar o Python.
  Vá em python.org, baixe a versão 3.12 e marque "Add Python to PATH".
- **O Godot não abriu:** O instalador pode não ter encontrado o Godot.
  Baixe o Godot 4.7 em godotengine.org e tente de novo.
- **O chat não responde:** Verifique se o VS Code está com a extensão do
  Copilot instalada e ativa.

---

## Pronto!

Você instalou o MCP, criou seu primeiro projeto, descreveu seu jogo e começou
a construir. No próximo tutorial, você vai criar sua primeira cena com personagem.
