# Pesquisa de mercado — Next-best-action, experimentação adaptativa e personalização responsável

## 1. Resumo executivo

A tese da startup — uma plataforma de **experimentação adaptativa** para decidir o **melhor próximo passo responsável** em ofertas financeiras — tem paralelos claros no mercado em três categorias:

1. **Customer decisioning / next-best-action enterprise**, com players como Pega, SAS, Salesforce e Adobe.
2. **Personalização e experimentação digital**, com players como Dynamic Yield/Mastercard, Optimizely, Eppo/Datadog, Statsig e LaunchDarkly.
3. **MLOps, IA responsável e explainability**, com players e referências como Dataiku, práticas de Responsible AI no setor financeiro e governança com humano no loop.

Os cases mais diretamente comparáveis estão em bancos que usam decisão centralizada e personalização omnichannel, como Citi, Wells Fargo, National Australia Bank, NatWest e Standard Chartered com Pega; U.S. Bank e TSB com Adobe; PostFinance e Jyske Bank com SAS; e Maybank/Davivienda com Dataiku.

O espaço competitivo valida a demanda por personalização em escala, mas a proposta do projeto deve evitar claims exagerados. O diferencial mais defensável é o recorte: **empréstimos com garantia**, múltiplos colaterais, delayed rewards, guardrails, auditoria e decisão de jornada — não apenas marketing, clique ou cross-sell.

## 2. Casos e referências relevantes

### 2.1 Pega Customer Decision Hub — bancos e next-best-action

Pega é o benchmark mais direto para a narrativa de **centralized decisioning** e **next best action** em serviços financeiros.

Casos encontrados:

- National Australia Bank: personalização com abordagem orientada por IA.
- NatWest: mensagens hiperpersonalizadas e aumento de customer lifetime value.
- Citi: motor de decisão omnichannel em web, mobile, branch e canais de atendimento.
- Wells Fargo: personalização de conversas em tempo real para grande base de clientes.
- Standard Chartered: decisão centralizada e next-best-actions em múltiplos mercados.

Uso na nossa narrativa:

- Validar que bancos grandes investem em motores centralizados de decisão.
- Mostrar que next-best-action é uma categoria existente.
- Diferenciar o MVP: nosso foco é demonstrável, sintético, governado e específico para empréstimos com garantia.

Fontes:

- https://www.pega.com/customers/national-australia-bank-customer-decision-hub
- https://www.pega.com/customers/natwest-unlocks-customer-decision-hub
- https://www.pega.com/customers/citi-customer-decision-hub
- https://www.pega.com/customers/wells-fargo-customer-decision-hub
- https://www.pega.com/customers/standard-chartered-bank-customer-decision-hub

### 2.2 Contextual bandits e experimentação adaptativa

Há evidências fortes em blogs técnicos de que bandits são usados para otimizar decisões digitais quando A/B testing clássico é lento ou desperdiça tráfego.

Casos encontrados:

- Adyen: uso de contextual multi-armed bandits para otimizar conversão de pagamentos.
- Wealthfront: uso de bandit testing como melhoria sobre A/B tests.
- Uber: contextual bandits para personalização de comunicação CRM.
- Braze: material explicativo sobre AI decisioning com contextual bandits.

Uso na nossa narrativa:

- Justificar por que uma política adaptativa pode aprender melhor que um baseline fixo.
- Explicar exploração vs. exploração controlada.
- Reforçar que bandits precisam de guardrails, principalmente em crédito.

Fontes:

- https://medium.com/adyen/optimizing-payment-conversion-rates-using-contextual-multi-armed-bandits-644e543e9c0e
- https://eng.wealthfront.com/2022/06/07/how-bandit-testing-improves-a-b-tests-at-wealthfront/
- https://www.uber.com/pk/en/blog/enhancing-personalized-crm/
- https://www.braze.com/resources/articles/contextual-bandits

### 2.3 Adobe Experience Platform / Journey Optimizer

Adobe aparece como concorrente/plataforma adjacente para personalização omnichannel e offer decisioning.

Casos encontrados:

- U.S. Bank: Adobe Experience Platform e offer decisioning para experiências personalizadas.
- TSB: personalização em canais digitais, app, telefone e atendimento presencial.
- Prudential: experiências financeiras personalizadas com Adobe Experience Manager, Target, AEP e Marketo.

Uso na nossa narrativa:

- Validar personalização em serviços financeiros.
- Posicionar nossa proposta como mais estreita e mais governada para decisão de crédito com garantia, não como suíte ampla de marketing experience.

Fontes:

- https://business.adobe.com/customer-success-stories/us-bank-case-study.html
- https://business.adobe.com/au/customer-success-stories/tsb-case-study.html
- https://news.adobe.com/news/news-details/2022/adobe-to-help-u-s-bank-accelerate-personalization-in-consumer-banking
- https://blog.adobe.com/en/publish/2023/03/31/prudential-financial-collaborates-with-adobe-deliver-personalized-financial-experiences

### 2.4 SAS Customer Intelligence

