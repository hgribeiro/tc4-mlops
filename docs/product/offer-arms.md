# Catálogo de braços — Próximo passo responsável em Empréstimos com Garantia

## 1. Objetivo

Este documento define os braços iniciais da plataforma demonstrável de **próximo passo responsável** para a BU de **Empréstimos com Garantia**.

No MVP, um braço não é uma aprovação de crédito nem uma oferta final. Um braço representa uma **ação de jornada auditável** que pode ser escolhida pela política de decisão para aumentar a chance de **proposta qualificada simulada**, reduzir abandono e preservar governança.

A plataforma não aprova crédito automaticamente, não define taxa, limite ou prazo real e não substitui análise formal de crédito, risco, jurídico ou compliance.

Este catálogo está alinhado ao escopo definido em `docs/product/mvp-lary.md`.

## 2. Princípios do catálogo

1. **Simulação antes de venda**: o MVP prioriza simulação, educação, documentação, encaminhamento consultivo ou `no_offer_now`, não oferta direta.
2. **Próximo passo, não ranking de produto**: a decisão central é qual ação responsável tomar na jornada.
3. **Colateral muda a jornada**: veículo, imóvel e investimentos têm riscos, tempos e necessidades de explicação diferentes.
4. **Governança na saída**: toda decisão deve gerar reason codes, versão de política, guardrails e log auditável.
5. **Humano no loop quando necessário**: especialmente em imóvel, alto valor, baixa confiança, comunicação sensível e exceções.
6. **`no_offer_now` sempre disponível**: a política nunca deve ser forçada a vender ou simular.
7. **Delayed rewards explícitos**: proposta qualificada pode acontecer dias ou semanas após a ação inicial.

## 3. Braços iniciais do MVP

| ID canônico | Tipo | Status no MVP | Descrição curta |
| --- | --- | --- | --- |
| `simulate_vehicle_secured_loan` | Simulação/jornada | Obrigatório | Simulação inicial de empréstimo com garantia de veículo no SuperApp. |
| `simulate_home_equity` | Simulação/jornada | Obrigatório | Simulação orientada de crédito com garantia de imóvel, normalmente com possibilidade de revisão humana. |
| `simulate_investment_secured_loan` | Simulação/jornada | Obrigatório | Simulação com garantia de investimentos para cliente sintético de maior relacionamento. |
| `educational_content_secured_credit` | Jornada | Obrigatório | Conteúdo educativo para explicar crédito com garantia, riscos e próximos passos. |
| `request_documents` | Jornada | Obrigatório | Solicitação de documentos ou dados sintéticos necessários para qualificação. |
| `route_to_specialist` | Jornada/humano no loop | Obrigatório | Encaminhamento para especialista, agência ou atendimento consultivo. |
| `no_offer_now` | Guardrail/jornada | Obrigatório | Não ofertar nem simular neste momento; pode sugerir educação, espera ou revisão posterior. |

## 4. Definição de sucesso principal

A métrica principal associada aos braços é **proposta qualificada simulada**.

Uma proposta qualificada simulada ocorre quando o cliente sintético:

1. conclui uma simulação; e
2. fornece dados mínimos ou documentação para pré-análise.

Isso não implica aprovação, contratação, limite, taxa ou promessa de crédito.

## 5. Detalhamento dos braços

### 5.1 `simulate_vehicle_secured_loan`

**Descrição**  
Recomenda iniciar simulação de empréstimo com garantia de veículo no SuperApp.

**Garantia**  
Veículo.

**Canal preferencial**  
SuperApp.

**Quando usar**

- cliente sintético com canal digital válido;
- bom engajamento digital;
- contexto suficiente para simulação inicial;
- risco sintético baixo ou médio;
- ausência de guardrails críticos;
- ausência de repetição excessiva de comunicação.

**Quando evitar**

- dados insuficientes sobre a garantia;
- baixa confiança da política;
- canal inválido;
- contexto adversarial;
- cliente já exposto repetidamente ao mesmo braço;
- qualquer sinal de que a comunicação possa parecer aprovação de crédito.

**Revisão humana**  
Normalmente não exigida em caso simples. Exigir se houver alto valor sintético, baixa confiança ou exceção de elegibilidade.

**Reason codes esperados**

- `vehicle_collateral_anchor`
- `digital_channel_fit`
- `sufficient_context_for_simulation`
- `qualified_intent_signal`
- `low_or_medium_synthetic_risk`
- `no_critical_guardrail_triggered`

**Sinais de sucesso**

