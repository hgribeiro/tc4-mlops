---
status: accepted
---

# AWS como arquitetura executável do MVP

Embora a direção anterior descrevesse Azure como arquitetura-alvo para Lary, o MVP será desenvolvido localmente com LocalStack e implantado temporariamente na AWS por Terraform, porque essa combinação reduz custo, permite validar a infraestrutura antes de criar a conta cloud e atende melhor ao ciclo efêmero da demonstração. A arquitetura executável usará apresentação HTML estática, API de Demonstração serverless e auditoria minimizada; Azure permanecerá apenas como equivalência corporativa conceitual, sem alegação de implantação, validação ou arquitetura multicloud.

## Consequências

A documentação e a apresentação devem distinguir explicitamente a AWS validada da equivalência Azure não implantada. O ambiente AWS `demo` será criado sob demanda e destruído após o uso; somente o bootstrap de estado e automação permanecerá. Aprendizado online e processamento cloud de Delayed Rewards continuam fora do MVP executável.
