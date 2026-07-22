---
name: pesquisa
description: 'Protocolo de pesquisa externa sistemática. Use ao iniciar fatia com tecnologia nova, quando /plan revela lacuna de conhecimento, ou quando a ficha da fatia exige consulta a fontes externas. Cobre: fontes obrigatórias, saturação, avaliação técnica, pesquisa de problemas, implementações reais, e auto-auditoria.'
---

# Protocolo de Pesquisa — MCP Godot Agent

> **Este arquivo é a fonte canônica do protocolo de pesquisa.**
> O comando `/pesquise` executa este protocolo integralmente.
> Atualize este arquivo para evoluir o comportamento do comando.

---

## 1. PRINCÍPIOS FUNDAMENTAIS

### 1.1 O que pesquisamos
Pesquisa externa é **revisão sistemática de engenharia de software e estado da arte**,
nunca pesquisa convencional. O objetivo é construir a base de conhecimento mais completa,
confiável, atualizada e aplicável possível para enriquecer o projeto.

### 1.2 Quando pesquisar
- Ao iniciar uma fatia que envolve tecnologia nova ou pouco conhecida
- Quando o `/plan` revela lacuna de conhecimento
- Quando `auditar.py` sugere melhoria que depende de referência externa
- Quando o usuário executa `/pesquise`
- Quando a fatia exige consulta a fontes externas (campo "Fonte" da ficha)

### 1.3 O que NÃO é pesquisa externa
- Ler arquivos do próprio projeto (isso é contexto, não pesquisa)
- Buscar no `classdb_cache/` (isso é consulta local)
- Revisar código do próprio repositório (isso é auditoria)

---

## 2. CICLO DE PESQUISA (iterativo até saturação)

### 2.1 Fase 0 — Determinar o alvo

1. Ler `.roadmap_progress.json` → identificar a fatia ativa (primeira `status != concluida`)
2. Ler `docs/ROADMAP_DEFINITIVO.md` → confirmar a ordem e dependências
3. Ler a ficha da fatia em `.github/roadmap/ONDA_*.md` → extrair o campo "Fonte"
4. Ler `docs/PESQUISA_EXTERNA.md` → verificar o que já foi pesquisado sobre este tema
5. Se a ficha tem fonte explícita ("Fonte: Doc do Godot sobre X"): **a fonte é o ponto de partida**
6. Se a ficha diz "Fonte: Nenhuma externa": pesquisar temas adjacentes que possam enriquecer a implementação

### 2.2 Fase 1 — Pesquisa primária (fontes obrigatórias)

Consultar, nesta ordem:

| Prioridade | Fontes |
|---|---|
| 🔴 Obrigatória | Documentação oficial (Godot 4.7, MCP Spec, Python 3.12+) |
| 🔴 Obrigatória | Especificações técnicas, RFCs, standards |
| 🟠 Alta | Código-fonte oficial (godotengine/godot, modelcontextprotocol) |
| 🟠 Alta | Repositórios open source maduros (GdUnit4, LimboAI, Nodot) |
| 🟡 Média | Artigos técnicos, whitepapers, post-mortems |
| 🟡 Média | Blogs de engenharia (Godot, MCP, VS Code) |
| 🟢 Complementar | Discussões técnicas (GitHub issues, PRs, fóruns) |
| 🟢 Complementar | Estudos de caso, benchmarks, tutoriais oficiais |

### 2.3 Fase 2 — Expansão e saturação

**Nunca encerrar nas primeiras descobertas.** Refinar iterativamente:

1. Após cada rodada de pesquisa, listar o que foi descoberto
2. Identificar lacunas: o que ainda não está claro?
3. Refinar palavras-chave, abordagens, fontes
4. Nova rodada com consultas mais específicas
5. Repetir até **saturação**: novas pesquisas não produzem conhecimento relevante novo

### 2.4 Fase 3 — Mapeamento do ecossistema

Para o tema pesquisado, mapear exaustivamente:

