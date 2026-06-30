# Drafts de issues — MVP Lary

Status: drafts prontos para publicar no GitHub Issues quando o `gh` CLI estiver disponível.

Label sugerido para todas as issues: `ready-for-agent`.

## 1. Documentar base pública e schema mínimo do Cliente Sintético

## What to build

Documentar a base pública usada como proxy e definir o schema mínimo do Cliente Sintético para o MVP de Próximo Passo Responsável. A entrega deve deixar claro quais dados podem existir, quais são proibidos, como evitar vazamento temporal e como enriquecer a base pública com contexto sintético de garantia, canal, risco, estágio da jornada e auditoria.

## Acceptance criteria

- [ ] A base pública principal está escolhida e documentada, incluindo fonte, link, versão/licença quando disponível, target, colunas originais, limitações e instruções de download.
- [ ] A coluna `duration`, se presente na base Bank Marketing, é explicitamente removida ou ignorada para decisão pré-interação por vazamento temporal.
- [ ] O schema mínimo do Cliente Sintético cobre garantia, canal, estágio da jornada, risco sintético, confiança da política, engajamento, completude de contexto, segmento não sensível e campos mínimos de auditoria.
- [ ] O schema explicita dados proibidos, incluindo identificadores pessoais, atributos sensíveis, renda/patrimônio reais e regras comerciais privadas.
- [ ] Recebíveis Sintéticos aparecem apenas como evolução futura, fora do MVP inicial.

## Blocked by

None - can start immediately

---

## 2. Criar contrato executável do Próximo Passo Responsável

## What to build

Criar o primeiro caminho executável para decidir um Próximo Passo Responsável a partir de um Cliente Sintético. A decisão pode usar uma política stub, mas já deve expor o contrato de entrada/saída, aplicar estrutura de log auditável e devolver uma resposta que respeite os termos canônicos do projeto.

## Acceptance criteria

- [ ] Existe um comando executável que recebe um Cliente Sintético mínimo e retorna uma decisão válida.
- [ ] A saída contém `decision_id`, `request_id`, `selected_action`, `policy_version`, `reason_codes`, `requires_human_review`, `guardrails_triggered` e referência de log auditável.
- [ ] A saída explicita que a decisão não é Aprovação, não é Contratação, não define taxa e não define limite real.
- [ ] O log auditável usa minimização de dados e não grava dados proibidos.
- [ ] Há pelo menos um exemplo executável documentado.

## Blocked by

- #1 Documentar base pública e schema mínimo do Cliente Sintético

---

## 3. Implementar cena veículo digital simples com baseline

## What to build

Implementar uma fatia demonstrável em que um Cliente Sintético pessoa física, com garantia de veículo, bom engajamento digital e canal SuperApp, recebe o Próximo Passo Responsável `simulate_vehicle_secured_loan` pelo Baseline Determinístico. A decisão deve ser auditável, explicável e segura.

## Acceptance criteria

- [ ] Um caso de veículo digital simples retorna `simulate_vehicle_secured_loan` como `selected_action`.
- [ ] A decisão inclui Reason Codes compatíveis com veículo, canal digital, contexto suficiente e ausência de Guardrail crítico.
- [ ] `requires_human_review` é `false` no caso simples, salvo se o próprio contexto sintético indicar exceção.
- [ ] A decisão gera log auditável completo.
- [ ] O cenário é executável de ponta a ponta por comando e pode ser usado na demo da Lary.

## Blocked by

- #2 Criar contrato executável do Próximo Passo Responsável

---

## 4. Implementar cena imóvel complexo com Humano no Loop

## What to build

Implementar uma fatia demonstrável em que um Cliente Sintético com garantia de imóvel, alto valor sintético, baixa confiança ou complexidade documental é direcionado para Humano no Loop. A decisão deve preferir `route_to_specialist` ou `simulate_home_equity` com revisão humana, sem parecer oferta direta ou aprovação.

## Acceptance criteria

- [ ] Um caso complexo de imóvel retorna `route_to_specialist` ou `simulate_home_equity` com `requires_human_review = true`.
- [ ] A decisão inclui Reason Codes relacionados a complexidade do colateral, orientação necessária, baixa confiança ou alto valor sintético.
- [ ] A saída preserva a separação entre Simulação, Proposta Qualificada Simulada, Aprovação e Contratação.
- [ ] A decisão gera log auditável completo.
- [ ] O cenário é executável de ponta a ponta e cobre a segunda cena da demo.

