# Modo Professor — MCP Godot Agent (FATIA 3.H)

> Explica o que foi feito, por que foi feito, e como foi feito.

## O que é

O Modo Professor é uma funcionalidade onde o MCP explica cada decisão
de design e implementação para o usuário, como um professor faria.

## Ativação

No prompt do MCP:
> "Explique o que você acabou de fazer no meu jogo."

Ou via tool:
> `explain_last_action()` — explica a última ação
> `explain_scene("game.tscn")` — explica a estrutura de uma cena
> `explain_behavior("health")` — explica um behavior específico

## Formato da Explicação

Cada explicação segue este template:

```
## O que foi feito
[1-2 frases descrevendo a ação em linguagem simples]

## Por que foi feito
[Contexto: qual problema isso resolve, por que essa abordagem]

## Como foi feito
[Detalhes técnicos: quais tools foram usadas, quais behaviors,
 qual a arquitetura resultante]

## O que você pode fazer agora
[Próximos passos sugeridos para o usuário]
```

## Exemplos

### Exemplo 1: Adicionar sistema de vida

```
## O que foi feito
Adicionei um sistema de vida ao seu personagem. Agora ele tem 100 HP
e morre quando chega a 0.

## Por que foi feito
Sem sistema de vida, o jogo não tem desafio. O jogador precisa
sentir risco para se engajar.

## Como foi feito
Usei o behavior `health` (behaviors/health/):
- max_hp = 100, current_hp = 100
- damageable = true, killable = true
- Sinal `died` conectado à cena game_over.tscn
- HUD atualizado com `health_bar` para mostrar corações

## O que você pode fazer agora
- Ajuste o max_hp para 50 se quiser mais difícil
- Adicione `collectable` para poções de cura
- Use `invulnerability` para tempo de invencibilidade após dano
```

### Exemplo 2: Criar inimigo que patrulha

```
## O que foi feito
Criei um inimigo Slime que patrulha entre dois pontos.

## Por que foi feito
Inimigos estáticos são previsíveis. Patrulha cria desafio espacial:
o jogador precisa observar o padrão e escolher o momento certo.

## Como foi feito
Usei `enemy_patrol` + `enemy_chase`:
- waypoints: [Vector2(200,100), Vector2(400,100)]
- speed: 60, wait_time: 1.0s
- chase_range: 150px (persegue se jogador chegar perto)
- health filho com 30 HP (morre em 3 hits)

## O que você pode fazer agora
- Aumente chase_range para 300 para inimigo mais agressivo
- Adicione `screen_shake` ao matar o inimigo
- Use `spawner_wave` para criar ondas de slimes
```
