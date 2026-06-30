# Decisão de Fundação — Plataforma de Experimentação Adaptativa para Ofertas Financeiras

## 1. Contexto da empresa

Estamos construindo uma startup tech de pequeno porte focada em inteligência aplicada à personalização responsável de ofertas financeiras em canais digitais. A empresa nasce com uma proposta clara: ajudar instituições financeiras digitais a decidir, com segurança, rastreabilidade e melhoria contínua, qual oferta, mensagem ou próximo passo apresentar para cada cliente elegível.

O cliente de referência será um banco digital representado por **Lary**, CTO da unidade de negócio de **Empréstimos com Garantia**. Lary lidera a tecnologia dessa vertical e quer melhorar ofertas, mensagens e jornadas de crédito colateralizado em diferentes tipos de garantia. O banco possui um **SuperApp** como principal canal digital de escala, mas também mantém **agências físicas para clientes de relacionamento mais alto**, que demandam atendimento mais consultivo e maior cuidado na comunicação.

A construção será conduzida por um time fundador/implementador formado por produto, engenharia, machine learning, design e governança. O stakeholder principal não será um membro interno desse time: ele será Lary, representando o banco cliente. Essa persona será usada como interlocutor de domínio para tomar decisões sobre dor de negócio, canais, ofertas, restrições, métricas e riscos, especialmente porque o time construtor não deve presumir conhecimento profundo sobre operação bancária.

A solução não deve ser apresentada como um sistema bancário real pronto para produção regulada. O posicionamento correto é o de uma plataforma técnica demonstrável, madura em engenharia, governança, avaliação e operação, capaz de provar viabilidade antes de qualquer adoção em ambiente real.

## 2. Problema de negócio

O banco cliente precisa decidir, em diferentes canais, qual oferta, mensagem ou próximo passo apresentar para clientes elegíveis em jornadas de empréstimo. O foco inicial é empréstimo com garantia, onde a decisão pode envolver não apenas ofertar crédito, mas também educar o cliente, solicitar documentação, sugerir simulação, encaminhar para atendimento consultivo ou não apresentar oferta naquele momento.

Estratégias tradicionais baseadas em regras fixas ou testes A/B longos têm limitações importantes:

- desperdiçam tráfego durante longos períodos de teste;
- demoram para reagir a mudanças de comportamento;
- dificultam personalização contextual entre SuperApp e agência física;
- não lidam bem com incerteza sobre aceitação, risco, canal e momento;
- podem favorecer decisões pouco auditáveis quando evoluem de forma desorganizada;
- podem gerar riscos de exposição injusta entre segmentos de clientes;
- podem maximizar conversão sem considerar adequação, explicabilidade e necessidade de revisão humana.

A oportunidade é criar uma plataforma que combine experimentação adaptativa, avaliação offline, governança, observabilidade e explicabilidade para apoiar decisões mais eficientes e responsáveis na evolução da área de empréstimos do banco cliente.

## 3. Proposta de valor

A plataforma deve permitir que uma equipe de produto, dados e risco:

1. carregue uma base histórica compatível com campanhas, marketing, propensão, recomendação ou conversão;
2. gere uma camada sintética de experimentação com ofertas, eventos, contexto e recompensas;
3. compare políticas determinísticas simples contra políticas adaptativas;
4. avalie performance, risco, fairness, regret, conversão e exploração;
5. exponha decisões por API, CLI, notebook executável ou interface demonstrável;
6. registre cada decisão com versão da política, braço selecionado e reason codes;
7. simule operação em nuvem Azure com segurança, identidade, observabilidade e governança;
8. documente limitações, intended use, usos fora de escopo, LGPD, riscos e procedimentos de aprovação humana;
9. ofereça um assistente com LLM/RAG para resumir experimentos, recuperar políticas internas sintéticas e explicar decisões.

## 4. Nome conceitual do produto

Nome de trabalho recomendado: **Adaptive Offer Lab**.

Alternativas futuras:

- OfferOps Lab;
- FinBandit Studio;
- Adaptive Growth Engine;
- Responsible Offer Platform.

A escolha final do nome pode ser feita posteriormente, desde que mantenha coerência com a proposta: experimentação adaptativa, decisão auditável e governança para ofertas financeiras.

## 5. Visão do produto

O produto é uma plataforma de experimentação adaptativa para ofertas, mensagens ou próximos passos em canais digitais.

A plataforma recebe um contexto de decisão, avalia elegibilidade e risco, escolhe uma ação entre braços disponíveis, registra a decisão e permite acompanhar resultados observados posteriormente.

A lógica central é baseada em multi-armed bandits, equilibrando:

- **explotação**: usar ações que historicamente performam melhor;
- **exploração**: testar alternativas ainda incertas para aprender mais;
- **governança**: impedir usos inadequados, registrar decisões e preservar revisão humana em decisões sensíveis.

## 6. Papéis envolvidos na construção e validação da plataforma

### 6.1 Lary — CTO da unidade de Empréstimos com Garantia

Lary representa a unidade de negócio de Empréstimos com Garantia da instituição financeira que poderia contratar ou avaliar a plataforma. Ele não faz parte do time construtor. Atua como fonte de contexto de negócio, tecnologia, restrições operacionais, prioridades comerciais, preocupações regulatórias e critérios de sucesso da vertical.

O banco de Lary é digital, opera um SuperApp como canal principal e mantém agências físicas para clientes de relacionamento mais alto. A prioridade de Lary é melhorar a jornada de empréstimos com garantia, cobrindo diferentes tipos de colateral como veículo, imóvel, investimentos e recebíveis sintéticos.

Essa persona deve ser consultada sempre que houver dúvida sobre:

- qual dor bancária priorizar na vertical de empréstimos;
- qual canal simular primeiro: SuperApp, agência física ou fluxo híbrido;
- quais ofertas e próximos passos de empréstimo com garantia fazem sentido por tipo de colateral;
- quais próximos passos são plausíveis além de ofertar crédito;
- quais métricas importam para o banco;
- quais decisões exigem cautela, explicação ou revisão humana;
- quais riscos tecnológicos, regulatórios ou reputacionais inviabilizariam a adoção.

### 6.2 Equipe de produto da startup

Constrói a plataforma junto com o restante do time. Usa a visão de Lary, stakeholder do banco cliente, para definir hipóteses de oferta, priorizar MVP, acompanhar experimentos, entender impacto e decidir quando uma política pode avançar no ciclo de vida.

### 6.3 Equipe de dados e machine learning da startup

Constrói a camada analítica e adaptativa da plataforma. Prepara dados, treina ou simula políticas, avalia métricas, versiona experimentos e monitora drift.

### 6.4 Equipe de engenharia da startup

Constrói a camada de serviço e operação. Mantém contratos de entrada e saída, registra logs auditáveis, testa componentes e opera infraestrutura.

### 6.5 Equipe de risco, compliance e privacidade da startup

Define guardrails e limites de uso. Revisa minimização de dados, auditoria de decisões, fairness, LGPD, telemetria e necessidade de aprovação humana.

### 6.6 Liderança da startup

Usa a plataforma e as evidências geradas para entender valor de negócio, retorno esperado, riscos, custo operacional, maturidade da solução e posicionamento comercial.

## 7. Personas operacionais

### 7.1 Lary — CTO da unidade de Empréstimos com Garantia

**Missão:** representar o ponto de vista da unidade de negócio de Empréstimos com Garantia do banco cliente, trazendo contexto de negócio, tecnologia, canais, restrições operacionais, prioridades comerciais e preocupações de risco para orientar as decisões do time construtor.

Lary deve funcionar como uma contraparte consultiva. Ele não implementa a plataforma, mas ajuda a decidir o que faz sentido para um banco digital com SuperApp, operação de empréstimos e agências físicas para clientes de relacionamento mais alto. Como o time construtor não conhece profundamente o domínio bancário, Lary será a principal fonte de validação sobre hipóteses de produto, operação e valor.

**Perfil definido:** CTO da unidade de negócio de Empréstimos com Garantia em um banco digital. Tem visão de tecnologia, escala, segurança, integração, canais digitais, operação bancária e prioridades executivas da vertical. Seu objetivo inicial é melhorar a originação, qualificação, simulação, documentação, atendimento consultivo e contratação responsável de empréstimos com garantia.

**Contexto do banco cliente:**

- banco digital com SuperApp como canal principal;
- presença de agências físicas para clientes de relacionamento mais alto;
- unidade de Empréstimos com Garantia como vertical prioritária;
- múltiplos tipos de garantia no escopo sintético inicial: veículo, imóvel, investimentos e recebíveis sintéticos;
- necessidade de equilibrar conversão, experiência, risco, governança e custo operacional.

**Responsabilidades:**

- explicar a dor de negócio da área de empréstimos;
- priorizar objetivos comerciais, tecnológicos e operacionais;
- escolher ou validar o cenário principal de uso;
- validar se as ofertas sintéticas de empréstimo com garantia parecem plausíveis;
- apontar restrições de elegibilidade, suitability, risco e comunicação;
- definir quais métricas importam para o banco;
- indicar canais prioritários, como SuperApp, push, e-mail, internet banking, agência física ou fluxo híbrido;
- diferenciar jornadas de autosserviço digital e atendimento consultivo em agência;
- questionar riscos de adoção, reputação, compliance, experiência do cliente e integração tecnológica;
- cobrar evidências de valor, ROI, TCO, segurança operacional, observabilidade e governança;
- impedir que a solução seja apresentada como pronta para produção regulada sem evidência suficiente.