SAS é relevante por ter presença histórica em analytics bancário, campanhas e customer intelligence.

Casos encontrados:

- PostFinance: automação e otimização de campanhas, maior eficiência e conversão.
- Jyske Bank: personalização de experiências bancárias.
- Slovenská sporiteľňa: caso divulgado com conversão em POC usando SAS Customer Intelligence.
- Moneta Money Bank: modernização de marketing e decisões em tempo real.

Uso na nossa narrativa:

- Mostrar que instituições financeiras buscam personalização com governança analítica.
- Diferenciar por ser um MVP focado em decisão de próximo passo com colateral, delayed rewards e logs auditáveis.

Fontes:

- https://www.sas.com/en_us/customers/postfinance-english.html
- https://www.sas.com/en_sa/customers/jyske-bank.html
- https://communities.sas.com/t5/SAS-Customer-Intelligence/From-4-Months-to-17-6-Conversion-How-Slovakia-s-Largest-Bank/td-p/973890
- https://www.sas.com/en_th/news/press-releases/2026/april/moneta-money-bank--faster-marketing-campaigns--smarter-decisions.html

### 2.5 Dataiku e next-best-offer para banking

Dataiku é relevante pela interseção de MLOps, analytics, governança e soluções de next-best-offer.

Referências encontradas:

- Dataiku Next Best Offer for Banking.
- LLM-enhanced Next Best Offer.
- Maybank Malaysia: personalização e customer-centric banking.
- Davivienda/DaviPlata: recommendation machines para inclusão financeira.

Uso na nossa narrativa:

- Reforçar que next-best-offer em banking é uma categoria reconhecida.
- Posicionar nosso projeto como mais prescritivo na decisão de jornada e mais explícito em governança/guardrails.

Fontes:

- https://www.dataiku.com/solutions/catalog/next-best-offer-for-banking/
- https://www.dataiku.com/solutions/catalog/llm-enhanced-next-best-offer/
- https://community.dataiku.com/discussion/45023/maybank-malaysia-redefining-customer-centric-banking
- https://community.dataiku.com/discussion/35266/davivienda-recommendation-machines-an-analytical-window-to-financial-inclusion

## 3. Concorrentes e plataformas similares

| Nome | Tipo | Relevância | Como usar na narrativa |
| --- | --- | --- | --- |
| Pega Customer Decision Hub | Customer decisioning / NBA | Concorrente conceitual mais próximo em bancos | Categoria validada; diferenciar por foco em empréstimos com garantia e MVP demonstrável |
| Salesforce Einstein / Financial Services Cloud | CRM + IA + recomendação | Forte em CRM financeiro e produtividade de advisor | Comparar com decisão orientada a relacionamento, mas evitar dizer que competimos com CRM inteiro |
| Adobe Experience Platform / Journey Optimizer | Personalização omnichannel / offer decisioning | Forte em dados, jornadas e experiências | Diferenciar por governança de crédito e colateral |
| SAS Customer Intelligence | Analytics + marketing decisioning | Forte em bancos e analytics tradicional | Diferenciar por experimentação adaptativa e logs do MVP |
| Dataiku | MLOps/AI platform + NBO banking | Forte em construção governada de soluções analíticas | Referência para MLOps e next-best-offer |
| Dynamic Yield / Mastercard | Personalização e experiência digital | Forte em recomendação/ofertas digitais | Referência para personalização algorítmica, menos focada em crédito regulado |
| Optimizely | Experimentação e feature experimentation | Referência em A/B testing e experimentação | Comparar com necessidade de bandits e delayed rewards |
| Eppo / Datadog Experiments | Experimentação moderna | Forte em análise confiável e self-service | Referência para cultura de experimentação |
| Statsig | Feature flags, experimentation, product analytics | Plataforma moderna de produto e experimentação | Útil para narrativa de métricas e controle de rollout |
| LaunchDarkly | Feature flags e runtime control | Forte em rollout, rollback e controle operacional | Útil para narrativa de governança e rollback |
| Braze | Customer engagement com IA decisioning | Referência didática em contextual bandits | Apoia explicação de bandits para CRM/personalização |

Fontes adicionais:

- https://dynamicyield.com/
- https://www.dynamicyield.com/glossary/next-best-action-marketing/
- https://geteppo.com/
- https://statsig.com/
- https://launchdarkly.com/

## 4. Diferenciais possíveis da nossa proposta

A pesquisa sugere que a proposta fica mais forte se não tentar parecer uma suíte genérica como Pega, Adobe ou Salesforce. O diferencial deve ser:

1. **Verticalização em empréstimos com garantia**  
   A plataforma considera veículo, imóvel, investimentos e recebíveis sintéticos como jornadas diferentes, com riscos, tempos de recompensa e necessidades de explicação diferentes.

2. **Next-best-action responsável, não next-best-offer puro**  
   A decisão pode ser oferta, simulação, conteúdo educativo, solicitação de documento, especialista ou `no_offer_now`.

3. **Governança by design**  
   Reason codes, logs auditáveis, `policy_version`, guardrails, humano no loop e rollback aparecem na própria saída da decisão.

