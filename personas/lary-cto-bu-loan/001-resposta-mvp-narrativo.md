# Resposta 001 — MVP narrativo da BU de Empréstimos com Garantia

## 1. Resumo executivo de Lary

Eu aprovo começar o MVP como uma plataforma demonstrável de experimentação adaptativa para decidir o **melhor próximo passo responsável** em jornadas de empréstimos com garantia, não como um motor de aprovação de crédito.

O problema prioritário é aumentar **propostas qualificadas** e reduzir abandono/custo operacional, aprendendo quando usar SuperApp, quando educar, quando pedir documentação e quando encaminhar para especialista. A garantia âncora da demo deve ser **veículo**, porque é a jornada mais simples para autosserviço digital. O MVP também deve incluir **imóvel** como caso de maior complexidade para demonstrar roteamento consultivo e governança. Investimentos pode entrar como braço controlado se houver tempo; recebíveis sintéticos ficam como extensão.

Minha decisão preferida é um MVP de **fluxo híbrido com SuperApp como canal principal**: autosserviço para simulação, educação e oferta leve; especialista/agência para garantias complexas, alto valor, baixa confiança ou necessidade de explicação. O risco dessa decisão é subestimar a complexidade operacional do handoff para especialista. Ainda assim, é melhor do que fingir que todo crédito com garantia cabe em uma jornada 100% digital.

## 2. Decisões para o MVP

| Tema | Decisão de Lary | Risco aceito |
| --- | --- | --- |
| Problema principal | Aumentar proposta qualificada e reduzir abandono/custo por proposta, sem perder governança | Métrica final pode demorar; usar sinais intermediários com cuidado |
| Canal inicial | Fluxo híbrido, com SuperApp como canal principal da demo | Handoff consultivo precisa ser bem explicado |
| Garantia âncora | Veículo | Pode parecer simples demais; compensar com cena de imóvel |
| Garantia complexa obrigatória | Imóvel | Delayed reward mais longo e maior necessidade de humano no loop |
| Garantia opcional | Investimentos | Comunicação de risco precisa ser clara |
| Fora do MVP inicial | Recebíveis sintéticos como implementação completa | Perde-se cenário PJ no início, mas reduz complexidade |
| Braços | Produto e jornada: oferta, simulação, educação, documentação, especialista, no_offer_now | Exige reason codes bons para não virar caixa-preta |
| Métrica principal | Taxa de proposta qualificada simulada contra baseline | Não equivale a contratação real |
| Política | Baseline determinístico + Thompson Sampling/adaptativa com guardrails | Bandit pode explorar braços inadequados se guardrails falharem |
| Governança | Logs auditáveis, policy_version, reason codes, guardrails, revisão humana e rollback | A demo precisa mostrar isso, não apenas mencionar |

## 3. Respostas às perguntas

### 1. Problema principal da BU

**1. Qual é o problema prioritário da unidade que o MVP deve resolver primeiro?**  
Resolver a baixa eficiência de qualificação na jornada de empréstimos com garantia: muitos clientes podem clicar ou iniciar interesse, mas poucos chegam a uma proposta completa e adequada. Quero aprender qual próximo passo aumenta a chance de **proposta qualificada**, não apenas clique.

**2. O problema principal é aquisição, conversão, qualificação, abandono, custo operacional, risco, experiência ou aprendizado?**  
Prioridade: **qualificação e redução de abandono**, com aprendizado sobre canal e tipo de garantia. Conversão importa, mas conversão sem adequação vira risco reputacional. Custo operacional entra como métrica secundária: especialista é caro, então deve ser usado quando agrega valor.

**3. Qual problema fica fora do MVP?**  
Ficam fora: aprovação formal de crédito, precificação real, cálculo real de limite/taxa, integração com core bancário, uso de dados reais de cliente, cobrança, formalização de contrato e recuperação de garantia.

### 2. Canal inicial

**4. O MVP começa por SuperApp, agência/consultivo ou híbrido?**  
Começa por **fluxo híbrido**, com decisão inicial no SuperApp e possibilidade explícita de roteamento para especialista.

**5. Qual canal principal na demo?**  
SuperApp. Ele demonstra escala e decisão em tempo quase real. A agência/especialista aparece como próximo passo responsável quando a jornada não deve seguir sozinha no digital.

**6. Quando sair do autosserviço digital para especialista?**  
Quando houver garantia de imóvel, alto valor sintético, baixa confiança da política, contexto incompleto, necessidade de documentação, cliente de alto relacionamento, dúvida de suitability, tentativa adversarial, repetição excessiva de oferta ou qualquer guardrail de risco/compliance.

