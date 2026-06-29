# Schema mínimo — Cliente Sintético e dados de decisão

## 1. Objetivo

Este documento define o schema mínimo para representar um **Cliente Sintético** no MVP de **Próximo Passo Responsável** em **Empréstimos com Garantia**.

O schema existe para enriquecer a base pública Bank Marketing com contexto sintético de garantia, canal, risco, estágio de jornada e auditoria, sem transformar a demonstração em sistema real de aprovação, precificação ou contratação de crédito.

## 2. Princípios

1. O cliente é sempre **sintético** e pessoa física.
2. A decisão é um **próximo passo responsável**, não aprovação de crédito.
3. Guardrails rodam antes do baseline ou da política adaptativa.
4. A política só escolhe entre braços elegíveis e seguros.
5. `no_offer_now` deve permanecer disponível em todos os fluxos.
6. Campos sintéticos devem ser reproduzíveis por semente e linhagem.
7. Dados proibidos não devem entrar no schema, nem como campo opcional.

## 3. Entidade principal: `synthetic_customer_context`

Este é o contrato mínimo de entrada para baseline, política adaptativa e CLI futura.

| Campo | Tipo | Obrigatório | Valores esperados | Observação |
| --- | --- | --- | --- | --- |
| `request_id` | string | Sim | `req_*` | Identificador da requisição, sem PII. |
| `schema_version` | string | Sim | `synthetic_customer_context_v0.1` | Versão do contrato. |
| `synthetic_customer_id` | string | Sim | `syn_*` | Identificador sintético, não reversível para pessoa real. |
| `source_dataset` | string | Sim | `bank_marketing_public_proxy`, `golden_set`, `manual_demo` | Linhagem da origem sintética. |
| `source_record_ref` | string/null | Não | `uci_bank_row_000001` | Referência técnica opcional, sem dados pessoais. |
| `random_seed` | inteiro | Sim | `42`, `20260629` | Reprodutibilidade do enriquecimento. |
| `event_timestamp` | string | Sim | ISO 8601 | Timestamp sintético ou de execução da decisão. |
| `collateral_type` | string | Sim | `vehicle`, `home`, `investment` | Garantias do MVP. |
| `channel` | string | Sim | `superapp`, `branch`, `specialist`, `hybrid` | Canal da decisão de jornada. |
| `journey_stage` | string | Sim | `awareness`, `simulation`, `documentation`, `proposal`, `follow_up` | Estágio sintético, sem confundir proposta com aprovação. |
| `synthetic_risk_level` | string | Sim | `low`, `medium`, `high`, `critical` | Risco sintético para guardrails, não score real de crédito. |
| `policy_confidence` | string | Sim | `low`, `medium`, `high` | Confiança operacional da política para o contexto. |
| `engagement_level` | string | Sim | `low`, `medium`, `high` | Sinal sintético de engajamento, não clique como sucesso final. |
| `context_completeness` | string | Sim | `insufficient`, `partial`, `sufficient` | Indica se há dados mínimos para o próximo passo. |
| `synthetic_segment` | string | Sim | Ver seção 4 | Segmento não sensível para avaliação e fairness. |
| `relationship_tier` | string | Sim | `standard`, `high_relationship` | Segmento sintético de relacionamento, sem patrimônio real. |
| `contact_repetition_count` | inteiro | Sim | `0` a `n` | Número sintético de exposições/contatos recentes. |
| `collateral_detail_status` | string | Sim | `missing`, `partial`, `complete` | Completeness da garantia sintética. |
| `collateral_complexity` | string | Sim | `low`, `medium`, `high` | Complexidade sintética da garantia. |
| `risk_communication_available` | boolean | Sim | `true`, `false` | Necessário especialmente para investimentos. |
| `known_guardrail_flags` | array de string | Sim | Lista, pode ser vazia | Sinais já detectados antes da política. |
| `human_review_hint` | boolean | Sim | `true`, `false` | Indicação prévia de revisão; saída final ainda decide `requires_human_review`. |
| `allowed_input_features` | array de string | Sim | Lista auditável | Features efetivamente usadas, para provar minimização. |

## 4. Segmentos sintéticos não sensíveis

`synthetic_segment` deve ser usado para análise de exposição e fairness sem recorrer a atributos sensíveis ou proxies indevidos.

Valores iniciais permitidos:

- `digital_simple`: cliente sintético com boa aderência ao autosserviço digital;
- `collateral_complex`: garantia ou documentação mais complexa;
- `high_relationship_synthetic`: relacionamento sintético alto, sem patrimônio real;
- `education_first`: contexto inicial que exige explicação antes da simulação;
- `documentation_needed`: intenção existe, mas faltam dados mínimos;
- `guardrail_sensitive`: caso com restrição de segurança ou comunicação;
- `cold_start`: pouco histórico sintético disponível.

Não criar segmentos baseados em idade, gênero, raça, religião, saúde, estado civil, escolaridade, ocupação, renda real, saldo real, patrimônio real ou localização granular.

