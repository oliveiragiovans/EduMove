# 📋 Business Rules - EduMove

## Version

Current Version: 1.0

---

# 1. Schools

## BR-001

Uma escola pode possuir vários professores.

## BR-002

Uma escola pode possuir várias turmas.

## BR-003

Uma escola é responsável pelos dados cadastrados no sistema.

## BR-004

Uma escola pode possuir apenas um administrador principal na versão 1.0.

---

# 2. Teachers

## BR-005

Todo professor deve estar vinculado a uma escola.

## BR-006

Todo professor possui um perfil de acesso.

Perfis disponíveis:

- Administrador
- Professor
- Coordenador (versão futura)

## BR-007

Um professor pode ser responsável por nenhuma, uma ou várias turmas.

## BR-008

Um professor pode ser desativado sem que suas avaliações sejam removidas.

---

# 3. Classes

## BR-009

Toda turma pertence a uma escola.

## BR-010

Uma turma pode existir sem professor responsável.

## BR-011

Cada turma deve ser única considerando:

- Escola
- Ano escolar
- Turma
- Ano letivo

## BR-012

Turmas encerradas não devem ser excluídas, apenas marcadas como inativas.

---

# 4. Students

## BR-013

Todo aluno pertence a apenas uma turma ativa.

## BR-014

Um aluno pode trocar de turma durante sua vida escolar.

## BR-015

O histórico de avaliações do aluno deve ser preservado mesmo após mudança de turma.

---

# 5. Assessments

## BR-016

Toda avaliação pertence a um único aluno.

## BR-017

Uma avaliação pode possuir diversos testes motores.

## BR-018

Uma avaliação nunca deve ser excluída automaticamente.

---

# 6. Motor Tests

## BR-019

Os testes motores são cadastrados apenas uma vez.

## BR-020

Novos protocolos poderão ser adicionados futuramente sem alterar a estrutura do banco.

---

# 7. Security

## BR-021

Professores visualizam apenas as turmas sob sua responsabilidade.

## BR-022

Administradores possuem acesso a toda a escola.

## BR-023

Coordenadores podem visualizar todas as turmas, porém possuem permissões limitadas para edição.

---

# 8. Audit

## BR-024

Todas as tabelas principais devem possuir:

- created_at
- updated_at

## BR-025

Registros importantes devem ser inativados, evitando exclusões permanentes.

---

# 9. Protocolos de Avaliação

## BR-026

Os testes de flexibilidade adaptada, salto horizontal e equilíbrio unipodal possuem
duas tentativas no MVP, com registro do melhor resultado.

## BR-027

Na recepção de bola, o professor escolhe entre 3 e 10 lançamentos. Cada lançamento
deve ser registrado individualmente como acerto ou erro, e o resultado final deve
mostrar acertos sobre o total de lançamentos.

## BR-028

O IMC deve ser calculado a partir do peso e da altura registrados na avaliação e não
armazenado como medida independente.

## BR-029

As observações posturais de ombros, coluna, joelhos e pés possuem finalidade de
triagem pedagógica e não devem ser apresentadas como diagnóstico clínico.

---

# Future Versions

## V1.1

- Histórico de turmas
- Coordenadores
- Convite de professores por e-mail

## V1.2

- Comparação entre avaliações
- Dashboard da escola
- Exportação para PDF

## V2.0

- Multi-escolas
- API pública
- Aplicativo móvel
