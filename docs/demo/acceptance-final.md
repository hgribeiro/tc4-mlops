# Aceite final da demonstração (#28)

**Issue:** #28 aberta no início desta consolidação; dependência #27 confirmada fechada. **Parent #17:** permanece aberto para aceite do mantenedor; este documento não fecha nem modifica o parent.

## Decisão de arquitetura

- **AWS é a arquitetura cloud executada/validada.** O #25 foi concluído nos commits `4ef82be`, `bd1ecc1`, `7c70cb5`, `13184ec` e `3ef9926`; o #27 foi concluído no commit local `748f57d`.
- O smoke real ocorreu na conta `969212888717`, região `us-east-1`, com CloudFront, API Gateway, Lambda por ECR, S3 de auditoria e CloudWatch. As URLs históricas `https://d28gr8c30kxdfs.cloudfront.net` e `https://487n63a3vd.execute-api.us-east-1.amazonaws.com/` são evidência histórica **offline/destroyed**, não endpoints atuais.
- O teardown verificou ausência de S3 presentation/audit, ECR, Lambda, API Gateway, CloudFront/OAC, CloudWatch logs/dashboard/alarmes e role runtime. Persistem bootstrap/state, OIDC/roles/boundary e Budget.
- Azure não foi implantado nem validado. A equivalência é conceitual e não constitui multicloud. Delayed Rewards não foram provisionados: EventBridge/SQS/worker são apenas evolução futura.

## Evidências e commits anteriores

| Evidência | Commit/issue | Resultado |
| --- | --- | --- |
| Persistência auditável desacoplada | #18 `cf9014b` | 24 testes e contrato preservado |
| API de Demonstração | #19 `04b24bc` | 32 testes e smoke de container |
| Experimento oficial | #20 `f76a7bb` | 45.211 registros; seeds 11/29/47/71/97; 9 contextos; 7 Braços |
| Deck offline | #21 `8290e80` | deck, gráficos, Mermaid, notes e apêndice |
| Deck interativo | #22 `4deede3` | 3 build + 6 Playwright; contingência explícita |
| LocalStack | #23 `1736056` | ciclo completo; REST API → Lambda ZIP → S3; 38 testes |
| Bootstrap/OIDC | #24 `8d1bf1a` | validação offline; aplicação e state persistentes depois confirmados no #25 |
| Deploy AWS real | #25 `4ef82be`, `bd1ecc1`, `7c70cb5`, `13184ec`, `3ef9926` | smoke das 3 cenas × 2 políticas, auditoria e telemetria minimizadas |
| CI/deploy manual | #26 `f416687` | gates, OIDC e environment `demo`; não executou deploy |
| Teardown/custo | #27 `748f57d` local, sem push | destroy real, residue check e bundle local hash-verificado |

## Artefatos oficiais e hashes

`artifacts/official-experiment/` é a evidência derivada versionada da Golden Set/Bank Marketing completa. É **sintética, offline e não causal**, não é evidência de crédito real:

- `report.json`: `8bda63f481d0224165d146e5861e2fc91aaf4ad492b1f7544c3d4022712566de`
- `policy.json`: `ef52293e7fad6ef6460cf1b2597de3095fcaa0ecda736f955d68e3bee20156b0`
- `provenance.json`: `4c53767f181c35aa2fb086d60ef93d573691d084bf1a3545bfe3446c13a4db3d`

Golden Set: `5/5` casos oficiais. A fonte Bank Marketing é proxy público; `duration` é excluída por vazamento temporal. Não alegar causalidade, fairness de grupos protegidos ou conversão bancária.

Evidência de teardown local do #27: manifesto final `artifacts/teardown-evidence-20260812T031259Z/manifest.json`, SHA-256 `04ea840a1ca8b6b1b56851f903938716f2d2322f293b1f63c04b906bba034c1b`; o bundle anterior com decisões foi `artifacts/teardown-evidence-20260812T024210Z/manifest.json`, SHA-256 `47db2618db7f80d7085f8f695843733a6ae3a3fd6c03cb08a58367df4764bdce`. Bundles são locais e não devem ser commitados.

## Gates e revisão

- Python full suite: #27 registrou `49 passed` (1 aviso externo).
- LocalStack: ciclo start/smoke/cleanup; Terraform fmt/validate/test, 2 testes do módulo, smoke HTTP/objeto S3.
- Deck: `npm test`, build 16:9 e 6 Playwright; `npm audit` mantém 7 advisories transitivos do Mermaid (6 moderados, 1 alto).
- Terraform: fmt/validate/test de bootstrap e demo passaram; `actionlint` e `shellcheck` passaram.
- `git diff --check` e revisão de segurança/especificação foram executados.
- #26 configurou environment `demo`, porém há somente `hgribeiro` como reviewer: self-review é possível. Para governança independente, adicionar reviewer e ativar `prevent_self_review=true`.
- O workflow de teardown não foi enviado/executado no GitHub: portanto **não existe GitHub Actions Artifact**. A evidência disponível é o bundle local hash-verificado.
- A conta permaneceu em low-quota mode: Lambda `ConcurrentExecutions=10`, com pedido `57e948cf306c4d08a0deb6927b2c85fauYwF6wh6` / case `178649843100746` pendente (`CASE_OPENED`) no momento do #25. Isso não deve ser narrado como capacidade de escala validada.

## Limites canônicos

A plataforma escolhe um **Próximo Passo Responsável** entre Braços elegíveis. A saída pode iniciar uma Simulação, educar, pedir documentação, encaminhar ou usar `no_offer_now`; não é Aprovação, Contratação, taxa, limite ou proposta real. A **Proposta Qualificada Simulada** é métrica sintética e não equivale a crédito. Não usar cliente real, dados pessoais, dados sensíveis, regras comerciais privadas ou inferências causais.

## Checklist de aceite

- [x] README, arquitetura AWS e ADR distinguem AWS executada, LocalStack, contingência e Azure conceitual.
- [x] Diagrama AWS Mermaid e tabela AWS→Azure têm fonte no deck/README e declaração explícita de não validação Azure.
- [x] Delayed Rewards estão somente como evolução futura não provisionada.
- [x] Deck tem fluxo principal de até cinco minutos, speaker notes e apêndice técnico sem credenciais/e-mail.
- [x] Runbook cobre local, bootstrap, gates, deploy, smoke, apresentação, export, teardown, Budget e resíduos.
- [x] Evidências #25/#27/#23, Golden Set, hashes e riscos residuais estão referenciados.
- [x] Parent #17 deve permanecer aberto para aceite do mantenedor.

### Riscos residuais (não bloqueadores do aceite documental)

1. O artifact de teardown do GitHub ainda não existe porque o workflow não foi pushado/executado.
2. Self-review do environment GitHub não equivale a aprovação independente.
3. Advisories transitivos do Mermaid permanecem no `npm audit`.
4. A quota baixa e o pedido pendente restringiram a configuração da Lambda; não há evidência de escala.
5. Fairness real, causalidade, delayed rewards e prontidão regulada continuam fora do escopo.