- simulação iniciada;
- dados sintéticos do veículo informados;
- simulação concluída;
- proposta qualificada simulada.

**Delayed reward sugerido**  
2 a 20 dias sintéticos.

---

### 5.2 `simulate_home_equity`

**Descrição**  
Recomenda simulação de crédito com garantia de imóvel, com linguagem conservadora e possibilidade de revisão humana.

**Garantia**  
Imóvel.

**Canal preferencial**  
SuperApp para início da simulação; especialista/agência para continuidade quando necessário.

**Quando usar**

- cliente sintético demonstra intenção clara;
- há informações mínimas sobre imóvel e estágio da jornada;
- simulação é mais adequada que oferta direta;
- existe necessidade de explicar prazo, documentação e complexidade;
- o caso pode demandar transição para atendimento consultivo.

**Quando evitar**

- baixa confiança extrema;
- ausência de dados mínimos do imóvel;
- cliente inelegível no contexto sintético;
- tentativa adversarial;
- risco de a mensagem ser interpretada como aprovação.

**Revisão humana**  
Frequentemente exigida. Deve ser `true` em alto valor, baixa confiança, contexto incompleto relevante ou complexidade documental.

**Reason codes esperados**

- `home_equity_requires_guidance`
- `high_complexity_collateral`
- `simulation_preferred_over_direct_offer`
- `human_review_recommended`
- `longer_delayed_reward_expected`

**Sinais de sucesso**

- simulação iniciada;
- simulação concluída;
- documentação iniciada;
- aceite de contato consultivo;
- proposta qualificada simulada após revisão.

**Delayed reward sugerido**  
7 a 45 dias sintéticos.

---

### 5.3 `simulate_investment_secured_loan`

**Descrição**  
Recomenda simulação com garantia de investimentos para clientes sintéticos de maior relacionamento, com comunicação clara sobre riscos.

**Garantia**  
Investimentos.

**Canal preferencial**  
SuperApp com possibilidade de especialista, principalmente em comunicação sensível.

**Status**  
Obrigatório no MVP.

**Quando usar**

- cliente sintético tem relacionamento compatível;
- há sinal de necessidade de liquidez sem venda imediata do investimento;
- canal digital é válido;
- comunicação de risco está disponível;
- política tem confiança suficiente.

**Quando evitar**

- cliente sintético sem perfil de relacionamento adequado;
- comunicação de risco ausente;
- baixa confiança;
- contexto sensível ou incompleto;
- risco de parecer recomendação de investimento ou aprovação de crédito.

**Revisão humana**  
Exigir em comunicação sensível, alto valor, baixa confiança ou exceções.

**Reason codes esperados**

- `investment_collateral_candidate`
- `relationship_context_supports_simulation`
- `liquidity_need_signal`
- `risk_communication_required`
- `human_review_if_sensitive`

**Sinais de sucesso**

- abertura da simulação;
- leitura/aceite de conteúdo explicativo;
- contato com especialista, quando aplicável;
- envio de dados mínimos;
- proposta qualificada simulada.

**Delayed reward sugerido**  
1 a 15 dias sintéticos.

---

### 5.4 `educational_content_secured_credit`

**Descrição**  
Entrega conteúdo educativo sobre crédito com garantia, diferenças entre colaterais, riscos, documentação e próximos passos.

**Garantia**  
Veículo, imóvel e investimentos.

**Canal preferencial**  
SuperApp, app inbox ou tela contextual na jornada.

**Quando usar**

- cliente sintético está no início da jornada;
- baixa maturidade ou baixa clareza de intenção;
- dados insuficientes para uma simulação responsável;
- baixa confiança moderada;
- necessidade de explicar diferença entre simulação, proposta, aprovação e contratação.

**Quando evitar**

- cliente já demonstrou intenção qualificada e tem contexto suficiente para simulação;
- repetição excessiva de conteúdo;
- situação exige especialista ou `no_offer_now`.

**Revisão humana**  
Não exigida normalmente. Pode ser exigida se o conteúdo envolver comunicação sensível sobre investimentos ou imóvel.

**Reason codes esperados**

- `education_before_simulation`
- `insufficient_context_for_simulation`
- `early_journey_stage`
- `responsible_personalization`
- `approval_clarification_needed`

**Sinais de sucesso**

- conteúdo visualizado;
- avanço para simulação;
- redução de abandono na próxima etapa;
- cliente fornece dados mínimos.

**Delayed reward sugerido**  
1 a 14 dias sintéticos.

---

### 5.5 `request_documents`

**Descrição**  
Solicita documentos ou dados sintéticos necessários para continuar a qualificação da jornada.

