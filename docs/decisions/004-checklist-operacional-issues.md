# Decisão 004 — Checklist operacional para execução de issues

## 1. Contexto

As issues do GitHub passaram a ser a fila operacional de implementação do MVP. O checklist de planejamento em `docs/decisions/003-checklist-planejamento-mvp-lary.md` continua sendo a visão de produto e progresso macro, mas ele não substitui o fluxo de execução de cada issue.

A falta de sincronização entre issue, código, documentação, commit e repositório remoto pode deixar o projeto em estado ambíguo: uma entrega pode estar implementada localmente, mas não refletida no checklist, não publicada no remoto ou não registrada na própria issue.

## 2. Decisão

Toda issue implementada por agente deve seguir um checklist operacional explícito, mantendo três superfícies sincronizadas:

1. código e testes no repositório;
2. documentação/checklists de decisão quando a entrega muda o estado do MVP;
3. GitHub remoto, incluindo commit publicado e status da issue.

## 3. Checklist antes de iniciar uma issue

- [ ] Confirmar que a árvore Git está limpa ou registrar mudanças existentes antes de editar.
- [ ] Sincronizar com o remoto quando possível:

```bash
git pull --ff-only
```

- [ ] Ler a issue com comentários e labels:

```bash
gh issue view <numero> --comments
```

- [ ] Verificar se a issue está desbloqueada e com label compatível, como `ready-for-agent`.
- [ ] Ler documentos de decisão, ADRs, PRD e persona Lary quando a issue envolver produto, domínio, risco ou narrativa.
- [ ] Identificar quais checklists documentais serão afetados pela entrega.

## 4. Checklist durante a implementação

- [ ] Usar TDD quando houver seam claro de contrato, CLI, API, avaliação offline ou regra de decisão.
- [ ] Fazer mudanças pequenas e coerentes com o escopo da issue.
- [ ] Manter a linguagem canônica: Cliente Sintético, Próximo Passo Responsável, Braço, Guardrail, Reason Code, Proposta Qualificada Simulada.
- [ ] Evitar dados proibidos, atributos sensíveis, aprovação, contratação, taxa ou limite real.
- [ ] Rodar testes focados durante a implementação.
- [ ] Atualizar documentação afetada pela issue, incluindo checklists em `docs/decisions/` quando a entrega concluir itens planejados.

## 5. Checklist antes de considerar a issue feita

- [ ] Rodar testes relevantes e, quando existir, a suíte completa.
- [ ] Rodar validações simples de execução documentadas, como CLI ou scripts de exemplo.
- [ ] Revisar o diff local.
- [ ] Usar revisão por agente ou revisão manual quando disponível.
- [ ] Garantir que o checklist macro em `docs/decisions/003-checklist-planejamento-mvp-lary.md` foi atualizado, se aplicável.
- [ ] Garantir que README, exemplos ou docs de uso foram atualizados quando a interface pública mudar.

## 6. Checklist de fechamento e sincronização remota

Quando a issue estiver implementada e validada:

- [ ] Fazer commit com mensagem objetiva.
- [ ] Sincronizar/publicar o trabalho no repositório remoto:

```bash
git push
```

- [ ] Comentar na issue com resumo do que foi feito, testes executados e commit relacionado.
- [ ] Fechar a issue se todos os acceptance criteria estiverem atendidos:

```bash
gh issue close <numero> --comment "..."
```

- [ ] Se algum acceptance criterion ficar pendente, não fechar a issue; comentar o estado, o bloqueio e o próximo passo.
- [ ] Confirmar o estado final:

```bash
git status --short --branch
gh issue view <numero> --json state,labels
```

## 7. Regra de ouro

Uma issue só deve ser tratada como **feita** quando estiver:

1. implementada localmente;
2. testada/validada;
3. documentada nos checklists relevantes;
4. commitada;
5. publicada no remoto;
6. comentada e, quando aplicável, fechada no GitHub.

Se qualquer etapa falhar, o agente deve explicitar o estado parcial em vez de afirmar conclusão plena.

## 8. Aplicação imediata

Esta decisão se aplica a partir da issue #2. A entrega da CLI de Próximo Passo Responsável deve atualizar o checklist macro, publicar commits no remoto e registrar o fechamento da issue no GitHub quando os critérios de aceite estiverem atendidos.