- Estado da arte e boas práticas modernas
- Padrões de arquitetura recomendados
- Funcionalidades correlatas e requisitos implícitos
- Ferramentas, bibliotecas, frameworks, SDKs, APIs
- Integrações, automações, metodologias
- Técnicas de implementação e otimização
- Estratégias de validação, teste, observabilidade
- Segurança, desempenho, escalabilidade
- Acessibilidade, internacionalização, documentação
- UX, DX (developer experience), manutenção
- CI/CD, versionamento, rollback, recuperação

---

## 3. AVALIAÇÃO TÉCNICA DE ALTERNATIVAS

Para cada tecnologia encontrada, avaliar:

| Dimensão | Pergunta |
|---|---|
| Maturidade | Estável (1.0+)? Quanto tempo no mercado? |
| Manutenção | Ativa? Frequência de commits? Quantos mantenedores? |
| Documentação | Completa? Atualizada? Exemplos? |
| Comunidade | Tamanho? Issues respondidas? Suporte? |
| Adoção | Quem usa? Casos conhecidos? |
| Compatibilidade | Funciona com Godot 4.7? Com nosso stack? |
| Implementação | Esforço? Curva de aprendizado? |
| Desempenho | Overhead? Benchmarks? |
| Segurança | CVEs? Dependências? Superfície de ataque? |
| Licenciamento | Compatível com MIT? Restrições? |

**Sempre comparar alternativas antes de recomendar.** Justificar tecnicamente a escolha.

---

## 4. PESQUISA DELIBERADA DE PROBLEMAS

Buscar ativamente:

- Problemas conhecidos e limitações
- Vulnerabilidades e CVEs
- Anti-padrões e armadilhas comuns
- Edge cases e conflitos de implementação
- Riscos ocultos e requisitos frequentemente esquecidos
- Falhas recorrentes em projetos similares
- Post-mortems, changelogs, breaking changes

---

## 5. PESQUISA DE IMPLEMENTAÇÕES REAIS

- Projetos open source maduros que implementam algo similar
- Estudos de caso e benchmarks
- Issues relevantes e PRs importantes
- Discussões técnicas em fóruns oficiais
- Lições aprendidas documentadas

---

## 6. CRITÉRIO DE PROPOSTA

Só propor implementação quando:

- Produz ganho líquido de qualidade, simplicidade, confiabilidade ou produtividade
- Não introduz overengineering, duplicação ou dependência desnecessária
- O custo-benefício é positivo e demonstrável
- É compatível com a arquitetura, decisões e padrões existentes

---

## 7. ATUALIZAÇÃO DA DOCUMENTAÇÃO

Durante a pesquisa, atualizar continuamente:

1. `docs/PESQUISA_EXTERNA.md` — adicionar seção com descobertas, fontes, data
2. `.github/instructions/fontes.instructions.md` — se nova fonte relevante for descoberta
3. `.github/instructions/aprendizados.instructions.md` — se novo anti-padrão for identificado
4. A ficha da fatia (`.github/roadmap/ONDA_*.md`) — se a pesquisa revelar nova fonte relevante
5. `HANDOFF.md` — resumo da pesquisa para a próxima sessão

---

## 8. AUTO-AUDITORIA FINAL (obrigatória)

Antes de encerrar, executar auditoria crítica da própria pesquisa:

1. **Lacunas:** Há temas relevantes não abordados?
2. **Vieses:** As fontes são diversas ou concentradas em uma única perspectiva?
3. **Inconsistências:** Fontes diferentes contradizem? Como resolver?
4. **Profundidade:** A pesquisa foi profunda o suficiente ou ficou superficial?
5. **Aplicabilidade:** As descobertas são realmente aplicáveis ao projeto?

Se qualquer resposta for negativa → **retomar pesquisa** até eliminar a lacuna.

---

## 9. FORMATO DE ENTREGA

Ao final, entregar relatório com:

1. **Tema pesquisado** e contexto no projeto
2. **Fontes consultadas** (nome, URL, data de acesso)
3. **Descobertas principais** (3-5 pontos de maior impacto)
4. **Recomendações** priorizadas por custo-benefício
5. **Riscos e problemas** identificados
6. **Documentação atualizada** (lista de arquivos modificados)