**Garantia**  
Veículo, imóvel e investimentos, com maior relevância para imóvel e investimentos.

**Canal preferencial**  
SuperApp para coleta inicial; especialista/agência quando houver complexidade.

**Quando usar**

- há intenção suficiente, mas contexto incompleto;
- a próxima barreira é documental ou cadastral;
- a política não deve avançar para proposta simulada sem mais evidência;
- garantia exige informações específicas para avançar.

**Quando evitar**

- cliente inelegível no contexto sintético;
- documento não altera decisão possível;
- fricção documental seria prematura;
- tentativa adversarial ou canal inválido.

**Revisão humana**  
Exigir quando documentação envolver imóvel, alto valor, divergência sintética ou exceção.

**Reason codes esperados**

- `documentation_required`
- `context_incomplete_but_recoverable`
- `qualification_before_simulation`
- `collateral_details_missing`
- `human_review_if_complex`

**Sinais de sucesso**

- documento/dado sintético enviado;
- documentação completa;
- avanço para simulação concluída;
- proposta qualificada simulada.

**Delayed reward sugerido**  
3 a 21 dias sintéticos.

---

### 5.6 `route_to_specialist`

**Descrição**  
Encaminha o cliente sintético para especialista, agência ou atendimento consultivo.

**Garantia**  
Veículo, imóvel e investimentos, com prioridade para imóvel, investimentos sensíveis e casos de alto valor.

**Canal preferencial**  
Handoff do SuperApp para atendimento humano; também pode iniciar em agência/consultivo.

**Quando usar**

- garantia de imóvel;
- alto valor sintético;
- baixa confiança;
- contexto incompleto relevante;
- necessidade de explicação humana;
- cliente sintético de maior relacionamento;
- comunicação sensível;
- tentativa adversarial não crítica, mas que exige avaliação;
- exceção de elegibilidade.

**Quando evitar**

- caso simples de veículo no SuperApp;
- cliente inelegível sem caminho responsável de recuperação;
- especialista seria usado apenas para empurrar venda;
- ausência de disponibilidade/capacidade sintética do canal.

**Revisão humana**  
Sim. Este braço representa humano no loop.

**Reason codes esperados**

- `specialist_required`
- `high_value_or_complex_case`
- `low_policy_confidence`
- `collateral_complexity`
- `suitability_or_explanation_needed`
- `human_in_the_loop`

**Sinais de sucesso**

- aceite de contato;
- atendimento iniciado;
- documentação orientada;
- proposta qualificada simulada;
- redução de abandono em caso complexo.

**Delayed reward sugerido**  
7 a 45 dias sintéticos.

---

### 5.7 `no_offer_now`

**Descrição**  
Não recomenda oferta nem simulação neste momento. Pode registrar bloqueio, sugerir conteúdo educativo genérico ou aguardar novo contexto.

**Garantia**  
Veículo, imóvel e investimentos.

**Canal preferencial**  
Todos.

**Quando usar**

- inelegibilidade sintética;
- canal inválido;
- dados insuficientes não recuperáveis naquele momento;
- baixa confiança extrema;
- contexto adversarial;
- repetição excessiva de comunicação;
- guardrail crítico acionado;
- ausência de braço adequado;
- risco de confundir recomendação com aprovação.

**Quando evitar**

- existe ação educativa ou documental claramente responsável;
- o problema é apenas falta leve de contexto;
- especialista resolveria a complexidade com segurança.

**Revisão humana**  
Não exigida por padrão, mas pode ser acionada se o motivo for exceção sensível ou investigação de guardrail.

**Reason codes esperados**

- `no_responsible_action_available`
- `synthetic_ineligibility`
- `invalid_channel`
- `insufficient_context`
- `excessive_contact_repetition`
- `critical_guardrail_triggered`
- `adversarial_or_unsafe_context`

**Sinais de sucesso**

- ausência de exposição indevida;
- redução de violação de guardrail;
- retorno futuro com contexto melhor;
- manutenção de auditoria adequada.

**Delayed reward sugerido**  
Pode ser censurado ou medido por retorno futuro: 7 a 30 dias sintéticos.

## 6. Matriz por garantia

