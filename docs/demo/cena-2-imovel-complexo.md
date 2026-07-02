# Cena 2 — Imóvel complexo com Humano no Loop

## Objetivo da cena

Demonstrar para Lary que um **Cliente Sintético** com garantia de imóvel, maior complexidade de colateral e baixa confiança da política é direcionado para **Humano no Loop**, sem parecer oferta direta, Aprovação ou Contratação.

A cena mostra que o **Próximo Passo Responsável** pode ser `route_to_specialist` quando a jornada exige orientação, revisão documental e comunicação cuidadosa de risco.

## Cliente Sintético usado

Arquivo executável:

- `examples/synthetic-customers/home-complex.json`

Características principais:

- garantia: `home`;
- canal: `hybrid`;
- estágio: `simulation`;
- risco sintético: `medium`;
- confiança da política: `low`;
- complexidade do colateral: `high`;
- relacionamento sintético: `high_relationship`;
- segmento não sensível: `collateral_complex`;
- `human_review_hint = true`.

## Como executar

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/home-complex.json \
  --audit-log-dir logs/decisions \
  --pretty
```

## Resultado esperado

Campos principais esperados na resposta:

```json
{
  "selected_action": "route_to_specialist",
  "policy_version": "baseline_deterministic_v0.1",
  "requires_human_review": true,
  "guardrails_triggered": []
}
```

A ação `simulate_home_equity` permanece elegível no catálogo para contextos de imóvel, mas neste caso o baseline prioriza `route_to_specialist` porque há complexidade alta, confiança baixa e indicação explícita de revisão humana.

Reason Codes esperados:

- `specialist_required`;
- `high_value_or_complex_case`;
- `home_collateral_complexity`;
- `specialist_guidance_required`;
- `collateral_complexity`;
- `low_policy_confidence`;
- `human_in_the_loop`.

A resposta também deve conter:

- `decision_id`;
- `request_id`;
- `eligible_actions`;
- `audit_log_ref`;
- `not_credit_approval = true`;
- `not_credit_contracting = true`;
- `not_simulated_qualified_proposal = true`;
- `does_not_define_real_rate = true`;
- `does_not_define_real_limit = true`;
- `requires_formal_credit_analysis = true`.

## Separação entre etapas de crédito

Esta cena diferencia explicitamente:

- **Simulação**: pode ser iniciada futuramente como etapa informativa da jornada;
- **Proposta Qualificada Simulada**: é critério de avaliação/recompensa sintética posterior, não resultado desta decisão;
- **Aprovação**: exige análise formal fora do escopo da plataforma demonstrável;
- **Contratação**: exige fluxo separado e ação explícita fora do MVP.

## Log auditável

O campo `audit_log_ref` aponta para um arquivo JSONL em `logs/decisions/` ou no diretório informado em `--audit-log-dir`.

O log deve conter a decisão, `policy_version`, Reason Codes, Guardrails, `requires_human_review` e contexto minimizado. Ele não deve conter CPF, nome, e-mail, telefone, renda real, patrimônio real, endereço do imóvel, valor real do imóvel ou regra comercial privada.

## Critério de sucesso da demo

A cena passa quando:

1. o comando executa de ponta a ponta;
2. `selected_action` é `route_to_specialist` ou, em versão futura documentada, `simulate_home_equity` com revisão humana;
3. `requires_human_review` é `true`;
4. os Reason Codes explicam complexidade do imóvel, necessidade de orientação, baixa confiança e Humano no Loop;
5. o log auditável existe e contém uma decisão minimizada;
6. a mensagem deixa claro que a decisão não é Proposta Qualificada Simulada, Aprovação, Contratação, taxa ou limite real.

## Por que isso importa para Lary

Em empréstimos com garantia de imóvel, uma personalização responsável não deve maximizar clique nem empurrar oferta direta em casos complexos. A cena demonstra governança operacional: quando a política não tem confiança suficiente ou o colateral é complexo, a melhor ação é envolver humano, preservar rastreabilidade e reduzir risco de interpretação indevida pelo cliente.
