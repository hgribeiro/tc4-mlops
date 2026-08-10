# Camada de explicação LLM/RAG

Uma camada LLM/RAG para explicar decisões e consultar documentação não faz parte do aceite mínimo do escopo oficial atual do Datathon.

## Por que está fora de escopo

O novo PDF não exige IA generativa. A pontuação técnica prioriza notebook de EDA, baseline, Política Adaptativa superando o controle, MLflow e interface demonstrável. Reason Codes e logs auditáveis já permitem explicar a decisão sem introduzir dependências, avaliação e Guardrails adicionais para um componente generativo.

O LLM nunca seria autoridade de decisão e poderá ser reconsiderado como diferencial após a entrega oficial. No escopo atual, a explicação determinística baseada em Reason Codes é suficiente e reduz risco de invenção de política.

## Prior requests

- #10 — "Adicionar explicação LLM/RAG sem decisão operacional"
