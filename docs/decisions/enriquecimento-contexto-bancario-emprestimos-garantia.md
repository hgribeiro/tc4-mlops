# Enriquecimento de Contexto — Banco Digital, SuperApp e Empréstimos com Garantia

## 1. Objetivo deste enriquecimento

Este documento adiciona contexto de mercado e de domínio bancário para orientar a construção da plataforma de experimentação adaptativa. O foco é o cliente representado por **Lary**, CTO de um banco digital que deseja melhorar a área de empréstimos, principalmente jornadas de **empréstimo com garantia**.

O objetivo não é copiar produtos reais de bancos, mas usar referências públicas para criar hipóteses plausíveis de produto, canais, métricas, riscos e jornadas sintéticas.

## 2. Hipótese de cliente

O banco cliente é um banco digital com:

- **SuperApp** como principal canal de relacionamento e escala;
- **agências físicas** ou atendimento presencial/consultivo para clientes de relacionamento mais alto;
- vertical prioritária de **empréstimos**;
- interesse especial em **empréstimos com garantia**;
- necessidade de combinar conversão, experiência, governança, risco e eficiência operacional.

Lary, CTO do banco, deve avaliar se a plataforma consegue apoiar decisões melhores sobre qual próximo passo apresentar a cada cliente elegível.

## 3. Sinais de mercado pesquisados

### 3.1 Crédito digital segue relevante, mesmo em ambiente desafiador

A pesquisa **Fintechs de Crédito Digital 2025**, da PwC Brasil com a Associação Brasileira de Crédito Digital, aponta que fintechs de crédito continuam crescendo em concessão, base de clientes e adaptação a cenário de juros altos, liquidez restrita e instabilidade. Isso reforça que crédito digital é um mercado competitivo, sensível a eficiência operacional e dependente de boa gestão de risco.

Fonte: PwC Brasil — Pesquisa Fintechs de Crédito Digital 2025  
https://www.pwc.com.br/pt/estudos/setores-atividade/financeiro/2025/pesquisa-fintechs-de-credito-digital-2025.html

**Implicação para a plataforma:** a proposta deve ser posicionada como ferramenta de melhoria de eficiência e aprendizado em crédito, não apenas como motor de recomendação comercial.

### 3.2 Bancos oferecem empréstimos com garantia em canais digitais

Referências públicas mostram que bancos tradicionais e digitais oferecem produtos de crédito com garantia de imóvel, veículo ou investimentos em canais digitais.

Exemplos:

- Banco do Brasil oferece empréstimo com garantia de imóvel em jornada 100% digital.  
  https://www.bb.com.br/site/pra-voce/emprestimo/emprestimo-pessoal/emprestimo-com-garantia/emprestimo-com-garantia-de-imovel/

- Banco BV oferece empréstimo com garantia de veículo, usando carro, ônibus ou caminhão quitado como garantia.  
  https://bv.com.br/emprestimos/emprestimo-com-garantia-de-veiculo

- Banco Inter oferece Home Equity, usando imóvel residencial ou comercial como garantia, sem necessidade de venda do imóvel.  
  https://inter.co/empresas/emprestimos/home-equity/

- Santander oferece crédito com garantia de investimentos, permitindo contratar pelo app e usar aplicações financeiras como garantia.  
  https://www.santander.com.br/credito-pessoal-investidor

- Bradesco Exclusive oferece crédito pessoal com garantia de investimentos, incluindo contratação pelo app e uso de CDB como garantia.  
  https://banco.bradesco/html/exclusive/produtos-servicos/emprestimo-e-financiamento/credito-pessoal/credito-pessoal-com-garantia-de-investimentos.shtm

**Implicação para a plataforma:** o catálogo sintético pode conter diferentes tipos de garantia, como imóvel, veículo e investimentos. Também pode conter próximos passos diferentes da oferta direta, como simulação, educação financeira, coleta de documentação ou encaminhamento para especialista.

