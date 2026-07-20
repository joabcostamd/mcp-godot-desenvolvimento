---
applyTo: '**'
---

# 08 — CAMADA 7 — POLIMENTO FINO [MARGINAL]

> Lê-se junto com `00-mestre.md`. **Toda esta camada é [MARGINAL] e a orientação é ADIAR.** Corresponde à Fase 4 do roadmap original. São refinamentos e recursos de fim de ciclo / pós-lançamento — só fazem sentido quando o jogo (ou o MCP) está maduro e perto de lançar. Fazer isto cedo é refinamento antes da hora.

**Regra desta camada:** a IA **não implementa nenhuma fatia sem confirmação humana explícita.** A maioria só faz sentido em contexto específico (pós-lançamento, projeto grande, multiusuário). Ao chegar aqui, listar e perguntar.

Formato enxuto. Spec detalhada gerada sob demanda quando (e se) confirmada.

---

## FATIA 7.1 — Detecção de vazamento de memória em sessão longa **[MARGINAL]**
- `memory_leak_detect`. Liga a `profile_memory`. Vale para jogo com sessão longa; usa perf regression (2.6).

## FATIA 7.2 — Migração de versão de engine **[MARGINAL]**
- `migrate_godot_version`. Só quando você for subir de versão do Godot. Ponto no tempo, não contínuo.

## FATIA 7.3 — Grafo de dependência entre addons **[MARGINAL]**
- `addon_dependency_graph`. Útil em projeto com muitos addons. Liga a supply-chain (4.5).

## FATIA 7.4 — Modo somente-leitura no início de projeto novo **[MARGINAL]**
- Trava por código no começo (forçar leitura/planejamento antes de escrever). Liga à filosofia de processo, mas pode atritar. Questionar se ajuda ou irrita.

## FATIA 7.5 — Trava de branch (bloquear escrita direta na main) **[MARGINAL]**
- Complementa git safety (0.5). Baixo custo se você usa branches; inútil se trabalha direto na main.

## FATIA 7.6 — Orçamento de tokens/custo em tempo real **[MARGINAL]**
- `session_budget_status`. Liga ao rastreio de custo do cliente HTTP (0.9) e ao governador (0.14). Parte disso já vem de graça daquelas fatias; esta é a visão em tempo real.

## FATIA 7.7 — Simulação de diff antes de edição em lote **[MARGINAL]**
- Prever o que uma edição em lote vai mudar antes de aplicar. Liga a checkpoint (0.5). Reduz risco de edição em lote; valor médio.

## FATIA 7.8 — Paridade de input (teclado/controle/touch) **[MARGINAL]**
- Checar que toda ação funciona nos três. Vale se o jogo é multiplataforma de input.

## FATIA 7.9 — Relator de crash pós-lançamento **[MARGINAL]**
- `crash_reporter_configure` + reprodução de crash a partir de telemetria real. Só faz sentido pós-lançamento. Liga a telemetria (5.4).

## FATIA 7.10 — Conformidade de privacidade para telemetria **[MARGINAL]**
- `privacy_compliance_check` (GDPR/COPPA). Obrigatório SE tiver telemetria (5.4). Não fazer telemetria sem isto.

## FATIA 7.11 — Definition-of-ready **[MARGINAL]**
- `definition_of_ready_check` — checklist de entrada da fase de design. On-brand (processo), mas refinamento. Liga ao scope_guard (1.13).

## FATIA 7.12 — Live ops **[MARGINAL]**
- Feature flags (parte já vem do kill switch 0.12), patch notes automático, análise de sentimento de reviews, teste A/B. Tudo pós-lançamento, para jogo em serviço. Escopo grande; só para jogo live-service.

## FATIA 7.13 — Build matrix multiplataforma **[MARGINAL]**
- Testar build em várias plataformas de uma vez. Vale perto do lançamento multiplataforma. Liga ao export gate (Feature 9).

## FATIA 7.14 — Resolução de conflito de edição multiusuário **[MARGINAL]**
- Dois devs/agentes na mesma cena. Só faz sentido em time, não solo. Para o seu caso (solo), provavelmente escopo morto — a não ser multi-agente (liga a 4.6).

---

## ORIENTAÇÃO PARA A IA NESTA CAMADA

Ao chegar na Camada 7:
1. **Não implemente nada automaticamente.**
2. Diga ao humano: "Esta é a camada de polimento fino / pós-lançamento. A orientação é adiar — a maioria só faz sentido quando o projeto está maduro ou perto de lançar."
3. Se o humano quer algo aqui, confirme o contexto (ex.: "vai ter telemetria?" antes de 7.9/7.10; "trabalha em branches?" antes de 7.5).
4. Para as confirmadas, spec sob demanda + fluxo normal do mestre.

Dependências úteis a lembrar: 7.10 é pré-requisito de qualquer telemetria (5.4). 7.6 e 7.12(flags) reusam infra já feita (0.9, 0.12). 7.14 só para multi-agente/time.

---

*Fim da Camada 7. Último documento: `09-glossario-referencias.md` + o prompt de início.*
