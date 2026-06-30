# Decisão 003 — Checklist de Planejamento do MVP para Lary

## 1. Contexto

Este checklist organiza os próximos passos do projeto após a definição de Lary como **CTO da unidade de negócio de Empréstimos com Garantia**. O objetivo é transformar a visão de produto em artefatos implementáveis, avaliáveis e demonstráveis para o Datathon.

A plataforma deve decidir o **melhor próximo passo responsável** para clientes elegíveis em jornadas de empréstimo com garantia, considerando múltiplos tipos de colateral, canais digitais, atendimento consultivo, governança e delayed rewards.

## 2. Decisão

O projeto seguirá uma sequência incremental:

1. consolidar o MVP narrativo para Lary;
2. documentar os braços/ofertas;
3. escolher e documentar a base pública;
4. definir schemas sintéticos;
5. criar golden set;
6. implementar baseline;
7. implementar política adaptativa;
8. expor decisão por CLI/API/app;
9. documentar governança;
10. montar narrativa de demo.

## 3. Checklist de planejamento

### 3.1 MVP narrativo para Lary

- [x] Criar `docs/product/mvp-lary.md`.
- [x] Definir problema principal da BU de Empréstimos com Garantia.
- [x] Definir canal inicial: SuperApp, agência ou fluxo híbrido.
- [x] Definir garantias no MVP:
  - [x] veículo;
  - [x] imóvel;
  - [x] investimentos;
  - [x] recebíveis sintéticos, se entrar no escopo inicial — decisão: fora do MVP inicial, como evolução futura.
- [x] Definir métrica principal de negócio.
- [x] Confirmar que a métrica principal será proposta qualificada, simulação qualificada ou contratação simulada.
- [x] Explicitar que a plataforma não aprova crédito automaticamente.

### 3.2 Catálogo de braços/ofertas

- [x] Criar `docs/product/offer-arms.md`.
- [x] Definir braços de produto.
- [x] Definir braços de jornada.
- [x] Incluir braço `no_offer_now`.
- [x] Incluir braço de conteúdo educativo.
- [x] Incluir braço de encaminhamento para especialista/agência.
- [x] Mapear cada braço por:
  - [x] tipo de garantia;
  - [x] canal;
  - [x] risco;
  - [x] necessidade de revisão humana;
  - [x] reason codes esperados;
  - [x] critérios de elegibilidade sintética.

### 3.3 Base pública Kaggle

- [ ] Escolher base pública principal.
- [ ] Recomendação inicial: Bank Marketing.
- [ ] Criar `data/kaggle/README.md`.
- [ ] Documentar:
  - [ ] fonte;
  - [ ] link;
  - [ ] versão;
  - [ ] licença;
  - [ ] target;
  - [ ] colunas originais;
  - [ ] limitações;
  - [ ] instruções de download.
- [ ] Documentar descarte de colunas com vazamento temporal.
- [ ] Confirmar tratamento da coluna `duration`, se a base escolhida for Bank Marketing.

### 3.4 Schema dos dados sintéticos

- [ ] Criar `docs/data/synthetic-schema.md`.
- [ ] Definir schema de `offer_catalog`.
- [ ] Definir schema de `offer_events`.
- [ ] Definir schema de `delayed_rewards`.
- [ ] Definir schema de `evaluation_cases`.
- [ ] Definir sementes aleatórias.
- [ ] Definir horizonte temporal por tipo de garantia.
- [ ] Definir segmentos sintéticos não sensíveis.
- [ ] Definir campos mínimos para auditoria.

### 3.5 Golden set

- [ ] Criar `data/golden_set/evaluation_cases.jsonl`.
- [ ] Incluir pelo menos 20 casos.
- [ ] Cobrir casos típicos.
- [ ] Cobrir casos de borda.
- [ ] Cobrir casos adversariais.
- [ ] Cobrir casos inelegíveis.
- [ ] Cobrir cold-start.
- [ ] Cobrir contexto incompleto.
- [ ] Cobrir canal inválido.
- [ ] Cobrir repetição excessiva de oferta.
- [ ] Cada caso deve conter:
  - [ ] contexto;
  - [ ] ação esperada;
  - [ ] recompensa esperada ou critério de sucesso;
  - [ ] justificativa;
  - [ ] critério explícito de pass/fail.

### 3.6 Baseline determinístico

