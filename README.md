# 🏃 EduMove

O **EduMove** é um sistema em desenvolvimento para auxiliar professores de Educação
Física no registro de avaliações antropométricas, motoras e posturais, na organização
de turmas e alunos e no acompanhamento da evolução individual ao longo do tempo.

O projeto nasceu de uma necessidade real da área educacional e também integra o
portfólio de Engenharia de Software de sua desenvolvedora.

## Objetivos

- Digitalizar avaliações realizadas no ambiente escolar.
- Centralizar informações de escolas, professores, turmas e alunos.
- Preservar o histórico de medidas e resultados.
- Apoiar o planejamento pedagógico com dados organizados.
- Aplicar boas práticas de arquitetura, banco de dados e testes.

## Escopo do MVP

A primeira versão contempla:

- cadastro de escolas, professores, turmas e alunos;
- avaliações com data, peso, altura, IMC calculado e observações;
- flexibilidade adaptada sem banco;
- salto horizontal;
- equilíbrio unipodal;
- recepção de bola com 3 a 10 lançamentos;
- histórico individual de avaliações;
- observações posturais de ombros, coluna, joelhos e pés.

As observações posturais terão finalidade de triagem pedagógica e não serão
apresentadas como diagnóstico clínico.

## Estado atual

A fundação do backend está implementada:

- configuração por variáveis de ambiente;
- conexão MySQL com SQLAlchemy;
- nove tabelas em InnoDB e onze chaves estrangeiras ativas;
- onze migrations SQL;
- modelos ORM para todas as entidades atuais;
- catálogo configurável de testes motores;
- seed do MVP com protocolos e limites de tentativas;
- CRUDs implementados para escolas, professores, turmas, alunos e avaliações;
- validação e normalização de dados escolares, docentes, das turmas e dos alunos;
- isolamento de professores por escola e administrador ativo único;
- validação do professor responsável dentro da escola da turma;
- busca de alunos por nome e turma, com transferência segura entre turmas;
- bloqueio da desativação de turmas que ainda possuem alunos ativos;
- avaliações com data, medidas opcionais, observações e IMC calculado;
- preservação automática da turma do aluno no momento da avaliação;
- registro e correção das tentativas dos testes motores;
- agregação automática por máximo, mínimo, soma ou média;
- recepção de bola preservada como acertos sobre o total de lançamentos;
- catálogo de 20 opções posturais para ombros, coluna, joelhos e pés;
- seleção postural por região e vista, com correção sem perda do histórico;
- quatro pranchas ilustrativas originais vinculadas ao catálogo;
- 322 testes automatizados aprovados.

Os próximos marcos são implementar autenticação e iniciar a interface Streamlit,
incluindo o formulário guiado pelas imagens posturais.

## Tecnologias

- Python
- Streamlit
- MySQL com InnoDB
- SQLAlchemy 2.0
- PyMySQL
- python-dotenv
- pytest
- Pandas
- Matplotlib / Plotly
- Git e GitHub

## Estrutura

```text
EduMove/
├── assets/
│   └── posture/
├── docs/
│   ├── database/
│   │   ├── schema/
│   │   └── seeds/
│   ├── assessment_mvp.md
│   ├── architecture.md
│   ├── business_rules.md
│   ├── database.md
│   ├── requirements.md
│   └── roadmap.md
├── src/
│   ├── business_rules/
│   ├── config/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── views/
├── tests/
│   └── models/
├── .env.example
├── app.py
├── requirements.txt
└── README.md
```

## Configuração local

1. Crie e ative um ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instale as dependências:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copie `.env.example` para `.env` e informe os dados do MySQL.

4. Para um banco novo, execute:

   - `docs/database/schema/schema.sql`;
   - `docs/database/seeds/seed.sql`.

5. Execute os testes:

   ```powershell
   python -m pytest -q
   ```

O arquivo `.env` é ignorado pelo Git e não deve ser versionado.

## Documentação

- [Escopo das avaliações do MVP](docs/assessment_mvp.md)
- [Arquitetura](docs/architecture.md)
- [Regras de negócio](docs/business_rules.md)
- [Banco de dados](docs/database.md)
- [Requisitos](docs/requirements.md)
- [Roadmap](docs/roadmap.md)

## Público-alvo

Professores de Educação Física da Educação Infantil e do Ensino Fundamental que
desejam organizar avaliações e acompanhar o desenvolvimento dos alunos de forma
digital.

## Desenvolvedora

**Giovana Luciano de Oliveira**

Graduada em Educação Física e estudante de Engenharia de Software, desenvolvendo
projetos voltados à tecnologia aplicada à educação.

## Status

🚧 Backend em desenvolvimento.