**Perguntas que essa persona deve fazer:**

- Que problema da área de empréstimos estamos tentando resolver primeiro?
- O foco é aumentar conversão, qualificar melhor os leads, reduzir custo de aquisição, melhorar experiência, aumentar uso de garantia ou aprender quais abordagens funcionam?
- Qual canal deve ser priorizado no MVP: SuperApp, agência física ou jornada híbrida?
- Em quais momentos faz sentido ofertar crédito e em quais momentos faz mais sentido educar, simular, pedir documentação ou encaminhar para especialista?
- Quais tipos de empréstimo com garantia são plausíveis para o catálogo sintético?
- Quais ofertas exigiriam mais cautela ou aprovação humana?
- Que tipo de cliente não deveria receber determinada oferta ou mensagem?
- Como o banco saberia que a plataforma gerou valor?
- Que métrica de negócio justificaria continuar o investimento?
- Que risco faria o banco pausar ou rejeitar a solução?
- A explicação da decisão é compreensível para uma área de negócio e defensável para risco/compliance?
- O custo operacional em Azure é justificável para o volume esperado?
- O que precisa aparecer na demonstração para convencer uma liderança bancária?

### 7.2 Gerente de produto

**Missão:** transformar a visão da startup e as necessidades trazidas por Lary, stakeholder do banco cliente, em escopo executável, organizando prioridades e mantendo coerência entre problema, solução, demonstração e documentação.

**Responsabilidades:**

- definir MVP;
- quebrar o trabalho em incrementos verticais;
- manter roadmap claro;
- alinhar dados, política, API, assistente e documentação;
- priorizar funcionalidades essenciais;
- preparar narrativa de produto.

**Perguntas que essa persona deve fazer:**

- Quem usa a plataforma no dia a dia?
- Qual fluxo precisa funcionar de ponta a ponta?
- O que é indispensável na primeira versão?
- Que cenário demonstra melhor a utilidade do produto?
- Quais riscos precisam aparecer explicitamente?
- Quais decisões ainda dependem de dados externos ou escolha humana?

### 7.3 Tech lead / engenheiro de ML

**Missão:** garantir que arquitetura, dados, algoritmos, avaliação, serviço e MLOps sejam sólidos, reproduzíveis e testáveis.

**Responsabilidades:**

- selecionar e documentar a base de dados;
- eliminar vazamento temporal ou atributos pós-contato indevidos;
- gerar enriquecimento sintético;
- implementar baseline determinístico;
- implementar ou simular política adaptativa;
- avaliar regret, conversão, recompensa, exploração e fairness;
- versionar dados, políticas e experimentos;
- expor uma decisão por API, CLI, notebook ou app;
- registrar logs auditáveis;
- definir arquitetura Azure;
- implementar testes automatizados mínimos.

**Perguntas que essa persona deve fazer:**

- Quais colunas não podem ser usadas por vazamento temporal?
- Como o contexto entra na decisão?
- Como as recompensas atrasadas são modeladas?
- Como o cold-start é tratado?
- Como a política é versionada?
- Como reproduzir o pipeline de ponta a ponta?
- Como auditar uma decisão individual?

### 7.4 Product designer

**Missão:** tornar a plataforma compreensível, demonstrável e confiável para públicos técnicos e não técnicos.

**Responsabilidades:**

- desenhar jornada do usuário;
- simplificar a experiência de demonstração;
- definir como reason codes, riscos e incerteza aparecem;
- apoiar storytelling visual;
- criar cenários típico, de borda e adversarial;
- garantir que a interface não prometa mais do que o sistema entrega.

**Perguntas que essa persona deve fazer:**

- Uma pessoa não técnica entende por que a oferta foi escolhida?
- O fluxo de demonstração é simples?
- Como mostramos confiança, incerteza e limites?
- Como diferenciar recomendação, elegibilidade e aprovação humana?
- Que evidência visual mostra que a decisão é auditável?

### 7.5 Responsável por risco, compliance e LGPD

**Missão:** garantir que a solução respeite privacidade, minimização, rastreabilidade, suitability sintética, revisão humana e limites de uso.

**Responsabilidades:**

- revisar atributos permitidos e proibidos;
- definir finalidade e base legal simulada;
- documentar minimização e retenção;
- avaliar fairness de exposição;
- revisar logs e telemetria;
- especificar guardrails;
- definir processo de aprovação humana;
- mapear riscos como reward hacking, manipulação de contexto, abuso do assistente e violação de suitability.