## 5. Campos derivados da base pública

A base Bank Marketing pode inspirar apenas sinais sintéticos de campanha. O uso recomendado é:

| Campo original | Campo sintético possível | Regra |
| --- | --- | --- |
| `contact` | `channel` | Mapear de forma sintética e limitada; não assumir SuperApp real. |
| `campaign` | `contact_repetition_count` | Usar como proxy de repetição, com cap e guardrail de excesso. |
| `pdays` | recência sintética opcional | Usar apenas se interpretado como histórico anterior. |
| `previous` | histórico sintético de contato | Usar apenas como sinal anterior, não como elegibilidade real. |
| `poutcome` | `engagement_level` inicial | Usar apenas como proxy fraco de histórico. |
| `y` | recompensa offline sintética | Nunca usar como feature de decisão. |

Campos proibidos ou bloqueados para decisão pré-interação:

- `duration`: removido/ignorado por vazamento temporal;
- `age`, `job`, `marital`, `education`: não usar para decisão por risco de discriminação/proxy;
- `balance`: não usar como renda ou patrimônio;
- `default`, `housing`, `loan`: não usar como regra real de elegibilidade de crédito.

## 6. Exemplo JSON mínimo

```json
{
  "request_id": "req_demo_vehicle_001",
  "schema_version": "synthetic_customer_context_v0.1",
  "synthetic_customer_id": "syn_vehicle_001",
  "source_dataset": "golden_set",
  "source_record_ref": null,
  "random_seed": 20260629,
  "event_timestamp": "2026-06-29T12:00:00Z",
  "collateral_type": "vehicle",
  "channel": "superapp",
  "journey_stage": "simulation",
  "synthetic_risk_level": "low",
  "policy_confidence": "high",
  "engagement_level": "high",
  "context_completeness": "sufficient",
  "synthetic_segment": "digital_simple",
  "relationship_tier": "standard",
  "contact_repetition_count": 1,
  "collateral_detail_status": "complete",
  "collateral_complexity": "low",
  "risk_communication_available": true,
  "known_guardrail_flags": [],
  "human_review_hint": false,
  "allowed_input_features": [
    "collateral_type",
    "channel",
    "journey_stage",
    "synthetic_risk_level",
    "policy_confidence",
    "engagement_level",
    "context_completeness",
    "synthetic_segment",
    "relationship_tier",
    "contact_repetition_count",
    "collateral_detail_status",
    "collateral_complexity",
    "risk_communication_available"
  ]
}
```

## 7. `offer_catalog`

O catálogo de braços deve ser consistente com `docs/product/offer-arms.md`.

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `action_id` | string | Sim | ID canônico do braço. |
| `action_type` | string | Sim | `simulation`, `education`, `documentation`, `human_routing`, `no_offer`. |
| `eligible_collateral_types` | array | Sim | Subconjunto de `vehicle`, `home`, `investment`; `no_offer_now` vale para todos. |
| `eligible_channels` | array | Sim | Canais permitidos. |
| `requires_human_review_default` | boolean | Sim | Default por braço. |
| `risk_ceiling` | string | Sim | Maior risco sintético permitido sem bloqueio. |
| `expected_reason_codes` | array | Sim | Reason codes canônicos. |
| `delayed_reward_window_days` | objeto | Sim | Janela por garantia quando aplicável. |
| `not_credit_approval` | boolean | Sim | Deve ser sempre `true`. |

Braços obrigatórios:

- `simulate_vehicle_secured_loan`;
- `simulate_home_equity`;
- `simulate_investment_secured_loan`;
- `educational_content_secured_credit`;
- `request_documents`;
- `route_to_specialist`;
- `no_offer_now`.

## 8. `offer_events`

Eventos de jornada servem para avaliação e delayed rewards. Eles não substituem logs auditáveis.

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `event_id` | string | Sim | ID sintético do evento. |
| `request_id` | string | Sim | Requisição associada. |
| `decision_id` | string | Sim | Decisão que originou o evento. |
| `synthetic_customer_id` | string | Sim | ID sintético. |
| `action_id` | string | Sim | Braço selecionado. |
| `event_type` | string | Sim | `content_viewed`, `simulation_started`, `documents_sent`, `specialist_contact_accepted`, `simulation_completed`, `simulated_qualified_proposal`, `guardrail_violation`, `abandonment`. |
| `event_timestamp` | string | Sim | ISO 8601. |
| `is_primary_success` | boolean | Sim | `true` apenas para proposta qualificada simulada quando definido. |
| `reward_weight` | número | Sim | Peso sintético documentado, não valor financeiro real. |

## 9. `delayed_rewards`

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `reward_id` | string | Sim | ID sintético. |
| `decision_id` | string | Sim | Decisão avaliada. |
| `action_id` | string | Sim | Braço selecionado. |
| `collateral_type` | string | Sim | `vehicle`, `home`, `investment`. |
| `observation_window_days` | inteiro | Sim | Deve respeitar a janela por garantia. |
| `reward_observed` | boolean | Sim | Indica se houve recompensa dentro da janela. |
| `reward_type` | string | Sim | `intermediate`, `simulated_qualified_proposal`, `censored`, `penalty`. |
| `reward_value` | número | Sim | Valor sintético para avaliação offline. |
| `observed_at` | string/null | Sim | ISO 8601 ou nulo se censurado. |