- [ ] Implementar política simples por regra.
- [ ] Regras iniciais sugeridas:
  - [ ] garantia de imóvel com alta complexidade → `route_to_specialist`;
  - [ ] veículo com alto engajamento digital → oferta/simulação no SuperApp;
  - [ ] baixa confiança → conteúdo educativo;
  - [ ] inelegível → `no_offer_now`.
- [ ] Registrar versão da política baseline.
- [ ] Gerar logs auditáveis.
- [ ] Medir conversão/recompensa simulada.

### 3.7 Política adaptativa

- [ ] Implementar ou simular Thompson Sampling.
- [ ] Definir priors por braço.
- [ ] Definir atualização com feedback observado.
- [ ] Definir tratamento de delayed rewards.
- [ ] Definir comportamento para eventos censurados.
- [ ] Comparar contra baseline.
- [ ] Documentar Nilos-UCB, UCB ou variação contextual como referência/alternativa.
- [ ] Calcular métricas:
  - [ ] recompensa acumulada;
  - [ ] regret acumulado;
  - [ ] taxa de exploração;
  - [ ] exposição por braço;
  - [ ] conversão qualificada;
  - [ ] fairness por segmento sintético.

### 3.8 Interface demonstrável

- [ ] Escolher primeira interface: CLI, API, notebook ou app.
- [ ] Recomendação inicial: CLI simples ou API REST mínima.
- [ ] Definir contrato de entrada.
- [ ] Definir contrato de saída.
- [ ] Incluir reason codes.
- [ ] Incluir `policy_version`.
- [ ] Incluir `requires_human_review`.
- [ ] Incluir `guardrails_triggered`.
- [ ] Gerar log auditável por decisão.
- [ ] Criar pelo menos um exemplo executável.

### 3.9 Governança e documentação obrigatória

- [ ] Criar `docs/model-card.md`.
- [ ] Criar `docs/system-card.md`.
- [ ] Criar `docs/lgpd-plan.md`.
- [ ] Documentar intended use.
- [ ] Documentar usos fora de escopo.
- [ ] Documentar riscos conhecidos.
- [ ] Documentar fairness.
- [ ] Documentar humano no loop.
- [ ] Documentar rollback.
- [ ] Documentar ciclo de aprovação de política.

### 3.10 Arquitetura Azure e MLOps

- [ ] Criar `docs/architecture-azure.md`.
- [ ] Incluir diagrama Mermaid.
- [ ] Mapear serviços Azure.
- [ ] Incluir Azure ML ou MLflow para tracking.
- [ ] Incluir Azure Key Vault.
- [ ] Incluir Managed Identity.
- [ ] Incluir Azure Monitor/Application Insights.
- [ ] Definir ambientes: local, teste e produção simulada.
- [ ] Definir aprovação humana antes de promoção de política.
- [ ] Definir rollback.

### 3.11 Narrativa de demo

- [ ] Criar roteiro da demo.
- [ ] Cena 1: cliente digital simples recebe simulação/oferta de veículo.
- [ ] Cena 2: cliente com garantia imóvel ou alta complexidade é roteado para especialista.
- [ ] Cena 3: cliente inelegível/adversarial recebe `no_offer_now` ou conteúdo educativo.
- [ ] Mostrar log auditável.
- [ ] Mostrar reason codes.
- [ ] Mostrar versão da política.
- [ ] Mostrar diferença entre baseline e política adaptativa.
- [ ] Preparar plano de contingência caso demo ao vivo falhe.

## 4. Ordem recomendada de execução

1. `docs/product/mvp-lary.md`
2. `docs/product/offer-arms.md`
3. `data/kaggle/README.md`
4. `docs/data/synthetic-schema.md`
5. `data/golden_set/evaluation_cases.jsonl`
6. baseline determinístico
7. Thompson Sampling
8. CLI/API demonstrável
9. avaliação offline
10. model card, system card e LGPD plan
11. arquitetura Azure
12. roteiro e slides da demo

## 5. Critério de pronto desta decisão

Esta decisão será considerada concluída quando:

- o MVP para Lary estiver documentado;
- os braços iniciais estiverem definidos;
- a base pública estiver escolhida e documentada;
- o schema sintético estiver definido;
- existir golden set com pelo menos 20 casos;
- houver baseline e política adaptativa comparáveis;
- uma decisão puder ser executada e auditada;
- a narrativa de demo estiver alinhada ao problema de Empréstimos com Garantia.