4. **Delayed rewards explícitos**  
   Em crédito com garantia, proposta qualificada e contratação não acontecem imediatamente. O MVP deve modelar sinais intermediários e recompensas atrasadas.

5. **Comparação baseline vs. política adaptativa**  
   A narrativa fica mais crível se mostrar baseline determinístico e política adaptativa com controle de exploração.

6. **Dados sintéticos e demonstrabilidade segura**  
   O MVP evita dados reais e promessas regulatórias, mas mostra arquitetura, logs e decisões auditáveis.

## 5. Riscos de claims exagerados

Evitar afirmar que a plataforma:

- substitui Pega, Salesforce, Adobe, SAS ou Dataiku;
- aprova crédito automaticamente;
- calcula taxa, limite ou elegibilidade real;
- está pronta para produção regulada;
- garante aumento de conversão real;
- resolve fairness em crédito real;
- usa IA generativa para tomar decisão financeira autônoma;
- personaliza ofertas sem necessidade de compliance, risco ou revisão humana;
- transforma clique em sucesso de negócio.

Claims mais seguros:

- “plataforma demonstrável”;
- “decide o próximo passo responsável em contexto sintético”;
- “compara baseline e política adaptativa”;
- “inclui logs auditáveis e reason codes”;
- “não representa aprovação de crédito”;
- “usa dados sintéticos para demonstrar MLOps e governança”.

## 6. Tabela de evidências

| Fonte | Tipo | Link | Evidência útil | Uso recomendado |
| --- | --- | --- | --- | --- |
| Pega — Citi | Case bancário | https://www.pega.com/customers/citi-customer-decision-hub | Motor de decisão omnichannel em banco | Validar NBA em web/mobile/branch/agent |
| Pega — Wells Fargo | Case bancário | https://www.pega.com/customers/wells-fargo-customer-decision-hub | Personalização de conversas em tempo real | Mostrar escala e “next best conversation” |
| Pega — Standard Chartered | Case bancário | https://www.pega.com/customers/standard-chartered-bank-customer-decision-hub | Decisioning centralizado em múltiplos mercados | Referência de central decision brain |
| Adyen | Blog técnico | https://medium.com/adyen/optimizing-payment-conversion-rates-using-contextual-multi-armed-bandits-644e543e9c0e | Contextual bandits para conversão de pagamentos | Justificar bandits em decisões digitais financeiras adjacentes |
| Wealthfront | Blog engenharia | https://eng.wealthfront.com/2022/06/07/how-bandit-testing-improves-a-b-tests-at-wealthfront/ | Bandit testing melhora A/B testing | Explicar exploração/exploitation |
| Uber | Blog engenharia | https://www.uber.com/pk/en/blog/enhancing-personalized-crm/ | Contextual bandits em CRM personalizado | Apoiar personalização de comunicação |
| Adobe — U.S. Bank | Case | https://business.adobe.com/customer-success-stories/us-bank-case-study.html | AEP e offer decisioning em banco | Referência de offer decisioning e dados de cliente |
| SAS — PostFinance | Case | https://www.sas.com/en_us/customers/postfinance-english.html | SAS Customer Intelligence em campanhas financeiras | Validar analytics/customer intelligence em banco |
| Dataiku — NBO Banking | Solução | https://www.dataiku.com/solutions/catalog/next-best-offer-for-banking/ | Solução explícita de next-best-offer para banking | Referência direta de categoria |
| Dynamic Yield | Plataforma | https://dynamicyield.com/ | Personalização algorítmica e matching de ofertas | Concorrente/adjacente em personalização digital |
| Statsig | Plataforma | https://statsig.com/ | Experimentos, feature flags e analytics | Referência para experimentação moderna |
| LaunchDarkly | Plataforma | https://launchdarkly.com/ | Runtime control, rollout e rollback | Referência para governança operacional |

## 7. Fontes recomendadas para citar nos docs do projeto

Para documentação do MVP, priorizar:

1. **Pega Citi, Wells Fargo ou Standard Chartered** — para validar next-best-action/decisioning em bancos.
2. **Adyen ou Wealthfront** — para validar contextual bandits/bandit testing em contexto financeiro ou fintech.
3. **Adobe U.S. Bank** — para validar offer decisioning e personalização em banco.
4. **Dataiku Next Best Offer for Banking** — para validar a categoria next-best-offer em banking.
5. **LaunchDarkly ou Statsig** — para embasar rollout, rollback e experimentação controlada.
6. **FSB Responsible AI consultation** — para reforçar humano no loop, governança e explainability em instituições financeiras.

Fonte de Responsible AI:

- https://www.fsb.org/uploads/P100626.pdf

## 8. Implicação para o próximo artefato

Ao criar `docs/product/offer-arms.md`, devemos deixar claro que os braços não são apenas ofertas. Eles são **ações de jornada auditáveis**. Essa é a principal diferença entre uma plataforma de marketing/cross-sell genérica e uma plataforma responsável para empréstimos com garantia.
