# Saídas previamente salvas para contingência da demo

Estas saídas resumem uma execução local bem-sucedida da versão atual. Elas permitem continuar o pitch se terminal, ambiente Python ou MLflow falhar. Os JSON completos de decisão podem ser regenerados pelos comandos do README; IDs e caminhos de log podem variar entre execuções.

## Comparação experimental salva

Os valores abaixo foram copiados de uma execução local de `artifacts/experiment/report.json` e ficam versionados neste documento. O artefato JSON completo é regenerável pelo comando `experiment` e, por ser saída local, permanece fora do Git.

| Configuração/métrica | Valor salvo |
| --- | ---: |
| Registros da fixture | 4 |
| Horizonte por seed | 400 |
| Seeds | `11,29,47` |
| Recompensa média do baseline | 206,67 |
| Recompensa média adaptativa | 303,67 |
| Uplift absoluto médio | 97,00 |
| Desvio-padrão do uplift | 6,53 |
| Regret adaptativo acumulado médio | 17,49 |
| Taxa média de exploração | 8,22% |

Recompensa significa avanço qualificado **sintético** no simulador. Não é conversão observada, Proposta Qualificada Simulada, Aprovação ou evidência causal.

## Cena 1 — veículo digital

```json
{
  "decision_id": "dec_7bef876479be",
  "request_id": "req_demo_vehicle_001",
  "selected_action": "simulate_vehicle_secured_loan",
  "policy_version": "baseline_deterministic_v0.1",
  "reason_codes": [
    "vehicle_collateral_anchor",
    "digital_channel_fit",
    "sufficient_context_for_simulation",
    "qualified_intent_signal",
    "low_or_medium_synthetic_risk",
    "no_critical_guardrail_triggered"
  ],
  "guardrails_triggered": [],
  "requires_human_review": false,
  "audit_log_ref": "logs/decisions/2026-06-29.jsonl",
  "not_credit_approval": true,
  "not_credit_contracting": true
}
```

## Cena 2 — imóvel complexo

```json
{
  "decision_id": "dec_657c819e8dba",
  "request_id": "req_demo_home_complex_001",
  "selected_action": "route_to_specialist",
  "policy_version": "baseline_deterministic_v0.1",
  "reason_codes": [
    "specialist_required",
    "high_value_or_complex_case",
    "home_collateral_complexity",
    "specialist_guidance_required",
    "collateral_complexity",
    "low_policy_confidence",
    "human_in_the_loop"
  ],
  "guardrails_triggered": [],
  "requires_human_review": true,
  "audit_log_ref": "logs/decisions/2026-06-29.jsonl",
  "not_credit_approval": true,
  "not_credit_contracting": true
}
```

## Cena 3 — adversarial/inelegível

```json
{
  "decision_id": "dec_34d86e0b8b95",
  "request_id": "req_demo_guardrail_001",
  "selected_action": "no_offer_now",
  "policy_version": "baseline_deterministic_v0.1",
  "reason_codes": [
    "adversarial_or_unsafe_context",
    "no_responsible_action_available",
    "approval_clarification_needed"
  ],
  "guardrails_triggered": ["adversarial_or_unsafe_context"],
  "requires_human_review": false,
  "audit_log_ref": "logs/decisions/2026-06-29.jsonl",
  "not_credit_approval": true,
  "not_credit_contracting": true
}
```

## Política Adaptativa

Uma execução com o artefato local `artifacts/experiment/policy.json` produziu:

```json
{
  "decision_id": "dec_7c08af3edf8a",
  "request_id": "req_demo_vehicle_001",
  "selected_action": "educational_content_secured_credit",
  "policy_version": "contextual_thompson_sampling_v0.1",
  "reason_codes": [
    "education_before_simulation",
    "responsible_personalization",
    "adaptive_policy_selection",
    "eligible_after_guardrails"
  ],
  "guardrails_triggered": [],
  "requires_human_review": false,
  "audit_log_ref": "logs/decisions/2026-06-29.jsonl",
  "not_credit_approval": true,
  "not_credit_contracting": true
}
```

A ação pode diferir da ação do Baseline Determinístico porque há amostragem contextual. Ela sempre deve pertencer a `eligible_actions`, calculado após os Guardrails. Uma decisão individual não comprova o uplift agregado.

## Golden Set

Última validação preparada:

```json
{
  "total_cases": 5,
  "passed_cases": 5,
  "failed_cases": 0,
  "policy_version": "baseline_deterministic_v0.1",
  "selected_actions": [
    "educational_content_secured_credit",
    "no_offer_now",
    "request_documents",
    "route_to_specialist",
    "simulate_vehicle_secured_loan"
  ]
}
```