## Blocked by

- #2 Criar contrato executável do Próximo Passo Responsável

---

## 5. Implementar cena inelegível/adversarial com Guardrail

## What to build

Implementar uma fatia demonstrável em que Guardrails rodam antes da política e bloqueiam simulações inadequadas para contexto inelegível, adversarial, incompleto não recuperável, canal inválido ou repetição excessiva. A decisão deve retornar `no_offer_now` ou conteúdo educativo quando apropriado.

## Acceptance criteria

- [ ] Um caso adversarial ou inelegível aciona ao menos um Guardrail antes da seleção final do Braço.
- [ ] A política não consegue selecionar Braço bloqueado por Guardrail.
- [ ] A decisão retorna `no_offer_now` ou `educational_content_secured_credit`, conforme o contexto.
- [ ] A saída inclui Reason Codes e `guardrails_triggered` compatíveis com o bloqueio.
- [ ] O cenário é executável de ponta a ponta e cobre a terceira cena da demo.

## Blocked by

- #2 Criar contrato executável do Próximo Passo Responsável

---

## 6. Implementar cena investimentos para cliente de relacionamento alto

## What to build

Implementar uma fatia demonstrável em que um Cliente Sintético de relacionamento alto e garantia de investimentos recebe um Próximo Passo Responsável compatível com liquidez, comunicação de risco e possível Humano no Loop. O comportamento deve evitar qualquer aparência de recomendação de investimento ou Aprovação de crédito.

## Acceptance criteria

- [ ] Um caso elegível de investimentos retorna `simulate_investment_secured_loan` ou `route_to_specialist`, conforme confiança e sensibilidade do contexto.
- [ ] A decisão inclui Reason Codes relacionados a garantia de investimentos, relacionamento sintético e comunicação de risco.
- [ ] Casos sensíveis, de alto valor ou baixa confiança exigem `requires_human_review = true`.
- [ ] A saída explicita que não é recomendação de investimento, Aprovação ou Contratação.
- [ ] O cenário é executável de ponta a ponta e cobre o terceiro tipo de garantia obrigatório no MVP.

## Blocked by

- #2 Criar contrato executável do Próximo Passo Responsável

---

## 7. Criar golden set e avaliação offline do baseline

## What to build

Criar um golden set com casos de avaliação e um caminho de avaliação offline para o Baseline Determinístico. A avaliação deve verificar se cada caso retorna o Próximo Passo Responsável esperado, com Reason Codes, Guardrails e revisão humana coerentes.

## Acceptance criteria

- [ ] O golden set contém pelo menos 20 casos cobrindo típicos, borda, adversariais, inelegíveis, cold-start, contexto incompleto, canal inválido e repetição excessiva.
- [ ] Cada caso contém contexto, ação esperada, critério de sucesso/recompensa esperada, justificativa e pass/fail explícito.
- [ ] Existe um comando que executa o Baseline Determinístico contra o golden set.
- [ ] O relatório mostra pass/fail por caso e cobertura de Braços, Guardrails, Reason Codes e logs.
- [ ] Falhas de contrato de saída ou ausência de log auditável quebram a avaliação.

## Blocked by

- #3 Implementar cena veículo digital simples com baseline
- #4 Implementar cena imóvel complexo com Humano no Loop
- #5 Implementar cena inelegível/adversarial com Guardrail
- #6 Implementar cena investimentos para cliente de relacionamento alto

---

## 8. Simular Delayed Reward por garantia

## What to build

Adicionar simulação de Delayed Reward por tipo de garantia, conectando eventos intermediários da jornada à Proposta Qualificada Simulada. A avaliação deve refletir que veículo, imóvel e investimentos têm janelas sintéticas diferentes e que clique imediato não é a métrica principal.

## Acceptance criteria

- [ ] Veículo usa janela sintética de 2 a 20 dias para Delayed Reward.
- [ ] Imóvel usa janela sintética de 7 a 45 dias para Delayed Reward.
- [ ] Investimentos usa janela sintética de 1 a 15 dias para Delayed Reward.
- [ ] Eventos intermediários como conteúdo visualizado, simulação iniciada, documentação enviada e atendimento aceito são representados com pesos ou sinais qualitativos.
- [ ] A avaliação distingue Proposta Qualificada Simulada de clique, Aprovação e Contratação.

## Blocked by

- #7 Criar golden set e avaliação offline do baseline