**Perguntas que essa persona deve fazer:**

- Algum atributo sensível ou proxy indevido está sendo usado?
- O sistema respeita minimização de dados?
- Há logs suficientes para auditoria sem expor informação desnecessária?
- Quais decisões exigem humano no loop?
- Como impedir que a política maximize conversão violando suitability?
- O assistente LLM pode inventar política ou expor informação indevida?

## 8. Escopo funcional inicial

A primeira versão deve ser direcionada à vertical de empréstimos do banco cliente, com ênfase em empréstimos com garantia. Ela deve conter:

1. cenário inicial de decisão para SuperApp, agência física ou fluxo híbrido;
2. base de dados pública documentada;
3. camada tratada sem vazamento temporal;
4. enriquecimento sintético com catálogo de ofertas de empréstimo, eventos de decisão e recompensas atrasadas;
5. baseline determinístico;
6. política adaptativa com Thompson Sampling e análise de UCB/Nilos-UCB ou variação contextual justificada;
7. avaliação offline reproduzível;
8. golden set com pelo menos 20 casos;
9. serviço, CLI, notebook ou app demonstrável;
10. log auditável de decisão;
11. documentação de arquitetura Azure;
12. ciclo de vida MLOps;
13. model card;
14. system card;
15. plano LGPD;
16. relatório técnico sintético;
17. narrativa executiva com valor, riscos, custos e plano de evolução para Lary e demais lideranças do banco cliente.

## 9. Fora de escopo inicial

A plataforma não deve prometer nesta fase:

- uso com dados reais de clientes;
- integração com core bancário real;
- aprovação automática de crédito, investimento ou produto sensível;
- decisão final sem revisão humana em contexto regulado;
- uso de patrimônio, renda real, gênero, raça, identificadores pessoais ou regras comerciais privadas;
- deploy produtivo real em ambiente financeiro regulado;
- substituição de times de risco, produto ou compliance.

## 10. Bases de dados públicas candidatas

A empresa deve usar uma base pública compatível com marketing, campanhas, propensão, recomendação, conversão ou resposta a ofertas. A base serve como referência factual inicial, enquanto a camada de experimentação adaptativa é sintética.

Opções candidatas:

| Base pública | Uso pretendido |
| --- | --- |
| Bank Marketing, de henriqueyamahata no Kaggle | Campanhas bancárias, propensão de conversão e decisão de oferta. |
| Bank Marketing Data Set, de tunguz no Kaggle | Variação do problema de marketing bancário para comparação. |
| Bank Term Deposit Subscription, de dharmik34 no Kaggle | Assinatura de depósito a prazo como proxy de conversão. |
| Telemarketing JYB Dataset, de aguado no Kaggle | Campanhas de contato e resposta, útil para comparação de canal ou abordagem. |

A escolha final deve registrar:

- fonte;
- link;
- versão;
- licença;
- colunas disponíveis;
- target;
- limitações;
- variáveis descartadas;
- riscos de vazamento temporal;
- instruções de download;
- justificativa de aderência ao problema de produto.

## 11. Política de dados

### 11.1 Dados permitidos

Podem ser usados dados públicos, anonimizados ou sintéticos que representem:

- histórico de campanha;
- atributos comportamentais não sensíveis;
- canal de contato;
- contexto sintético de decisão;
- elegibilidade sintética;
- resposta ou conversão observada;
- atraso na observação da recompensa;
- segmentos sintéticos não sensíveis.

### 11.2 Dados proibidos

Não devem ser usados:

- dados reais de clientes;
- nomes;
- CPF;
- e-mail;
- telefone;
- endereço;
- identificadores bancários;
- patrimônio real;
- renda real sensível;
- gênero;
- raça;
- religião;
- orientação sexual;
- dados de saúde;
- regras comerciais privadas;
- qualquer atributo que possa gerar discriminação direta ou indireta sem controle explícito.

### 11.3 Vazamento temporal

A preparação dos dados deve remover ou tratar colunas que só seriam conhecidas após a interação. Em bases de marketing bancário, a coluna `duration` é exemplo clássico de informação pós-contato que não deve ser usada para decidir a oferta antes da interação.

Toda exclusão ou transformação por risco de vazamento deve ser documentada.

## 12. Camadas de dados esperadas

A estrutura de dados recomendada é:

```text
data/
  kaggle/
    README.md
  processed/
    dataset_tratado_sem_vazamento.*
  synthetic_enrichment/
    offer_catalog.*
    offer_events.*
    delayed_rewards.*
  golden_set/
    evaluation_cases.jsonl
```

