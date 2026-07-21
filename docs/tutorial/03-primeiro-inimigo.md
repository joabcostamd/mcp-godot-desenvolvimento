# Tutorial 3: Seu primeiro inimigo

**Tempo estimado:** 20 minutos
**Pré-requisito:** Tutorial 2 concluído (cena com personagem controlável)
**O que você vai ter no final:** Um inimigo que persegue o jogador, com colisão e dano.

---

## Passo 1: Adicionar um inimigo

No chat:

```
criar um inimigo — circulo vermelho que persegue o jogador
```

**O que vai acontecer:** O MCP cria um inimigo com:
- Um círculo vermelho visível
- Comportamento de perseguição (anda na direção do jogador)
- Colisão com o jogador

**Confira:** Você vê um círculo vermelho na tela do Godot, em uma posição
diferente do personagem.

---

## Passo 2: Testar a perseguição

Aperte **F5** para rodar o jogo.

**O que vai acontecer:** O círculo vermelho começa a se mover na direção do
seu personagem.

**Confira:** Quando você move o personagem, o inimigo segue. Se o inimigo
ficar parado, volte ao chat e diga "o inimigo não está me perseguindo".

---

## Passo 3: Adicionar dano

Agora faça o inimigo causar dano:

```
configurar dano: quando inimigo encosta no jogador, perde 1 de vida
```

**O que vai acontecer:** O MCP adiciona um sistema de vida ao personagem e
configura o inimigo para causar dano ao tocar.

**Confira:** Rode o jogo (F5). Quando o inimigo encosta em você, algo acontece —
uma mensagem, um número, ou o personagem pisca.

---

## Passo 4: Usar o botão Reverter

Se algo der errado, o painel do MCP tem um botão **Reverter**. Experimente:

1. Mude algo simples — por exemplo, peça "mude a cor do inimigo para roxo"
2. Se não gostar do resultado, clique **Reverter** no painel do MCP

**O que vai acontecer:** O MCP desfaz a última mudança. O painel mostra para
onde você voltou: "volta para antes de 'mudar cor do inimigo'".

**Confira:** O inimigo volta à cor anterior.

---

## Se algo der errado

- **O inimigo não persegue:** Diga "o inimigo não está se movendo na direção do jogador".
- **O dano não funciona:** Diga "o jogador não está perdendo vida quando encosta no inimigo".
- **O botão Reverter não aparece:** Verifique se o painel do MCP está visível
  no lado direito do Godot. Se não estiver, o plugin pode não estar ativo.

---

## Pronto!

Você adicionou um inimigo com perseguição e dano, e aprendeu a desfazer mudanças.
No próximo tutorial, você vai publicar seu jogo.