---

## 9. Comparar baseline contra Política Adaptativa

## What to build

Implementar a comparação offline entre Baseline Determinístico e Política Adaptativa usando Thompson Sampling contextual simplificado. A política adaptativa só pode explorar entre Braços elegíveis após Guardrails, e o relatório deve mostrar valor incremental sem otimizar apenas clique.

## Acceptance criteria

- [ ] A Política Adaptativa usa contexto sintético como garantia, canal, segmento sintético e estágio da jornada.
- [ ] A exploração ocorre apenas entre Braços elegíveis e seguros após Guardrails.
- [ ] A atualização usa feedback observado, incluindo Delayed Rewards e eventos censurados quando aplicável.
- [ ] O relatório compara baseline vs adaptativo com recompensa acumulada, regret acumulado, taxa de exploração, exposição por Braço, Proposta Qualificada Simulada e fairness por segmento sintético.
- [ ] O resultado preserva logs auditáveis e `policy_version` para cada decisão avaliada.

## Blocked by

- #8 Simular Delayed Reward por garantia

---

## 10. Adicionar explicação LLM/RAG sem decisão operacional

## What to build

Adicionar uma camada de explicação e governança baseada em LLM/RAG que, dado um `decision_id` ou log auditável, explica a decisão usando Reason Codes e documentação do projeto. Essa camada não pode escolher Braços, alterar decisões, aprovar crédito, substituir Guardrails ou inventar política.

## Acceptance criteria

- [ ] Dado um identificador de decisão, a camada gera uma explicação em linguagem clara baseada no log, Reason Codes e documentação disponível.
- [ ] A explicação diferencia Simulação, Proposta Qualificada Simulada, Aprovação e Contratação.
- [ ] A camada não altera `selected_action`, `policy_version`, Guardrails ou resultado da política.
- [ ] A resposta recusa ou limita perguntas que peçam aprovação, taxa, limite real ou regra bancária privada.
- [ ] Há exemplo demonstrável de explicação para pelo menos uma cena do MVP.

## Blocked by

- #7 Criar golden set e avaliação offline do baseline

---

## 11. Documentar governança mínima do MVP

## What to build

Criar o pacote mínimo de governança do MVP para que Lary consiga avaliar uso pretendido, limites, riscos, fairness, Humano no Loop, auditoria, rollback e ciclo de aprovação de política. A documentação deve reforçar que a solução é sintética e demonstrável, não produção bancária regulada.

## Acceptance criteria

- [ ] O pacote documenta intended use, usos fora de escopo, limitações e riscos conhecidos.
- [ ] O pacote documenta dados proibidos, minimização de dados, LGPD simulada e auditoria de decisão.
- [ ] O pacote documenta fairness por segmento sintético, Humano no Loop e critérios de revisão humana.
- [ ] O pacote documenta rollback/pause policy e aprovação humana antes de promover política.
- [ ] A documentação referencia a separação entre Simulação, Proposta Qualificada Simulada, Aprovação e Contratação.

## Blocked by

- #7 Criar golden set e avaliação offline do baseline
- #9 Comparar baseline contra Política Adaptativa

---

## 12. Documentar arquitetura Azure/MLOps e roteiro final da demo

## What to build

Documentar uma arquitetura Azure/MLOps demonstrável e preparar o roteiro final da demo para Lary. A narrativa deve conectar as três cenas mínimas, a comparação baseline vs Política Adaptativa, logs auditáveis, Reason Codes, Guardrails, Delayed Rewards e o plano de contingência.

## Acceptance criteria

- [ ] A arquitetura inclui diagrama Mermaid e mapeamento de serviços Azure adequados para ingestão, experimentação, tracking, monitoramento, segredos, identidade e observabilidade.
- [ ] A documentação define ambientes local, teste e produção simulada, incluindo aprovação humana antes de promoção de política e rollback.
- [ ] O roteiro cobre cliente digital simples com veículo, imóvel/complexidade com Humano no Loop e caso inelegível/adversarial com Guardrail.
- [ ] A demo mostra log auditável, Reason Codes, `policy_version`, diferença entre baseline e Política Adaptativa e Delayed Reward.
- [ ] Existe plano de contingência caso a demo ao vivo falhe.

## Blocked by

- #9 Comparar baseline contra Política Adaptativa
- #10 Adicionar explicação LLM/RAG sem decisão operacional
- #11 Documentar governança mínima do MVP