### 12.1 `data/kaggle/README.md`

Deve documentar:

- base escolhida;
- link;
- versão;
- licença;
- fonte;
- instruções de download;
- limitações;
- colunas originais;
- colunas removidas;
- decisão sobre vazamento temporal.

### 12.2 `data/processed/`

Deve conter a base tratada, sem atributos indevidos para decisão.

### 12.3 `data/synthetic_enrichment/offer_catalog`

Deve conter catálogo sintético de braços/ofertas, inicialmente orientado a empréstimos e próximos passos relacionados. Exemplo de campos:

- `offer_id`;
- `offer_name`;
- `offer_type`;
- `loan_type`;
- `guarantee_type`;
- `channel`;
- `eligibility_rule_id`;
- `risk_level`;
- `expected_business_value`;
- `requires_human_review`;
- `suitability_notes`;
- `active_from`;
- `active_until`.

### 12.4 `data/synthetic_enrichment/offer_events`

Deve conter impressões, contexto de decisão e ações selecionadas. Exemplo de campos:

- `event_id`;
- `synthetic_customer_id`;
- `timestamp`;
- `channel`;
- `context_features`;
- `eligible_offers`;
- `selected_offer_id`;
- `policy_version`;
- `decision_reason_codes`;
- `exploration_flag`.

### 12.5 `data/synthetic_enrichment/delayed_rewards`

Deve conter recompensas observadas depois da decisão. Exemplo de campos:

- `event_id`;
- `selected_offer_id`;
- `reward_observed_at`;
- `reward_type`;
- `conversion_flag`;
- `intermediate_signal`;
- `reward_value`;
- `delay_days`;
- `censored_flag`.

### 12.6 `data/golden_set/evaluation_cases.jsonl`

Deve conter pelo menos 20 casos avaliativos versionados. Cada caso deve incluir:

- contexto;
- ação esperada ou comportamento esperado;
- recompensa esperada ou critério de sucesso;
- justificativa;
- critério explícito de pass/fail;
- tipo do caso: típico, borda, elegibilidade, adversarial, fairness ou segurança.

## 13. Enriquecimento sintético

A camada sintética deve transformar a base pública em um ambiente de experimentação adaptativa. Ela deve simular:

- catálogo de ofertas;
- canais digitais;
- eventos de impressão;
- contexto de decisão;
- ações elegíveis;
- política aplicada;
- recompensas intermediárias;
- recompensas finais;
- atraso na observação de recompensa;
- cenários de cold-start;
- segmentos sintéticos para análise de exposição;
- casos adversariais.

Todo processo sintético deve registrar:

- semente aleatória;
- hipóteses de geração;
- distribuição dos braços;
- distribuição dos segmentos;
- horizonte temporal;
- regras de atraso;
- limitações;
- riscos de interpretação.

## 14. Estratégia algorítmica

A abordagem principal deve comparar uma política simples com uma política adaptativa.

### 14.1 Baseline determinístico

Possíveis baselines:

- sempre escolher o melhor braço histórico;
- regra fixa por segmento sintético;
- oferta padrão para todos os clientes elegíveis;
- política baseada em ranking estático de conversão histórica.

O baseline é importante porque permite demonstrar ganho ou limitação da política adaptativa.

### 14.2 Thompson Sampling

Thompson Sampling deve ser considerado como política adaptativa principal ou componente de simulação.

Uso esperado:

- modelar incerteza sobre conversão ou recompensa de cada braço;
- manter priors documentados;
- atualizar distribuições com feedback observado;
- equilibrar exploração e explotação;
- comparar resultado contra baseline.

Evidências necessárias:

- definição dos priors;
- regra de atualização;
- tratamento de recompensas atrasadas;
- análise de exploração;
- comparação quantitativa.

### 14.3 UCB, Nilos-UCB ou variação contextual

A análise algorítmica deve incluir UCB, Nilos-UCB, LinUCB ou variação contextual justificada.

A documentação deve explicar:

- fórmula ou adaptação escolhida;
- como a incerteza influencia seleção de braço;
- como o contexto entra na decisão;
- trade-off entre confiança, exploração e conversão;
- motivo para implementar ou não implementar essa família na primeira versão.

### 14.4 Cold-start

Deve haver regra clara para:

- ofertas novas;
- segmentos pouco observados;
- canais recém-criados;
- ausência de histórico suficiente.

Possíveis soluções:

- priors informativos sintéticos;
- exploração mínima obrigatória;
- fallback para baseline;
- regras de segurança e elegibilidade antes da seleção;
- aprovação humana para ativação de novos braços.

### 14.5 Recompensas atrasadas