**7. Encaminhamento para especialista é sucesso ou fricção?**  
É **sucesso possível** quando reduz risco, aumenta proposta qualificada ou melhora experiência. Não aceito tratar especialista como fracasso automaticamente.

### 3. Garantias no MVP

**8. Quais garantias entram no MVP inicial?**  
Obrigatórias: veículo e imóvel.  
Opcional controlada: investimentos, se houver tempo para documentar comunicação e revisão humana.  

**9. Quais ficam como extensão futura?**  
Recebíveis sintéticos ficam como extensão futura, especialmente para cenário PJ ou fluxo recorrente.

**10. Qual deve ser a garantia âncora da demo?**  
Veículo. É a melhor âncora para autosserviço no SuperApp, com sinais intermediários rápidos: clique, simulação, envio de dados do veículo.

**11. Como a decisão muda por garantia?**

- **Veículo:** pode receber simulação ou oferta leve no SuperApp se elegível e com bom engajamento digital.
- **Imóvel:** preferir simulação, documentação ou especialista; evitar oferta direta agressiva.
- **Investimentos:** pode aparecer para cliente de maior relacionamento, mas com comunicação clara sobre uso da garantia e revisão humana quando sensível.
- **Recebíveis sintéticos:** quando entrar, deve priorizar pré-análise/documentação e especialista PJ; não deve compartilhar lógica com veículo.

### 4. Próximos passos permitidos

**12. Quais próximos passos a plataforma pode escolher no MVP?**

- `offer_vehicle_secured_loan`
- `offer_home_equity_simulation`
- `offer_investment_secured_loan` se incluído
- `educational_content_secured_credit`
- `request_documents`
- `route_to_specialist`
- `no_offer_now`

**13. Apenas ofertas de produto ou também ações de jornada?**  
Também ações de jornada. Para empréstimos com garantia, educação, simulação, documentação e especialista são tão importantes quanto oferta.

**14. Quando `no_offer_now` deve aparecer?**  
Quando o cliente for inelegível no contexto sintético, houver baixa confiança, canal inválido, dados insuficientes, risco de repetição excessiva, guardrail acionado, contexto adversarial ou ausência de braço adequado.

### 5. Métrica principal

**15. Qual deve ser a métrica principal de negócio?**  
**Taxa de proposta qualificada simulada**, comparada contra baseline determinístico.

**16. Devemos otimizar clique, simulação iniciada, simulação qualificada, proposta completa, proposta qualificada ou contratação simulada?**  
Otimizar proposta qualificada. Como ela é delayed reward, usar simulação qualificada e proposta completa como sinais intermediários. Clique sozinho não serve como métrica principal.

**17. Qual métrica Lary defenderia para continuidade?**  
Uplift estatisticamente e operacionalmente convincente em proposta qualificada contra baseline, sem aumento de violações de guardrail, sem concentração injusta de exposição e com custo por proposta qualificada menor ou justificável.

**18. Quais métricas secundárias acompanham?**

- simulações qualificadas;
- propostas completas;
- abandono por etapa;
- custo por proposta qualificada;
- taxa de encaminhamento efetivo para especialista;
- reward acumulado e regret;
- taxa de exploração;
- exposição por braço e segmento sintético;
- decisões bloqueadas por guardrail;
- taxa de revisão humana;
- cobertura de logs auditáveis;
- latência da decisão;
- delayed rewards por tipo de garantia.

### 6. Guardrails e não-objetivos

**19. O que a plataforma não pode prometer?**  
Não pode prometer aprovação de crédito, taxa, limite, contratação, elegibilidade real, decisão regulatória, uso produtivo em banco real, integração com core, ou substituição de risco/compliance.

**20. Quais decisões exigem humano no loop?**  
Encaminhamento de imóvel, investimentos com comunicação sensível, alto valor sintético, baixa confiança, exceções de elegibilidade, contexto incompleto relevante, divergência entre política e regra mínima, ativação de novo braço, promoção de política e qualquer decisão que possa ser interpretada como aprovação ou recomendação sensível.

**21. Quais riscos fariam Lary pausar o MVP?**

- ausência de log auditável;
- reason codes genéricos ou incompreensíveis;
- bandit explorando oferta sensível sem guardrail;
- confusão entre simulação/oferta e aprovação;
- uso de atributo sensível ou proxy indevido;
- maximização de clique com queda de proposta qualificada;
- exposição injusta entre segmentos sintéticos;
- repetição abusiva de oferta;
- falta de rollback;
- delayed rewards ignorados;
- custo Azure desproporcional para a tese demonstrada.