| Garantia | Braços preferenciais | Braços cautelosos | Humano no loop | Observação |
| --- | --- | --- | --- | --- |
| Veículo | `simulate_vehicle_secured_loan`, `educational_content_secured_credit`, `request_documents` | `route_to_specialist` em casos complexos | Apenas se alto valor, baixa confiança ou exceção | Âncora do MVP e principal cena digital. |
| Imóvel | `simulate_home_equity`, `request_documents`, `route_to_specialist` | Simulação sem dados mínimos; comunicação que pareça aprovação | Frequentemente sim | Caso obrigatório para demonstrar consultivo e governança. |
| Investimentos | `simulate_investment_secured_loan`, `educational_content_secured_credit`, `route_to_specialist`, `request_documents` | Uso sem comunicação de risco | Sim em comunicação sensível | Entra no MVP para representar cliente de maior relacionamento. |
| Recebíveis sintéticos | Fora do MVP inicial | N/A | N/A | Evolução futura, provavelmente ligada a PJ/fluxo de caixa sintético. |

## 7. Matriz por canal

| Canal | Braços adequados | Braços que exigem cautela | Critério de uso |
| --- | --- | --- | --- |
| SuperApp | `simulate_vehicle_secured_loan`, `simulate_home_equity`, `simulate_investment_secured_loan`, `educational_content_secured_credit`, `request_documents`, `no_offer_now` | Simulação de imóvel ou investimentos sem explicação suficiente | Canal principal para escala, simulação e educação. |
| Especialista/agência | `route_to_specialist`, `request_documents`, `simulate_home_equity`, `simulate_investment_secured_loan` | Qualquer comunicação sem log ou sem reason codes | Usar em alta complexidade, alto valor, baixa confiança ou comunicação sensível. |
| Híbrido | Todos, com governança | Todos se não houver handoff auditável | Fluxo padrão do MVP: decisão digital com saída consultiva quando necessário. |

## 8. Matriz por risco sintético

| Risco sintético | Ações preferidas | Ações bloqueadas ou cautelosas | Revisão humana |
| --- | --- | --- | --- |
| Baixo | Simulação, educação | Nenhuma, se elegível | Normalmente não |
| Médio | Simulação, documentação, educação | Simulação de colateral complexo sem explicação | Depende do colateral |
| Alto | Especialista, documentação, educação | Simulação direta sem revisão | Sim |
| Crítico/adversarial | `no_offer_now` | Simulações e promessas comerciais | Avaliar apenas se houver processo de exceção |
| Baixa confiança da política | Especialista, documentação, educação ou `no_offer_now` | Exploração agressiva | Sim quando sensível |

## 9. Elegibilidade sintética mínima

A elegibilidade abaixo é apenas para demonstração. Não representa regra real de crédito.

Campos sintéticos recomendados para avaliar braços:

- `collateral_type`: `vehicle`, `home`, `investment`;
- `channel`: `superapp`, `branch`, `specialist`, `hybrid`;
- `journey_stage`: `awareness`, `simulation`, `documentation`, `proposal`, `follow_up`;
- `synthetic_risk_level`: `low`, `medium`, `high`, `critical`;
- `policy_confidence`: `low`, `medium`, `high`;
- `engagement_level`: `low`, `medium`, `high`;
- `context_completeness`: `insufficient`, `partial`, `sufficient`;
- `relationship_tier`: `standard`, `high_relationship`;
- `contact_repetition_count`;
- `guardrails_triggered`;
- `requires_human_review`.

Recebíveis sintéticos podem ser adicionados no futuro, mas não fazem parte do schema mínimo do MVP.

## 10. Reason codes canônicos

Reason codes devem ser compreensíveis por negócio, risco e compliance.

### Adequação ao colateral

- `vehicle_collateral_anchor`
- `home_equity_requires_guidance`
- `investment_collateral_candidate`
- `collateral_complexity`
- `collateral_details_missing`

### Jornada e canal

- `digital_channel_fit`
- `early_journey_stage`
- `qualified_intent_signal`
- `simulation_preferred_over_direct_offer`
- `documentation_required`
- `specialist_required`

### Risco e governança

- `low_or_medium_synthetic_risk`
- `high_value_or_complex_case`
- `low_policy_confidence`
- `no_critical_guardrail_triggered`
- `critical_guardrail_triggered`
- `human_review_recommended`
- `human_in_the_loop`

### Segurança da decisão

- `insufficient_context`
- `context_incomplete_but_recoverable`
- `synthetic_ineligibility`
- `invalid_channel`
- `excessive_contact_repetition`
- `adversarial_or_unsafe_context`
- `no_responsible_action_available`
- `approval_clarification_needed`

## 11. Guardrails por braço

