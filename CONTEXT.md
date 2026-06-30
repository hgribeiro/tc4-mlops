# Personalização Responsável em Empréstimos com Garantia

Este contexto define a linguagem de domínio da plataforma demonstrável para decidir o próximo passo responsável em jornadas sintéticas de empréstimos com garantia.

## Language

**Lary**:
CTO da unidade de negócio de Empréstimos com Garantia e persona principal para decisões de produto, tecnologia, risco e governança.
_Avoid_: CTO genérica do banco, usuária final, aprovadora de crédito.

**Empréstimo com Garantia**:
Jornada de crédito em que uma garantia sintética, como veículo, imóvel ou investimentos, orienta a simulação e o próximo passo responsável.
_Avoid_: crédito genérico, empréstimo pessoal sem garantia.

**Cliente Sintético**:
Termo canônico para a pessoa física simulada usada no MVP, sem dados reais, identificadores pessoais ou atributos sensíveis.
_Avoid_: cliente real, lead real, usuário real do banco, pessoa jurídica.

**Garantia**:
Tipo de colateral sintético usado para diferenciar jornada, risco, explicação e delayed reward. No MVP, as garantias são veículo, imóvel e investimentos.
_Avoid_: ativo real de cliente, patrimônio real, dado sensível.

**Recebíveis Sintéticos**:
Garantia candidata para evolução futura, fora do MVP inicial, associada a maior complexidade de pessoa jurídica e fluxo de caixa sintético.
_Avoid_: escopo obrigatório do MVP, recebíveis reais.

**Próximo Passo Responsável**:
Termo canônico para a decisão da plataforma; é a ação de jornada escolhida pela política para orientar o cliente sintético sem prometer aprovação, limite, taxa ou contratação de crédito.
_Avoid_: próxima melhor oferta, recomendação de crédito, oferta final, aprovação, venda automática.

**Braço**:
Termo canônico para uma ação selecionável pela política adaptativa ou pelo baseline, como simular, educar, solicitar documentação, encaminhar para especialista ou não ofertar.
_Avoid_: produto vendido, campanha, oferta, aprovação.

**Simulação**:
Etapa de jornada em que o cliente sintético explora uma possibilidade de empréstimo com garantia sem gerar aprovação, proposta real, limite real ou taxa real. Pode anteceder uma **Proposta Qualificada Simulada**, mas não equivale a ela.
_Avoid_: oferta aprovada, proposta qualificada, contratação, concessão.

**Aprovação**:
Decisão formal de crédito, fora do escopo do MVP, que exigiria política real de risco, compliance e processos regulados.
_Avoid_: resultado da plataforma, simulação, proposta qualificada simulada.

**Contratação**:
Efetivação real de um empréstimo, fora do escopo do MVP e posterior a etapas formais não demonstradas pela plataforma.
_Avoid_: sucesso principal do MVP, proposta qualificada simulada, simulação concluída.

**Proposta Qualificada Simulada**:
Termo canônico para a métrica principal do MVP; ocorre quando o cliente sintético conclui uma simulação e fornece dados mínimos ou documentação para pré-análise.
_Avoid_: conversão genérica, clique, lead simples, proposta real, aprovação, contratação.

**Baseline Determinístico**:
Política simples baseada em regras transparentes usada como comparação mínima contra a política adaptativa.
_Avoid_: modelo campeão implícito, regra bancária real.

**Política Adaptativa**:
Política de decisão que aprende com recompensas simuladas e explora apenas entre braços elegíveis e seguros. No MVP, a abordagem preferida é Thompson Sampling contextual simplificado.
_Avoid_: motor de aprovação, modelo de crédito, exploração sem guardrail.

**Guardrail**:
Restrição de segurança, governança ou elegibilidade aplicada antes da política adaptativa ou do baseline para bloquear, restringir ou redirecionar braços inseguros. A política só pode escolher entre braços elegíveis após guardrails.
_Avoid_: sugestão opcional, explicação posterior, regra comercial privada.

**Reason Code**:
Código explicável associado à decisão para comunicar por que um próximo passo foi selecionado ou bloqueado.
_Avoid_: justificativa opaca, feature importance sem tradução de negócio.

**Humano no Loop**:
Participação de especialista, agência, risco ou revisão humana quando a decisão envolve complexidade, baixa confiança, alto valor sintético ou comunicação sensível.
_Avoid_: aprovação automática disfarçada, atendimento obrigatório em todos os casos.

**Delayed Reward**:
Recompensa observada após uma janela sintética de tempo, diferente por garantia, refletindo que jornadas de crédito com garantia não convertem instantaneamente.
_Avoid_: clique imediato como sucesso final.

**LLM/RAG**:
Camada de explicação, consulta documental e apoio à governança. Não escolhe braços, não aprova crédito, não substitui guardrails, não substitui reason codes e não substitui baseline ou política adaptativa.
_Avoid_: decisor principal, motor de crédito, fonte de política inventada, substituto de auditoria.

## Flagged ambiguities

**Oferta**:
No MVP, evitar usar “oferta” como ação principal. Quando necessário, diferenciar explicitamente simulação, proposta, aprovação e contratação.

**Cliente**:
Ambiguidade resolvida: quando aparecer sozinho neste projeto, “cliente” significa **Cliente Sintético** pessoa física, não cliente real do banco.

**Conversão**:
Usar com cuidado. A conversão principal do MVP é proposta qualificada simulada, não clique, contratação ou aprovação.

## Example dialogue

Dev: Para esse cliente sintético com veículo e bom engajamento no SuperApp, podemos mostrar uma oferta?

Especialista de domínio: No MVP, chame isso de simulação, não oferta. O próximo passo responsável pode ser `simulate_vehicle_secured_loan`, desde que os guardrails estejam limpos e a saída diga que não é aprovação.

Dev: E se o cliente tiver imóvel e alto valor sintético?

Especialista de domínio: A garantia é mais complexa. A política pode escolher `simulate_home_equity`, mas provavelmente com `requires_human_review = true` ou `route_to_specialist`.

Dev: O LLM pode decidir esse braço?

Especialista de domínio: Não. O LLM/RAG explica a decisão e consulta documentação, mas quem escolhe o braço é o baseline ou a política adaptativa, após guardrails.
