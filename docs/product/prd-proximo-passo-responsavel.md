# PRD — MVP de Próximo Passo Responsável em Empréstimos com Garantia

## Problem Statement

Lary, CTO da unidade de negócio de Empréstimos com Garantia, precisa demonstrar uma plataforma de MLE/MLOps e IA generativa que personalize jornadas de crédito com garantia sem parecer um motor de aprovação, precificação ou venda automática de crédito.

O problema não é simplesmente escolher a próxima melhor oferta. O problema é decidir o **Próximo Passo Responsável** para um **Cliente Sintético** pessoa física, considerando garantia, canal, estágio da jornada, risco sintético, contexto disponível, guardrails, humano no loop, delayed rewards e logs auditáveis.

A BU precisa aumentar **Propostas Qualificadas Simuladas** por decisão, comparando uma política adaptativa contra um baseline determinístico, sem usar dados reais, atributos sensíveis, regras bancárias privadas ou promessas de contratação.

## Solution

Construir um MVP demonstrável que recebe o contexto de um Cliente Sintético, aplica guardrails antes de qualquer política, escolhe um braço elegível como Próximo Passo Responsável e retorna uma decisão auditável.

O MVP deve cobrir três cenas obrigatórias de demonstração: cliente digital simples com garantia de veículo, cliente com garantia complexa encaminhado para especialista ou revisão humana, e cliente inelegível/adversarial redirecionado para `no_offer_now` ou conteúdo educativo. O MVP também deve incluir investimentos como terceira garantia do escopo inicial.

A primeira interface demonstrável será uma CLI. A mesma lógica deve poder evoluir depois para API REST, notebook ou app, mas sem acoplar a decisão ao canal de apresentação.

A camada LLM/RAG deve apoiar explicação, consulta documental e governança, mas não deve escolher braço, aprovar crédito, substituir guardrails, substituir reason codes ou substituir baseline/política adaptativa.

## User Stories

1. As Lary, I want to see a responsible next-step decision for a synthetic secured-loan journey, so that I can evaluate business value without implying automatic credit approval.
2. As Lary, I want every decision to distinguish simulation, simulated qualified proposal, approval, and contracting, so that the demo is safe for a regulated financial context.
3. As Lary, I want the MVP to compare a deterministic baseline with an adaptive policy, so that uplift is measured against a simple explainable reference.
4. As Lary, I want the platform to optimize for Simulated Qualified Proposals rather than clicks, so that the metric reflects qualified journey progress.
5. As Lary, I want decisions to include reason codes, so that business, risk, and compliance stakeholders can understand why a next step was chosen.
6. As Lary, I want decisions to include guardrails triggered, so that unsafe or ineligible scenarios are visible and auditable.
7. As Lary, I want decisions to include a policy version, so that results are traceable across experiments.
8. As Lary, I want decisions to indicate whether human review is required, so that complex collateral or sensitive cases are escalated responsibly.
9. As Lary, I want `no_offer_now` to always be available, so that the system is never forced to simulate or sell when no responsible action exists.
10. As Lary, I want the demo to include a simple vehicle scenario in the SuperApp, so that digital self-service value is visible.
11. As Lary, I want the demo to include a home equity or complex collateral scenario, so that human-in-the-loop governance is visible.
12. As Lary, I want the demo to include an ineligible or adversarial scenario, so that guardrails and safe refusal are visible.
13. As Lary, I want the demo to include investment-secured lending for a high-relationship synthetic customer, so that the MVP covers all approved collateral types.
14. As a product stakeholder, I want each selectable arm to have a canonical ID, so that experiments and logs can be compared consistently.
15. As a product stakeholder, I want each arm to document when to use and when to avoid it, so that implementation does not drift into unsafe recommendation behavior.
16. As a risk stakeholder, I want guardrails to run before the baseline or adaptive policy, so that exploration cannot bypass safety constraints.
17. As a risk stakeholder, I want exploration to occur only among eligible and safe arms, so that Thompson Sampling cannot choose a blocked action.
18. As a compliance stakeholder, I want the output to state that the decision is not credit approval, so that users do not confuse simulation with formal credit decisions.
19. As a compliance stakeholder, I want prohibited data categories to be documented, so that agents do not introduce real personal data or sensitive attributes.
20. As a data stakeholder, I want the public banking marketing dataset documented as a proxy, so that its limitations are explicit.
21. As a data stakeholder, I want temporal leakage risks documented, so that fields only available after interaction are not used for pre-interaction decisions.
22. As a data stakeholder, I want a synthetic schema for secured-loan journeys, so that the dataset can be enriched without pretending to be real bank data.
23. As a data stakeholder, I want delayed reward windows by collateral type, so that evaluation reflects different journey maturation times.
24. As an MLE, I want a deterministic baseline, so that adaptive policy performance can be evaluated against a transparent reference.
25. As an MLE, I want a contextual Thompson Sampling policy, so that the system can demonstrate adaptive learning by segment, collateral, and channel.
26. As an MLE, I want offline evaluation metrics for uplift, cumulative reward, regret, exploration rate, arm exposure, fairness, and guardrail rate, so that the experiment can be judged beyond click-through.
27. As an MLE, I want a golden set of evaluation cases, so that expected behavior is stable across future changes.
28. As an MLE, I want the golden set to cover vehicle, home, investments, education, documentation, specialist routing, and `no_offer_now`, so that all arms are exercised.
29. As an MLE, I want the CLI to return a complete decision contract, so that end-to-end behavior is testable from outside the implementation.
30. As an auditor, I want a decision log reference for every decision, so that outcomes can be traced after the fact.
31. As an auditor, I want logs to follow minimization of data, so that the demo does not normalize excessive data capture.
32. As an auditor, I want model and system documentation, so that intended use, limitations, and known risks are explicit.
33. As a demo operator, I want three clear demo scenes, so that the narrative can be shown reliably in a Datathon setting.
34. As a demo operator, I want sample synthetic customers, so that the CLI can be run without manual data preparation.
35. As a demo operator, I want outputs that are readable by non-engineering stakeholders, so that Lary can evaluate the product logic quickly.
36. As a future API developer, I want the decision engine independent from the CLI, so that the same behavior can later be exposed through REST or an app.
37. As a governance stakeholder, I want rollback or pause policy documented, so that unsafe policy promotion can be stopped.
38. As a governance stakeholder, I want human approval before promoting policies, so that adaptive learning does not become uncontrolled production automation.
39. As a future product owner, I want received-backed lending to remain explicitly future scope, so that the MVP does not accidentally expand into synthetic business cash-flow complexity.
40. As a future maintainer, I want canonical terminology to be enforced in docs and code, so that “offer”, “approval”, and “conversion” do not become ambiguous.