Janelas sintéticas obrigatórias:

| Garantia | Janela |
| --- | --- |
| `vehicle` | 2 a 20 dias |
| `home` | 7 a 45 dias |
| `investment` | 1 a 15 dias |

## 10. `evaluation_cases`

O golden set futuro deve usar este formato mínimo.

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `case_id` | string | Sim | ID estável do caso. |
| `description` | string | Sim | Descrição curta para humanos. |
| `context` | objeto | Sim | Um `synthetic_customer_context`. |
| `expected_action_class` | string | Sim | Braço ou classe esperada. |
| `expected_guardrails_triggered` | array | Sim | Lista esperada, pode ser vazia. |
| `expected_requires_human_review` | boolean | Sim | Resultado esperado. |
| `expected_reason_codes` | array | Sim | Reason codes esperados. |
| `pass_fail_criteria` | string | Sim | Critério explícito de aceitação. |

O golden set deve cobrir veículo, imóvel, investimentos, educação, documentação, especialista e `no_offer_now`.

## 11. Campos mínimos de auditoria na saída da decisão

Toda decisão derivada deste schema deve retornar, no mínimo:

| Campo | Obrigatório | Observação |
| --- | --- | --- |
| `decision_id` | Sim | ID da decisão. |
| `request_id` | Sim | Ecoa a entrada. |
| `selected_action` | Sim | Braço escolhido. |
| `eligible_actions` | Sim | Braços elegíveis após guardrails. |
| `policy_version` | Sim | Versão do baseline ou política adaptativa. |
| `reason_codes` | Sim | Reason codes explicáveis. |
| `guardrails_triggered` | Sim | Lista, pode ser vazia. |
| `requires_human_review` | Sim | Boolean. |
| `audit_log_ref` | Sim | Referência de log com minimização de dados. |
| `not_credit_approval` | Sim | Deve ser `true`. |
| `requires_formal_credit_analysis` | Sim | Deve ser `true`. |

A saída não pode conter aprovação, limite, taxa, contratação ou promessa de concessão.

## 12. Dados proibidos

O schema não deve conter:

- CPF;
- nome;
- e-mail;
- telefone;
- endereço;
- identificadores pessoais reais;
- dados reais de cliente;
- renda real;
- patrimônio real;
- saldo real interpretado como patrimônio;
- dados reais de veículo, imóvel ou investimento;
- gênero;
- raça ou etnia;
- religião;
- saúde;
- orientação sexual;
- estado civil como feature de decisão;
- idade como feature de decisão;
- geolocalização granular;
- regras comerciais privadas de bancos;
- decisões reais de aprovação, limite, taxa, contratação, cobrança ou inadimplência.

Se algum campo desse tipo aparecer em fonte pública ou arquivo auxiliar, ele deve ser descartado, mascarado ou bloqueado antes da decisão.

## 13. Guardrails mínimos derivados do schema

| Guardrail | Condição de exemplo | Comportamento esperado |
| --- | --- | --- |
| `temporal_leakage_duration` | `duration` aparece em `allowed_input_features` | Bloquear preparação de features e registrar falha. |
| `prohibited_personal_data` | Campo proibido detectado | Bloquear decisão ou remover campo antes da política. |
| `invalid_channel` | Canal fora da enumeração | Preferir `no_offer_now` ou erro de validação. |
| `unsupported_collateral` | Garantia fora de `vehicle`, `home`, `investment` | Bloquear no MVP; registrar fora de escopo. |
| `insufficient_context` | `context_completeness = insufficient` | Evitar simulação direta; considerar educação, documentação ou `no_offer_now`. |
| `excessive_contact_repetition` | Repetição acima do limite sintético | Evitar nova exposição comercial. |
| `adversarial_or_unsafe_context` | `synthetic_risk_level = critical` | Preferir `no_offer_now`. |

## 14. Recebíveis sintéticos

Recebíveis sintéticos não fazem parte do schema mínimo do MVP. O valor `synthetic_receivables` não é aceito em `collateral_type` nesta versão.

Evolução futura deve criar uma versão nova do schema, provavelmente com contexto de pessoa jurídica, fluxo de caixa sintético, eventos de recebíveis e revisão de governança.

## 15. Critério de pronto deste schema

Este schema está pronto para orientar a próxima etapa quando:

- todos os campos mínimos do Cliente Sintético estiverem definidos;
- `duration` estiver bloqueado para decisão pré-interação;
- dados proibidos estiverem explícitos;
- as três garantias do MVP estiverem cobertas;
- recebíveis estiverem marcados como futuro escopo;
- auditoria mínima estiver definida;
- houver base suficiente para criar golden set, baseline determinístico e CLI de decisão.