**22. Como deixar claro que não aprova crédito automaticamente?**  
O contrato de saída deve conter `decision_type = next_best_action`, `not_credit_approval = true`, `requires_formal_credit_analysis = true` quando aplicável, `requires_human_review`, reason codes e texto explícito: “Esta decisão recomenda um próximo passo de jornada; não representa aprovação, limite, taxa ou contratação de crédito.”

### 7. Critérios de sucesso da demo

**23. O que precisa aparecer para eu considerar convincente?**  
Preciso ver uma decisão executável, com contexto minimizado, braços elegíveis, braço escolhido, policy version, reason codes, guardrails, flag de exploração, revisão humana quando necessário, log auditável e comparação contra baseline.

**24. Quais três cenas representam melhor o valor?**

1. Cliente digital simples recebe simulação/oferta de veículo no SuperApp.
2. Cliente com imóvel/alta complexidade é encaminhado para especialista, com revisão humana.
3. Cliente inelegível, adversarial ou com dados insuficientes recebe `no_offer_now` ou conteúdo educativo, com guardrail registrado.

**25. Qual evidência mínima de governança precisa aparecer?**  
Log JSONL ou equivalente com `decision_id`, `request_id`, timestamp, contexto minimizado, ofertas elegíveis, ação selecionada, `policy_version`, reason codes, guardrails, `requires_human_review`, referência de configuração e ambiente. Também quero ver rollback/pause policy descrito.

### 8. Decisão final de Lary

**26. Decisão executiva curta**  
Eu aprovo iniciar o MVP com uma jornada híbrida de empréstimos com garantia, ancorada em veículo no SuperApp e com imóvel como caso consultivo obrigatório. A plataforma deve decidir o próximo passo responsável — oferta, simulação, educação, documentação, especialista ou não ofertar — medindo proposta qualificada contra baseline, com logs auditáveis, reason codes, guardrails, delayed rewards e humano no loop para decisões sensíveis. Não aprovo qualquer narrativa de aprovação automática de crédito.

**27. Decisões pendentes para confirmação humana antes da implementação**

- Confirmar se investimentos entra no MVP ou fica para segunda iteração.
- Confirmar janelas sintéticas finais de delayed reward por garantia.
- Confirmar catálogo inicial de braços e nomes canônicos.
- Confirmar critérios sintéticos de elegibilidade e baixa confiança.
- Confirmar segmentos sintéticos permitidos para fairness.
- Confirmar política adaptativa inicial: Thompson Sampling simples ou contextual.
- Confirmar contrato final de entrada/saída da CLI/API.
- Confirmar formato e retenção dos logs auditáveis.
- Confirmar threshold de pausa/rollback.
- Confirmar se a primeira interface será CLI, API REST mínima ou notebook demonstrável.

## 4. Não-objetivos e guardrails

### Não-objetivos

- Aprovar crédito automaticamente.
- Definir taxa, limite ou prazo real.
- Usar dados reais de cliente.
- Integrar com core bancário real.
- Substituir análise formal de crédito, risco, jurídico ou compliance.
- Prometer prontidão para produção regulada.
- Otimizar clique como métrica final.
- Tratar todos os colaterais como equivalentes.

### Guardrails obrigatórios

- Minimização de dados no contexto de decisão.
- Proibição de atributos sensíveis e proxies indevidos.
- Separação explícita entre oferta, simulação, educação, documentação, roteamento e aprovação formal.
- `no_offer_now` sempre disponível.
- Humano no loop para imóvel, alto valor, baixa confiança e decisões sensíveis.
- Logs auditáveis por decisão.
- Reason codes compreensíveis para negócio, risco e compliance.
- Controle de exploração do bandit.
- Tratamento de delayed rewards e eventos censurados.
- Fairness de exposição por segmentos sintéticos.
- Rollback e pausa de política.

## 5. Métricas aprovadas

### Métrica principal

**Uplift em proposta qualificada simulada contra baseline determinístico.**

### Métricas secundárias de negócio

- simulação qualificada;
- proposta completa;
- abandono por etapa;
- custo por proposta qualificada;
- taxa de encaminhamento efetivo para especialista;
- valor esperado por decisão;
- distribuição de próximos passos por garantia e canal.

### Métricas técnicas