## Implementation Decisions

- The canonical product decision is **Próximo Passo Responsável**, not next-best-offer.
- The canonical selectable unit is **Braço**.
- The MVP treats “cliente” as **Cliente Sintético** pessoa física only.
- The approved MVP collateral types are vehicle, home, and investments.
- Synthetic receivables are future scope because they introduce business-customer and synthetic cash-flow complexity.
- The main success metric is **Proposta Qualificada Simulada**.
- Simulation, Simulated Qualified Proposal, Approval, and Contracting are separate stages and must not be collapsed.
- Guardrails must run before baseline or adaptive policy selection.
- The policy can only select among arms that remain eligible after guardrails.
- `no_offer_now` must remain an available arm in all decision flows.
- The deterministic baseline is the first executable policy and acts as the comparison reference.
- The adaptive policy is contextual Thompson Sampling simplified by segment, collateral, and channel.
- The first external interface is a CLI that accepts a synthetic customer context and returns a full auditable decision.
- The decision output must include decision ID, request ID, selected action, policy version, reason codes, guardrails triggered, human review flag, and explicit non-approval semantics.
- The data layer must treat the public bank marketing dataset as a proxy and document its limitations.
- Fields that create temporal leakage must not be used for pre-interaction decisioning.
- The synthetic schema must support collateral type, channel, journey stage, synthetic risk, policy confidence, engagement, context completeness, relationship tier, contact repetition, guardrails, and human review.
- The golden set must encode expected behavior for all required demo scenes and all required arms.
- Delayed rewards must be modeled with different synthetic windows by collateral type: vehicle 2–20 days, home 7–45 days, investments 1–15 days.
- LLM/RAG is not part of the decision authority. It can explain decisions, consult documentation, summarize experiments, and support governance.
- Governance artifacts must include intended use, out-of-scope uses, known risks, human-in-the-loop, rollback/pause policy, fairness considerations, simulated LGPD posture, model card, and system card.

## Testing Decisions

The preferred highest-level testing seam is the CLI decision contract. Tests should validate externally observable behavior: given a synthetic customer context, the system returns the expected selected action class, reason codes, guardrails, human review flag, non-approval fields, and log reference.

A second high-level seam is offline evaluation. Tests should validate that a fixed golden set can be evaluated against the baseline and later against the adaptive policy, producing stable metrics without depending on implementation internals.

A third seam is governance/explanation behavior. Tests should validate that an explanation can be generated from an existing decision and documented reason codes without changing the selected arm.

Good tests for this MVP should:

- assert behavior at the decision boundary, not internal helper functions;
- cover all approved collateral types;
- cover all required arms;
- cover guardrail-first behavior;
- cover human-in-the-loop routing;
- cover `no_offer_now` as a valid responsible outcome;
- assert that approval, limit, rate, and contracting are never returned as outcomes;
- assert that temporal-leakage fields are excluded from decision inputs;
- assert that outputs contain audit and governance fields;
- assert that adaptive exploration never selects an ineligible arm.

There is no existing implementation test suite in the current repo. The first tests should therefore be acceptance-style tests around CLI behavior and offline evaluation outputs.

## Out of Scope

- Real credit approval.
- Real credit contracting.
- Real limit calculation.
- Real interest-rate pricing.
- Integration with a real banking core.
- Use of real customer data.
- Use of CPF, name, email, phone, real income, real wealth, sensitive attributes, or private bank rules.
- Production-regulated operation.
- Replacing risk, legal, compliance, or formal credit processes.
- LLM-based arm selection.
- LLM-based credit approval.
- Optimizing only clicks or superficial conversion.
- Synthetic receivables in the initial MVP.
- Business-customer lending flows in the initial MVP.
- Full UI/app implementation before the CLI proves the decision path.

## Further Notes

The MVP should be built in vertical slices. A thin but complete first slice should accept one synthetic customer, apply guardrails, choose a safe arm, return an auditable decision, and be testable from the CLI. Subsequent slices should add data documentation, synthetic schema, baseline scenarios, golden set evaluation, delayed rewards, adaptive policy, LLM/RAG explanation, and governance artifacts.

The issue tracker and triage label vocabulary were not available in this environment, so this PRD was saved as a repository document instead of being published with a `ready-for-agent` label.