| Guardrail | Braços afetados | Comportamento esperado |
| --- | --- | --- |
| Atributo sensível/proxy indevido | Todos | Bloquear decisão ou remover atributo do contexto; registrar guardrail. |
| Canal inválido | Todos | Preferir `no_offer_now` ou solicitar correção do canal. |
| Contexto insuficiente | Simulações | Preferir `request_documents`, educação ou `no_offer_now`. |
| Baixa confiança | Simulações | Preferir especialista, documentação, educação ou `no_offer_now`. |
| Repetição excessiva | Simulações e comunicação | Bloquear nova exposição; preferir educação, pausa ou `no_offer_now`. |
| Colateral complexo | Imóvel e investimentos | Exigir revisão humana ou especialista quando aplicável. |
| Exploração adaptativa | Todos | Permitir apenas entre braços elegíveis e seguros. |
| Confusão com aprovação | Todos | Incluir disclaimer e campos `not_credit_approval` e `requires_formal_credit_analysis`. |

## 12. Contrato mínimo de saída por decisão

Toda escolha de braço deve gerar uma saída auditável com, no mínimo:

```json
{
  "decision_id": "dec_001",
  "request_id": "req_001",
  "decision_type": "next_best_action",
  "selected_action": "simulate_vehicle_secured_loan",
  "eligible_actions": [
    "simulate_vehicle_secured_loan",
    "educational_content_secured_credit",
    "request_documents",
    "no_offer_now"
  ],
  "policy_version": "baseline_v0.1",
  "reason_codes": [
    "vehicle_collateral_anchor",
    "digital_channel_fit",
    "qualified_intent_signal"
  ],
  "guardrails_triggered": [],
  "requires_human_review": false,
  "not_credit_approval": true,
  "requires_formal_credit_analysis": true,
  "exploration_flag": false,
  "message": "Esta decisão recomenda um próximo passo de jornada; não representa aprovação, limite, taxa ou contratação de crédito."
}
```

## 13. Recompensas e delayed rewards

A política não deve otimizar apenas clique. A métrica principal continua sendo **proposta qualificada simulada contra baseline**.

| Evento | Uso | Peso sugerido qualitativo |
| --- | --- | --- |
| Conteúdo visualizado | Sinal inicial | Baixo |
| Simulação iniciada | Sinal intermediário | Baixo/médio |
| Dados/documentos enviados | Sinal de qualificação | Médio |
| Atendimento especialista aceito | Sinal de avanço consultivo | Médio |
| Simulação concluída | Forte sinal intermediário | Alto |
| Proposta qualificada simulada | Métrica principal | Máximo |
| Guardrail violado | Penalidade | Crítico |
| Comunicação repetida abusivamente | Penalidade | Alto |

Janelas sintéticas recomendadas:

| Garantia | Janela de delayed reward |
| --- | --- |
| Veículo | 2 a 20 dias |
| Imóvel | 7 a 45 dias |
| Investimentos | 1 a 15 dias |

## 14. Relação com baseline e política adaptativa

### Baseline determinístico inicial

Regras sugeridas:

- veículo + SuperApp + alto engajamento + contexto suficiente → `simulate_vehicle_secured_loan`;
- imóvel + alto valor/complexidade → `route_to_specialist` ou `simulate_home_equity` com revisão;
- investimentos + alto relacionamento + comunicação de risco disponível → `simulate_investment_secured_loan` ou `route_to_specialist`;
- contexto incompleto recuperável → `request_documents`;
- início de jornada ou baixa clareza → `educational_content_secured_credit`;
- inelegível, adversarial, canal inválido ou guardrail crítico → `no_offer_now`.

### Política adaptativa

A política adaptativa, inicialmente Thompson Sampling contextual simplificado, só pode explorar entre braços elegíveis após aplicação dos guardrails.

Exploração nunca deve liberar braço bloqueado por risco, canal, colateral ou revisão humana ausente.

## 15. Não-objetivos preservados pelo catálogo

Este catálogo não deve ser interpretado como:

- motor de aprovação automática de crédito;
- precificador real de taxa ou limite;
- política real de concessão;
- substituto de risco, jurídico ou compliance;
- recomendação de investimento;
- integração com core bancário real;
- uso de dados reais ou sensíveis.

## 16. Critérios de pronto do catálogo

Este catálogo está pronto para orientar implementação quando:

- todos os braços têm ID canônico;
- cada braço possui garantia, canal, risco e revisão humana definidos;
- `no_offer_now` está disponível em todas as decisões;
- reason codes canônicos estão definidos;
- elegibilidade sintética mínima está documentada;
- delayed rewards estão ligados a sinais de jornada;
- a saída deixa claro que não há aprovação automática de crédito;
- há base suficiente para criar golden set e baseline determinístico.