- recompensa acumulada;
- regret acumulado;
- taxa de exploração;
- exposição por braço;
- estabilidade entre versões de política;
- latência da decisão;
- performance no golden set.

### Métricas de risco e governança

- decisões com log auditável;
- decisões com reason codes válidos;
- guardrails acionados;
- revisões humanas requeridas;
- violações de elegibilidade;
- concentração excessiva de braço;
- fairness de exposição entre segmentos sintéticos;
- eventos censurados por delayed reward.

## 6. Cenas recomendadas para demo

### Cena 1 — Veículo no SuperApp

Cliente sintético com bom engajamento digital, canal mobile válido e garantia de veículo. A política recomenda `offer_vehicle_secured_loan` ou simulação de veículo. A saída mostra reason codes como elegibilidade sintética, alto engajamento digital e exploração controlada. Não há revisão humana obrigatória se o risco for baixo/médio.

### Cena 2 — Imóvel com roteamento consultivo

Cliente sintético interessado em garantia de imóvel, alto valor ou contexto complexo. A política escolhe `route_to_specialist` ou `offer_home_equity_simulation` com `requires_human_review = true`. A demo deve mostrar que roteamento é sucesso possível, não falha.

### Cena 3 — Caso adversarial/inelegível

Cliente com canal inválido, contexto incompleto, repetição excessiva de oferta ou sinal adversarial. A política escolhe `no_offer_now` ou `educational_content_secured_credit`. A saída registra guardrail acionado, reason codes e log auditável.

## 7. Pendências de confirmação humana

1. Escopo final de investimentos no MVP.
2. Janelas de delayed reward por garantia: veículo, imóvel e investimentos.
3. Lista final de braços e critérios de elegibilidade sintética.
4. Thresholds de baixa confiança, repetição excessiva e pausa de política.
5. Segmentos sintéticos para avaliação de fairness.
6. Interface inicial: CLI, API REST mínima ou notebook.
7. Campos definitivos do log auditável.
8. Regras de aprovação humana para promoção de política.
9. Plano de rollback e responsável por aprovação.
10. Limites de custo Azure para a demo.

## 8. Texto-base recomendado para docs/product/mvp-lary.md

O MVP para Lary será uma plataforma demonstrável de experimentação adaptativa para a BU de Empréstimos com Garantia de um banco digital. O objetivo é decidir o melhor próximo passo responsável para cada contexto sintético elegível, considerando tipo de garantia, canal, risco, estágio da jornada e necessidade de revisão humana.

O MVP começa com fluxo híbrido: o SuperApp é o canal principal de escala para educação, simulação e oferta leve, enquanto especialista/agência é usado para garantias complexas, maior valor, baixa confiança ou necessidade de explicação. A garantia âncora da demonstração será veículo, por ser mais adequada ao autosserviço. Imóvel entra como caso obrigatório de complexidade e roteamento consultivo. Investimentos é opcional controlado; recebíveis sintéticos ficam para evolução futura.

A plataforma poderá escolher braços de produto e de jornada: oferta de empréstimo com garantia de veículo, simulação de home equity, crédito com garantia de investimentos se incluído, conteúdo educativo, solicitação de documentação, roteamento para especialista e `no_offer_now`. A solução não aprova crédito automaticamente, não define taxa ou limite real e não substitui análise formal de crédito.

A métrica principal será uplift em proposta qualificada simulada contra baseline determinístico. Como empréstimos com garantia possuem delayed rewards, o MVP acompanhará sinais intermediários como clique, simulação qualificada, envio de documentação e aceite de contato, mas não usará clique como sucesso final. Métricas secundárias incluem abandono, custo por proposta qualificada, encaminhamento efetivo para especialista, reward acumulado, regret, exploração, fairness de exposição, guardrails acionados e cobertura de logs auditáveis.

A demo deve mostrar três cenas: um cliente digital simples recebendo simulação/oferta de veículo no SuperApp; um cliente com imóvel ou alta complexidade sendo encaminhado para especialista com revisão humana; e um caso adversarial ou inelegível recebendo `no_offer_now` ou conteúdo educativo. Em todas as cenas, a saída deve exibir `policy_version`, reason codes, guardrails, necessidade de revisão humana quando aplicável e referência de log auditável.

O MVP só será considerado convincente se demonstrar comparação contra baseline, controle de exploração, tratamento de delayed rewards, logs auditáveis, reason codes compreensíveis, minimização de dados, fairness sintética, rollback e separação clara entre recomendação de próximo passo, simulação, oferta e aprovação formal de crédito.
