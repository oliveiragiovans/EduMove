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

## BR-030

Os dados de uma escola devem ser normalizados antes da persistência:

- CNPJ armazenado somente com 14 dígitos, quando informado;
- e-mail armazenado em letras minúsculas;
- sigla do estado armazenada em letras maiúsculas;
- campos de texto sem espaços excedentes.

## BR-031

Uma escola deve ser desativada em vez de excluída, preservando professores, turmas e
avaliações relacionados.

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

## BR-032

Toda consulta, atualização ou desativação de professor deve ser limitada à escola
informada na operação.

## BR-033

Nome e e-mail devem ser normalizados antes da persistência. Senhas em texto puro não
podem ser recebidas pelo CRUD de professores; somente hashes gerados pelo futuro
serviço de autenticação poderão ser armazenados.

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

## BR-034

Quando uma turma possuir professor responsável, esse professor deve estar ativo e
pertencer à mesma escola da turma.

## BR-035

Toda consulta, atualização ou desativação de turma deve ser limitada a uma escola
ativa. Série e ano letivo devem ser números inteiros válidos, a seção deve possuir
uma letra e os valores de nível de ensino e turno devem pertencer aos catálogos
definidos pelo sistema.

---

# 4. Students

## BR-013

Todo aluno pertence a apenas uma turma ativa.

## BR-014

Um aluno pode trocar de turma durante sua vida escolar.

## BR-015

O histórico de avaliações do aluno deve ser preservado mesmo após mudança de turma.

## BR-036

Nome e matrícula do aluno devem ser normalizados antes da persistência. A matrícula
é opcional, mas, quando informada, deve ser única. A data de nascimento não pode
estar no futuro.

## BR-037

O cadastro e a transferência de um aluno devem usar uma turma ativa pertencente à
mesma escola informada na operação. Uma turma com alunos ativos não pode ser
desativada até que esses alunos sejam transferidos ou desativados.

## BR-038

Toda consulta, busca, atualização ou desativação de aluno deve ser limitada a uma
escola ativa. Turmas inativas permanecem consultáveis para preservar o histórico.

---

# 5. Assessments

## BR-016

Toda avaliação pertence a um único aluno.

## BR-017

Uma avaliação pode possuir diversos testes motores.

## BR-018

Uma avaliação nunca deve ser excluída automaticamente.

## BR-039

Uma nova avaliação exige escola, aluno, professor e turma ativos. O aluno e o
professor devem pertencer à escola informada, e a turma da avaliação deve ser
capturada automaticamente a partir da turma atual do aluno.

## BR-040

A data da avaliação não pode estar no futuro nem ser anterior ao nascimento do
aluno. Peso e altura são opcionais, mas, quando informados, devem ser positivos e
normalizados com duas casas decimais.

## BR-041

Aluno, turma e professor identificam o contexto histórico da avaliação. O CRUD
permite corrigir o professor, a data, as medidas e as observações, mas não permite
trocar o aluno ou a turma de uma avaliação existente.

## BR-042

Consultas e alterações de avaliações devem ser limitadas a uma escola ativa.
Avaliações históricas continuam consultáveis após a desativação do aluno, professor
ou turma relacionados.

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

## BR-043

As tentativas de um teste motor devem ser enviadas como um conjunto completo. Testes
com protocolo fixo exigem a quantidade configurada, enquanto protocolos variáveis
devem respeitar seus limites mínimo e máximo.

## BR-044

Resultados binários aceitam somente acerto ou erro, persistidos numericamente como
1 ou 0. O resumo deve preservar e exibir tanto a quantidade de acertos quanto o
total de tentativas ativas.

## BR-045

O resultado resumido de um teste deve ser calculado pelo método configurado em seu
protocolo: máximo, mínimo, soma ou média. O valor agregado é derivado e não deve ser
duplicado como dado de origem.

## BR-046

O equilíbrio unipodal aceita no máximo 30 segundos por tentativa. Correções devem
reutilizar os registros existentes, e tentativas removidas do conjunto devem ser
desativadas em vez de excluídas.

## BR-047

As observações posturais possuem finalidade de triagem pedagógica. Rótulos,
descrições e mensagens da interface não devem apresentar as opções como diagnóstico
clínico.

## BR-048

Cada avaliação pode possuir somente uma observação postural ativa por combinação de
região corporal e posição de visualização. Ao selecionar outra opção no mesmo
contexto, a escolha anterior deve ser desativada, e não excluída.

## BR-049

Observações de posições diferentes são independentes. Uma escolha frontal não deve
substituir uma escolha lateral da mesma região corporal.

## BR-050

Somente avaliações e opções posturais ativas podem receber novas escolhas.
Avaliações históricas inativas continuam disponíveis para consulta.

## BR-051

Cada opção do catálogo pode indicar uma imagem de referência armazenada como ativo
da aplicação. O banco deve guardar apenas o caminho e os metadados, nunca o conteúdo
binário da imagem.

## BR-052

Observações livres associadas a uma escolha postural são opcionais, devem ter os
espaços externos removidos e podem conter no máximo 255 caracteres.

## BR-053

Senhas novas devem possuir entre 15 e 128 caracteres. Espaços, caracteres Unicode e
frases-senha são permitidos, sem exigência artificial de letras maiúsculas, números
ou símbolos.

## BR-054

Senhas nunca devem ser persistidas em texto simples. O backend deve gerar um hash
Argon2id com sal aleatório antes de criar ou atualizar um professor.

## BR-055

Somente professores ativos vinculados a escolas ativas podem autenticar.

## BR-056

Falhas por e-mail inexistente, senha incorreta, professor inativo ou escola inativa
devem produzir a mesma mensagem genérica, sem revelar quais contas estão
cadastradas.

## BR-057

Uma troca de senha iniciada pelo professor deve confirmar a senha atual antes de
persistir o novo hash.

## BR-058

Após um login válido, hashes criados com parâmetros Argon2id antigos devem ser
atualizados automaticamente quando a configuração de segurança vigente exigir.

## BR-059

A sessão do Streamlit deve armazenar somente o identificador do professor, o
identificador da escola, nome, e-mail e perfil. Senha e hash não podem fazer parte
do estado da interface.

## BR-060

Ao sair, a identidade autenticada deve ser removida da sessão e a aplicação deve
retornar ao formulário de login.

## BR-061

Sem uma identidade autenticada válida, a aplicação deve renderizar somente a tela
de login e não deve exibir a navegação ou o conteúdo interno.

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