A plataforma deve reconhecer que conversões ou resultados finais podem não ser observados imediatamente.

Deve haver documentação sobre:

- janela de observação;
- eventos censurados;
- sinais intermediários;
- atraso médio por tipo de oferta;
- como updates da política lidam com eventos ainda não finalizados.

## 15. Métricas de avaliação

A avaliação deve incluir métricas técnicas e de negócio.

### 15.1 Métricas técnicas

- recompensa acumulada;
- taxa de conversão simulada;
- regret acumulado;
- taxa de exploração;
- distribuição de exposição por braço;
- estabilidade da política;
- sensibilidade a priors;
- performance em golden set;
- taxa de erro em contratos de entrada;
- latência da decisão, se houver serviço.

### 15.2 Métricas de negócio

- uplift simulado contra baseline;
- valor esperado por decisão;
- desperdício de tráfego reduzido;
- custo estimado de operação;
- ROI qualitativo;
- TCO qualitativo;
- impacto por canal;
- volume mínimo necessário para aprendizado confiável.

### 15.3 Métricas de risco e governança

- fairness de exposição entre segmentos sintéticos;
- concentração excessiva em um único braço;
- violações de elegibilidade;
- casos bloqueados por guardrail;
- decisões que exigem humano no loop;
- cobertura de logs auditáveis;
- drift de contexto;
- drift de recompensa.

## 16. Avaliação offline e golden set

Antes de servir decisões, a política deve passar por avaliação offline reproduzível.

A avaliação deve responder:

- a política supera o baseline?
- o ganho é robusto ou depende de uma hipótese frágil?
- há segmentos sintéticos recebendo exposição injusta?
- a política evita ofertas inadequadas?
- casos adversariais são bloqueados ou tratados corretamente?
- métricas são reproduzíveis por comando ou notebook?

O golden set deve cobrir:

- casos típicos;
- casos de borda;
- segmentos sintéticos elegíveis;
- cenários adversariais;
- cold-start;
- ausência de contexto;
- oferta inelegível;
- tentativa de manipulação de contexto;
- decisão com baixa confiança;
- casos que exigem revisão humana.

## 17. Serviço ou interface demonstrável

A primeira versão deve ter uma forma simples de operar a decisão.

Opções aceitáveis:

- API REST;
- CLI;
- notebook executável;
- app demonstrável;
- combinação de API e interface leve.

Contrato de entrada sugerido:

```json
{
  "customer_context": {
    "synthetic_customer_id": "CUST-001",
    "channel": "mobile_app",
    "segment": "synthetic_segment_a",
    "features": {
      "previous_campaign_contacts": 2,
      "days_since_last_contact": 30,
      "digital_engagement_score": 0.72
    }
  },
  "request_metadata": {
    "request_id": "REQ-001",
    "timestamp": "2026-01-01T10:00:00Z"
  }
}
```

Contrato de saída sugerido:

```json
{
  "request_id": "REQ-001",
  "decision_id": "DEC-001",
  "selected_offer_id": "OFF-003",
  "selected_offer_name": "Oferta sintética de investimento conservador",
  "policy_version": "policy_ts_v1",
  "decision_mode": "adaptive_exploration",
  "reason_codes": [
    "eligible_offer",
    "high_expected_reward",
    "controlled_exploration"
  ],
  "requires_human_review": false,
  "guardrails_triggered": [],
  "audit_log_ref": "logs/decisions/2026-01-01.jsonl"
}
```

Tratamento de erro deve cobrir:

- contexto incompleto;
- canal inválido;
- nenhuma oferta elegível;
- política inexistente;
- versão de política desativada;
- falha de validação de schema.

## 18. Log auditável de decisão

Cada decisão deve gerar log com:

- `decision_id`;
- `request_id`;
- timestamp;
- contexto minimizado;
- ofertas elegíveis;
- oferta selecionada;
- política e versão;
- reason codes;
- score ou amostra usada, quando aplicável;
- flag de exploração;
- guardrails acionados;
- necessidade de revisão humana;
- hash ou referência da configuração;
- ambiente de execução.

Os logs devem evitar dados pessoais e seguir minimização.

## 19. Testes automatizados mínimos

A plataforma deve conter testes para:

- schema da base processada;
- schema dos dados sintéticos;
- contrato de entrada da decisão;
- contrato de saída da decisão;
- baseline determinístico;
- política adaptativa;
- regra de elegibilidade;
- registro de log auditável;
- golden set;
- bloqueio de casos adversariais;
- ausência de vazamento temporal conhecido.

## 20. Arquitetura-alvo em Azure

A arquitetura de referência deve usar exclusivamente Azure.

Camadas a cobrir:

### 20.1 Compute

Possíveis serviços:

- Azure Functions;
- Azure Container Apps;
- Azure Kubernetes Service, se houver justificativa de escala;
- Azure Machine Learning para experimentos, jobs e registry.

### 20.2 API

Possíveis serviços:

- Azure API Management;
- Azure Container Apps com endpoint HTTP;
- Azure Functions com HTTP trigger.

### 20.3 Dados

Possíveis serviços:

- Azure Data Lake Storage Gen2;
- Azure Blob Storage;
- Azure SQL Database ou Cosmos DB para metadados, se necessário.

### 20.4 IA, RAG e assistente

Possíveis serviços:

- Azure OpenAI Service;
- Azure AI Search;
- Azure Machine Learning;
- Azure Storage para documentos sintéticos de política;
- Managed Identity para acesso seguro.

### 20.5 Observabilidade

Possíveis serviços:

- Azure Monitor;
- Application Insights;
- Log Analytics Workspace;
- dashboards de métricas de decisão, recompensa, drift e risco.

### 20.6 Segurança, identidade e segredos

Possíveis serviços:

- Microsoft Entra ID;
- Azure Key Vault;
- Managed Identity;
- RBAC;
- Private Endpoints, quando aplicável.

### 20.7 Governança

Possíveis serviços e práticas:

- Azure Policy;
- tagging de recursos;
- controle de custos;
- versionamento de modelos e políticas;
- approval gates;
- segregação de ambientes.

## 21. FinOps, custo e escala

A narrativa de operação deve explicar:

- quais serviços geram custo fixo;
- quais serviços escalam por uso;
- como reduzir custo em ambiente pequeno;
- quando migrar de Functions/Container Apps para AKS;
- custo qualitativo por serviço;
- TCO qualitativo;
- ROI esperado em função de uplift de conversão e redução de tráfego desperdiçado.

Cenários a documentar:

1. **baixo volume:** execução local, storage simples, API leve;
2. **volume intermediário:** Container Apps, Azure ML, Application Insights;
3. **alto volume:** maior automação, filas, particionamento, autoscaling e governança reforçada.

## 22. Ciclo de vida MLOps

A empresa deve operar políticas como artefatos versionados.

Fluxo recomendado:

1. nova hipótese de oferta, canal ou mensagem;
2. criação ou atualização do catálogo de ofertas;
3. simulação offline;
4. avaliação contra baseline;
5. análise de risco e fairness;
6. registro de experimento em MLflow ou ferramenta equivalente;
7. revisão humana estruturada;
8. aprovação para ambiente controlado;
9. monitoramento de decisão e recompensa;
10. promoção, pausa ou rollback.

Elementos obrigatórios de processo:

- critérios de promoção;
- approval gate;
- rollback;
- versionamento de política;
- rastreio de experimentos;
- monitoramento de drift;
- monitoramento de recompensa;
- revisão periódica de documentação de modelo e sistema.

## 23. Assistente LLM/RAG

A plataforma deve incluir ou planejar um assistente com LLM para apoiar interpretação e governança.

Funções esperadas:

- resumir experimentos;
- recuperar políticas internas sintéticas;
- explicar por que uma decisão foi tomada;
- listar limitações de uma política;
- responder perguntas sobre métricas;
- auxiliar na preparação de relatório executivo.

Guardrails necessários:

- não inventar política inexistente;
- citar documentos recuperados;
- recusar perguntas fora do escopo;
- não expor dados pessoais;
- não recomendar aprovação automática de produto sensível;
- diferenciar explicação de decisão, recomendação comercial e decisão regulatória.

Documentos sintéticos que podem alimentar o RAG futuramente:

- política comercial sintética;
- guia de suitability sintética;
- procedimento de aprovação de política;
- playbook de incidentes;
- glossário de reason codes;
- matriz de guardrails.

## 24. Governança e LGPD

A documentação de governança deve cobrir:

- finalidade do tratamento;
- base legal simulada;
- minimização de dados;
- retenção;
- descarte;
- mapeamento de identificadores;
- atributos protegidos e proibidos;
- política de logs;
- política de telemetria;
- resposta a incidentes;
- revisão humana;
- intended use;
- usos fora de escopo;
- vieses conhecidos;
- limitações técnicas.

Riscos a explicitar:

- reward hacking;
- maximização de conversão em detrimento de suitability;
- manipulação de contexto;
- concentração injusta de exposição;
- decisões sensíveis sem humano no loop;
- uso indevido do assistente;
- drift de comportamento;
- inferência indevida por atributos proxy;
- logs excessivos;
- falsa sensação de prontidão regulatória.

## 25. Artefatos futuros a criar