### 3.3 Crédito com garantia costuma comunicar menor taxa e maior segurança relativa

Produtos de empréstimo com garantia geralmente comunicam condições mais atrativas do que crédito pessoal sem garantia, pois o colateral reduz risco para a instituição. O Banco Central mantém estatísticas públicas de taxas por modalidade, que podem ser usadas como referência qualitativa para justificar que modalidades de crédito possuem dinâmicas distintas de custo e risco.

Fonte: Banco Central do Brasil — Taxas de juros por modalidade  
https://www.bcb.gov.br/estatisticas/reporttxjuros

**Implicação para a plataforma:** a política adaptativa não deve otimizar apenas conversão. Ela deve considerar adequação do produto, risco, canal, momento e necessidade de explicação, principalmente quando a garantia envolve patrimônio relevante do cliente.

### 3.4 Atendimento digital e atendimento consultivo podem coexistir

Referências de mercado mostram que bancos podem combinar contratação digital com experiências diferenciadas para públicos de maior relacionamento. O Nubank Ultravioleta, por exemplo, comunica experiência exclusiva e suporte 24 horas para clientes de alta renda.

Fonte: Nubank Ultravioleta  
https://nubank.com.br/ultravioleta

**Implicação para a plataforma:** o banco de Lary pode operar uma lógica multicanal:

- SuperApp para escala, autosserviço, simulação e comunicações rápidas;
- agência física ou atendimento consultivo para clientes de maior relacionamento, operações maiores, dúvidas sobre garantia ou necessidade de orientação;
- fluxo híbrido quando o cliente começa no app e termina com especialista.

### 3.5 Open Finance pode apoiar personalização e crédito, mas exige consentimento e governança

Fontes públicas indicam que Open Finance permite, mediante consentimento, compartilhamento de informações financeiras entre instituições, apoiando personalização, ofertas mais adequadas e análise de crédito. O ecossistema também é associado a geração de operações de crédito e maior capacidade de compreender perfil financeiro do cliente.

Referências:

- BV Inspira — compartilhamento de dados entre bancos e personalização.  
  https://www.bv.com.br/bv-inspira/open-finance/compartilhamento-de-dados-entre-bancos

- Finsiders Brasil — Open Finance gerando operações de crédito segundo dados associados ao Banco Central.  
  https://finsidersbrasil.com.br/economia-open/open-finance-gera-r-18-bi-em-operacoes-de-credito-aponta-bc/

- Futurecom Digital — Open Finance e hiperpersonalização bancária.  
  https://digital.futurecom.com.br/transformaodigital/varejo/como-o-open-finance-esta-impulsionando-a-hiperpersonalizacao-bancaria/

**Implicação para a plataforma:** Open Finance pode aparecer como hipótese futura ou dado sintético consentido, mas não deve ser usado como premissa obrigatória na primeira versão. Se aparecer na narrativa, precisa vir acompanhado de consentimento, minimização, finalidade clara e governança.

## 4. Decisões enriquecidas para o produto

### 4.1 Vertical inicial

A vertical inicial será **empréstimos com garantia**.

Essa escolha é adequada porque:

- possui valor econômico relevante;
- exige decisão cuidadosa;
- tem múltiplos tipos de garantia;
- pode combinar canais digitais e consultivos;
- permite modelar delayed rewards;
- exige explicabilidade e governança;
- é um bom caso para comparar regra fixa com política adaptativa.

### 4.2 Canais iniciais

Os canais sintéticos recomendados são:

1. **SuperApp**
   - canal principal de escala;
   - ideal para simulação, oferta, educação, push e acompanhamento;
   - adequado para decisões de baixo atrito.

2. **Agência física / atendimento consultivo**
   - canal para clientes de relacionamento mais alto;
   - adequado para ofertas de maior complexidade;
   - útil quando a decisão exige explicação, documentação ou revisão humana.

