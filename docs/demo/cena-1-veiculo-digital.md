# Cena 1 — Cliente digital simples com garantia de veículo

## Objetivo da cena

Demonstrar para Lary que a plataforma consegue receber um **Cliente Sintético** pessoa física, aplicar guardrails, executar o **Baseline Determinístico** e devolver um **Próximo Passo Responsável** auditável para uma jornada simples de veículo no SuperApp.

Esta cena não representa Aprovação, Contratação, taxa, limite ou proposta real de crédito. A ação escolhida é uma recomendação de jornada para iniciar uma **Simulação**.

## Cliente Sintético usado

Arquivo executável:

- `examples/synthetic-customers/vehicle-simple.json`

Características principais:

- garantia: `vehicle`;
- canal: `superapp`;
- estágio: `simulation`;
- risco sintético: `low`;
- confiança da política: `high`;
- engajamento: `high`;
- completude de contexto: `sufficient`;
- segmento não sensível: `digital_simple`;
- sem guardrail conhecido antes da política.

## Como executar

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/vehicle-simple.json \
  --audit-log-dir logs/decisions \
  --pretty
```

## Resultado esperado

Campos principais esperados na resposta:

```json
{
  "selected_action": "simulate_vehicle_secured_loan",
  "policy_version": "baseline_deterministic_v0.1",
  "requires_human_review": false,
  "guardrails_triggered": []
}
```

Reason Codes esperados:

- `vehicle_collateral_anchor`;
- `digital_channel_fit`;
- `sufficient_context_for_simulation`;
- `qualified_intent_signal`;
- `low_or_medium_synthetic_risk`;
- `no_critical_guardrail_triggered`.

A resposta também deve conter:

- `decision_id`;
- `request_id`;
- `eligible_actions`;
- `audit_log_ref`;
- `not_credit_approval = true`;
- `not_credit_contracting = true`;
- `does_not_define_real_rate = true`;
- `does_not_define_real_limit = true`;
- `requires_formal_credit_analysis = true`.

## Log auditável

O campo `audit_log_ref` aponta para um arquivo JSONL em `logs/decisions/` ou no diretório informado em `--audit-log-dir`.

O log deve registrar somente contexto minimizado, sem CPF, nome, e-mail, telefone, renda real, patrimônio real, atributos sensíveis, regras comerciais privadas ou dados reais de veículo.

## Critério de sucesso da demo

A cena passa quando:

1. o comando executa de ponta a ponta;
2. `selected_action` é `simulate_vehicle_secured_loan`;
3. `requires_human_review` é `false`;
4. `guardrails_triggered` é vazio;
5. os Reason Codes explicam veículo, canal digital, contexto suficiente e ausência de guardrail crítico;
6. o log auditável existe e contém uma decisão minimizada;
7. a mensagem deixa claro que a decisão não é Aprovação, Contratação, taxa ou limite real.

## Por que isso importa para Lary

Esta é a cena de autosserviço digital mais simples do MVP. Ela mostra que a plataforma consegue gerar valor no SuperApp sem transformar a decisão em uma venda automática de crédito e sem perder rastreabilidade.