Não serão criados agora, mas devem ser planejados:

- `README.md` com visão, execução local, mapa de pastas e limitações;
- `pyproject.toml` com dependências, versão de Python e ferramentas;
- `.env.example` com variáveis necessárias sem segredos reais;
- `data/kaggle/README.md`;
- notebook ou script de EDA;
- relatório de qualidade de dados;
- scripts de geração de dados sintéticos;
- scripts de baseline e política adaptativa;
- avaliação offline reproduzível;
- `data/golden_set/evaluation_cases.jsonl`;
- API, CLI, notebook ou app demonstrável;
- testes automatizados;
- `docs/architecture-azure.md`;
- `docs/model-card.md`;
- `docs/system-card.md`;
- `docs/lgpd-plan.md`;
- relatório técnico;
- slides executivos;
- roteiro de demonstração;
- plano de contingência para demonstração ao vivo.

## 26. Critérios internos de sucesso

A primeira versão será considerada sólida quando uma pessoa externa conseguir:

1. entender o problema e o posicionamento da empresa;
2. identificar a fonte dos dados;
3. verificar que a base tratada evita vazamento temporal conhecido;
4. reproduzir a geração de dados sintéticos;
5. executar baseline e política adaptativa;
6. comparar métricas quantitativas;
7. rodar avaliação offline;
8. inspecionar golden set;
9. solicitar uma decisão de exemplo;
10. ver oferta selecionada, versão da política e reason codes;
11. localizar log auditável;
12. entender arquitetura Azure;
13. entender plano de MLOps;
14. entender limites de uso, riscos e governança;
15. compreender valor de negócio, custo qualitativo e próximos passos.

## 27. Perguntas que precisarão ser respondidas futuramente

Algumas decisões já foram tomadas:

1. O banco cliente de referência será um banco digital.
2. O stakeholder do banco cliente será **Lary**, CTO do banco.
3. A dor prioritária será melhorar a área de empréstimos.
4. O foco inicial será empréstimo com garantia, com múltiplos tipos de colateral sintético: veículo, imóvel, investimentos e recebíveis.
5. O banco possui SuperApp e também agências físicas para clientes de relacionamento mais alto.

Ainda será necessário decidir:

1. Qual base pública será usada?
2. Qual nome definitivo da empresa/produto?
3. A primeira interface será API, CLI, notebook ou app?
4. O cenário principal de demonstração será SuperApp, agência física ou fluxo híbrido?
5. Quais ofertas sintéticas de empréstimo com garantia farão parte do catálogo inicial?
6. Quais tipos de garantia serão simulados?
7. Quais próximos passos serão tratados como braços além da oferta direta, como simulação, educação, coleta de documentação ou encaminhamento para especialista?
8. Quais segmentos sintéticos serão usados para análise de fairness?
9. Qual política será implementada primeiro: Thompson Sampling puro, contextual bandit ou UCB?
10. Como será calculada a recompensa?
11. Qual será a janela de delayed reward em uma jornada de empréstimo?
12. Qual ferramenta será usada para tracking: MLflow local, Azure ML ou ambas?
13. Qual formato de log será adotado?
14. O assistente LLM/RAG será implementado na primeira versão ou ficará como módulo planejado?
15. Quais documentos sintéticos alimentarão o RAG?
16. Qual será o roteiro da narrativa executiva para Lary?
17. Quais perguntas de domínio bancário precisarão ser respondidas por Lary durante a construção?

## 28. Decisão atual

A empresa será construída como uma plataforma pequena, técnica e demonstrável de experimentação adaptativa para ofertas financeiras, usando dados públicos e enriquecimento sintético. A primeira vertical será empréstimos, com foco em empréstimo com garantia para um banco digital com SuperApp e agências físicas para clientes de relacionamento mais alto. A solução priorizará rastreabilidade, avaliação, governança, MLOps e clareza de valor.

As personas operacionais serão usadas como mecanismo de construção e validação:

- **Lary, CTO da unidade de Empréstimos com Garantia**, para contexto de domínio, dor de negócio, viabilidade, prioridades, métricas, tecnologia e restrições da vertical;
- gerente de produto da startup para escopo e priorização;
- tech lead/engenheiro de ML da startup para arquitetura e implementação;
- product designer da startup para experiência, explicabilidade e narrativa;
- responsável por risco, compliance e LGPD da startup para governança e limites de uso.

Lary será tratado como a principal fonte de decisão quando surgir dúvida sobre o que faria sentido em uma instituição financeira, especialmente na área de empréstimos com garantia. O restante das personas representa o time construtor da plataforma.

Essa decisão passa a ser a referência principal para orientar os próximos passos do repositório.