3. **Fluxo híbrido**
   - cliente inicia no SuperApp;
   - sistema identifica necessidade de atendimento humano;
   - cliente é encaminhado para especialista ou agência.

### 4.3 Tipos de garantia sintética

O catálogo sintético pode conter:

- garantia de imóvel;
- garantia de veículo;
- garantia de investimentos;
- garantia por recebíveis ou outra garantia empresarial sintética, se a jornada incluir cliente PJ.

Para a primeira versão, recomenda-se começar com:

1. **empréstimo com garantia de veículo** — jornada mais simples;
2. **empréstimo com garantia de imóvel** — maior valor e maior necessidade de cautela;
3. **empréstimo com garantia de investimentos** — bom caso para cliente de alto relacionamento.

### 4.4 Braços do bandit

Os braços não precisam ser apenas ofertas finais de crédito. Eles podem representar próximos passos na jornada:

| Braço | Descrição | Canal provável | Cautela |
| --- | --- | --- | --- |
| `offer_vehicle_secured_loan` | Oferta de empréstimo com garantia de veículo | SuperApp | Média |
| `offer_home_equity_simulation` | Simulação de crédito com garantia de imóvel | SuperApp + consultivo | Alta |
| `offer_investment_secured_loan` | Crédito com garantia de investimentos | SuperApp ou agência | Alta |
| `educational_content_secured_credit` | Conteúdo educativo sobre crédito com garantia | SuperApp | Baixa |
| `request_documents` | Solicitação de documentação para pré-análise | SuperApp | Média |
| `route_to_specialist` | Encaminhar para especialista/agência | Híbrido | Alta |
| `no_offer_now` | Não ofertar neste momento | Todos | Governança |

Essa modelagem é melhor do que tratar todos os braços como produtos, porque empréstimo com garantia envolve etapas, confiança, educação, risco e documentação.

## 5. Hipóteses de jornadas

### 5.1 Jornada SuperApp — autosserviço

1. Cliente acessa o SuperApp.
2. O contexto indica possível interesse ou elegibilidade sintética.
3. A plataforma decide entre simulação, conteúdo educativo, oferta leve ou não ofertar.
4. Cliente interage ou ignora.
5. Recompensa intermediária é observada rapidamente: clique, início de simulação, envio de documento.
6. Recompensa final pode demorar: contratação, aprovação, desistência ou reprovação.

### 5.2 Jornada consultiva — cliente de alto relacionamento

1. Cliente possui relacionamento mais alto com o banco.
2. A plataforma identifica que uma oferta direta no app pode ser inadequada ou insuficiente.
3. O próximo passo recomendado é encaminhar para especialista ou agência.
4. O especialista explica opções de garantia e coleta informações.
5. Recompensa final demora mais e pode depender de análise humana.

### 5.3 Jornada híbrida

1. Cliente inicia simulação no SuperApp.
2. O contexto sugere maior complexidade ou valor elevado.
3. A plataforma recomenda continuar com especialista.
4. O atendimento humano finaliza orientação, documentação ou proposta.
5. A plataforma mede se o encaminhamento aumentou conversão qualificada, não apenas cliques.

## 6. Métricas sugeridas para Lary

### 6.1 Métricas de negócio

- aumento de conversão qualificada em simulações;
- aumento de propostas completas;
- redução de abandono na jornada de empréstimo;
- aumento de uso de garantias adequadas;
- redução de custo por proposta qualificada;
- taxa de encaminhamento efetivo para especialista;
- valor esperado por decisão;
- uplift contra baseline determinístico.

### 6.2 Métricas de risco e qualidade

- taxa de ofertas bloqueadas por guardrail;
- taxa de encaminhamento para revisão humana;
- exposição por segmento sintético;
- concentração de ofertas de maior risco;
- taxa de clientes expostos repetidamente à mesma mensagem;
- taxa de decisões sem explicação suficiente;
- divergência entre política adaptativa e regras mínimas de elegibilidade.

