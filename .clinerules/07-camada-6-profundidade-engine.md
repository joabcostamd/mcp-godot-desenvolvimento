# 07 — CAMADA 6 — PROFUNDIDADE DE ENGINE [MARGINAL / Campo A]

> Lê-se junto com `00-mestre.md`. **AVISO FORTE DA AUDITORIA:** esta é a camada mais perigosa do roadmap — não por risco técnico, mas por risco **estratégico**. É "Campo A": profundidade bruta de engine, onde os MCPs concorrentes (tugcantopaloglu 149 tools, godot-mcp-pro 175 tools) já ganham de você e crescem toda semana. **Perseguir paridade aqui dilui o seu fosso** (ser o único MCP que é dono do processo) e você nunca vence essa corrida — eles têm dezenas de tools só de engine e mais surgem constantemente.

**A auditoria recomenda: quase tudo aqui deve ser pulado conscientemente.** Só faça uma fatia se houver uma razão explícita e concreta do jogo que você está construindo. "Seria legal ter" não é razão suficiente — isso é a definição de scope creep que mata projeto solo.

**Regra desta camada:** a IA **não implementa nenhuma fatia sem confirmação humana explícita + justificativa concreta** de por que o jogo específico precisa. Ao chegar aqui, a IA lista e alerta.

---

## FATIA 6.1 — Skeleton IK / bone pose **[MARGINAL — a única com valor real]**
- SkeletonIK3D, get/set bone pose.
- **Por que é a exceção:** liga direto ao auto-rig de arte (Camada 3) e à animação de personagem. É a única fatia desta camada que fortalece o fosso (criação), em vez de só empatar engine. Se você tem personagens 3D animados, sobe de prioridade.
- Rollup provável: op em `anim_manage`.

## FATIA 6.2 — 3D depth **[MARGINAL / Campo A]**
- CSG, MultiMeshInstance3D, procedural mesh (ArrayMesh), GI (VoxelGI/LightmapGI), ReflectionProbe/Decal/FogVolume, Sky procedural/físico, camera attributes (DOF/exposição).
- **Questionar:** só vale se 3D for foco explícito e sério. Para jogo 2D ou 3D simples, é escopo morto. O concorrente já tem tudo isso; você não ganha nada competindo aqui.
- Rollup provável: `d3_manage` (ops).

## FATIA 6.3 — Física **[MARGINAL / Campo A]**
- Joints (pin/spring/hinge/cone/slider), body config (massa/atrito/bounce/damping), Area2D/3D queries, point/shape intersection.
- **Questionar:** jogo pequeno raramente precisa de joints. **[verificar no inventário 0.1]** o que `physics_manage` já cobre antes de qualquer coisa.
- Rollup provável: `physics_manage` (ops).

## FATIA 6.4 — UI granular **[MARGINAL / Campo A]**
- Tree, ItemList/OptionButton, TabContainer/TabBar, PopupMenu/MenuBar, ProgressBar/Slider/SpinBox/ColorPicker, Popup/Dialog/Window, LineEdit/TextEdit/RichTextLabel, foco/anchors/tooltip.
- **Questionar:** só vale se o jogo tem menu/UI complexo. **[verificar no inventário 0.1]** o que `ui_manage` já cobre.
- Rollup provável: `ui_manage` (ops).

## FATIA 6.5 — Rede **[MARGINAL / Campo A]**
- RPC, WebSocket client, validação anti-cheat, netcode dedicado (multiplayer_setup_enet, dedicated_server_export), lobby/matchmaking.
- **Questionar:** multiplayer é um projeto de meses se feito de verdade (era Fase 3 do roadmap original). Jogo single-player solo não precisa. Só se o jogo é multiplayer por design central.
- Rollup provável: novo `network_ops`.

## FATIA 6.6 — Runtime signals **[MARGINAL / Campo A]**
- connect/disconnect/emit signal em runtime.
- **Questionar:** útil para testar comportamento sem reiniciar. Valor médio. Liga ao `analyze_signal_flow`/`watch_signal` que já existem.
- Rollup provável: op em `debugger_ops`.

## FATIA 6.7 — Render settings **[MARGINAL / Campo A]**
- MSAA/FXAA/TAA, scaling mode/scale.
- **Questionar:** baixa prioridade. Config de render raramente é gargalo no desenvolvimento solo.
- Rollup provável: op em `config_manage`.

## FATIA 6.8 — C#/.NET scaffold **[MARGINAL / Campo A]**
- Scaffold completo de projeto .NET; suporte a script C# equivalente ao fluxo GDScript.
- **Questionar:** só vale se você programa em C#, não GDScript. Você já tem `build_csharp`. Scaffold completo é esforço grande para um público que pode ser zero no seu caso.
- Rollup provável: novo `csharp_ops` ou expansão do existente.

---

## ORIENTAÇÃO PARA A IA NESTA CAMADA

Ao chegar na Camada 6:
1. **Não implemente nada automaticamente.**
2. Alerte o humano: "Esta é a camada Campo A. A auditoria recomenda pular quase tudo — competir em profundidade de engine dilui o diferencial do MCP e é uma corrida que os concorrentes de 149–175 tools já ganham."
3. Liste as fatias. Destaque a 6.1 (skeleton IK) como a única que fortalece o fosso.
4. Para qualquer outra, exija do humano uma **justificativa concreta do jogo** (não "seria bom ter"). Sem justificativa concreta, não faça.
5. Para as confirmadas, primeiro **verificar no inventário 0.1** o que o rollup relevante já cobre — muita coisa aqui pode já existir escondida.

Este é o ponto do roadmap onde a disciplina de escopo mais importa. A tentação é grande (a lista de gaps de engine é sedutora e mensurável). Resista a ela conscientemente — é literalmente o conselho da auditoria.

---

*Fim da Camada 6. Próximo documento: `08-camada-7-polimento.md`.*