### 6.3 Métricas técnicas

- regret acumulado;
- recompensa acumulada;
- taxa de exploração;
- latência de decisão;
- cobertura de logs auditáveis;
- drift de contexto;
- drift de recompensa;
- estabilidade da política entre versões.

## 7. Recompensas atrasadas em empréstimos

Em crédito, a recompensa final raramente é imediata. Para empréstimos com garantia, a plataforma deve modelar eventos intermediários e finais.

### 7.1 Sinais intermediários

- visualização da oferta;
- clique;
- início de simulação;
- conclusão de simulação;
- aceite de contato;
- envio de documentação;
- agendamento com especialista;
- comparecimento à agência;
- consentimento para análise adicional.

### 7.2 Sinais finais

- proposta enviada;
- proposta aprovada;
- proposta contratada;
- proposta rejeitada;
- desistência;
- reprovação por política;
- encerramento sem conversão.

### 7.3 Janela sintética inicial

Sugestão inicial:

- sinais digitais simples: 0 a 2 dias;
- envio de documentação: 1 a 7 dias;
- análise de garantia: 3 a 20 dias;
- contratação final: 7 a 45 dias.

A janela exata deve ser validada com Lary.

## 8. Guardrails específicos para empréstimo com garantia

A plataforma deve evitar:

- empurrar crédito para cliente sem sinal mínimo de elegibilidade;
- repetir oferta excessivamente;
- apresentar oferta de garantia complexa sem explicação;
- maximizar clique em detrimento de contratação responsável;
- tratar encaminhamento para agência como falha, quando pode ser o melhor próximo passo;
- usar atributos sensíveis ou proxies indevidos;
- sugerir contratação automática sem revisão em casos de maior risco;
- prometer aprovação antes de análise formal;
- confundir simulação com concessão de crédito.

## 9. Perguntas para Lary

Estas perguntas devem ser usadas em conversas futuras com a persona Lary:

1. Qual é a principal dor atual da área de empréstimos: aquisição, conversão, abandono, custo, risco ou experiência?
2. O foco inicial deve ser cliente pessoa física, alta renda, pessoa jurídica ou uma mistura sintética?
3. Qual garantia é mais estratégica: veículo, imóvel ou investimentos?
4. O SuperApp já concentra simulações de empréstimo ou apenas comunicação/oferta?
5. Quando uma oferta deve ir para atendimento consultivo em vez de autosserviço?
6. Quais sinais indicam que o cliente está pronto para uma oferta direta?
7. Quais sinais indicam que o cliente precisa primeiro de educação ou simulação?
8. Quais métricas fariam Lary defender a continuidade do projeto?
9. Quais riscos fariam Lary pausar a iniciativa?
10. Qual volume mínimo de decisões seria plausível para aprender com bandits?
11. Quais decisões exigiriam aprovação humana?
12. Qual explicação uma área de risco/compliance esperaria ver em cada decisão?
13. O banco quer otimizar contratação final ou proposta qualificada?
14. Como tratar clientes de relacionamento alto sem prejudicar experiência premium?
15. Que diferença deve existir entre decisão no SuperApp e decisão em agência?

## 10. Decisão enriquecida

Com base nas referências públicas, a plataforma deve ser direcionada inicialmente para uma jornada de **experimentação adaptativa em empréstimos com garantia**, combinando SuperApp, atendimento consultivo e governança.

A decisão adaptativa não deve escolher apenas “qual produto vender”, mas sim o **melhor próximo passo responsável** para cada contexto sintético:

- ofertar;
- simular;
- educar;
- pedir documentação;
- encaminhar para especialista;
- não ofertar.

Essa formulação é mais adequada para o banco de Lary porque empréstimos com garantia envolvem maior complexidade, maior valor financeiro, maior sensibilidade reputacional e maior necessidade de explicabilidade.
