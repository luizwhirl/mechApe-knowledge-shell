# MechApe - Shell de Sistemas Especialistas com IA

Ferramenta genérica para construção de aplicações baseadas em conhecimento voltadas a diagnóstico e recomendação, desenvolvida como trabalho da disciplina **Inteligência Artificial (2026.1)**.

## Equipe e Distribuição de Tarefas

| # | Responsável | Área principal |
|---|-------------|---------------|
| P1 | [Manu](https://github.com/Manu-Vii) | Motor de inferência e arquitetura geral |
| P2 | [Indias](https://github.com/luizwhirl) | Base de conhecimento e editor de regras |
| P3 | [João](https://github.com/BrandaoJatoba) | Mecanismo de explicação e interface com o usuário |
| P4 | [Lucas](https://github.com/lucasqtl) | Questão 2 - Sistema A |
| P5 | [Rayssa](https://github.com/rayssar9i) | Questão 2 - Sistema B + Questão 3 |

## Estado Atual

### Questão 1 - Shell de Sistema Especialista

#### Módulo 1 - Editor da Base de Conhecimento `P2`
- ☑️ Cadastro de fatos
- ☑️ Cadastro de regras no formato `SE condição1 E condição2 ENTÃO conclusão`
- ☑️ Edição de regras existentes
- ☑️ Remoção de regras
- ☑️ Persistência da base em arquivo JSON
- ☑️ Carregamento da base a partir de arquivo externo sem alterar código-fonte

#### Módulo 2 - Base de Conhecimento `P2`
- ☑️ Estrutura para armazenar fatos iniciais
- ☑️ Estrutura para armazenar fatos inferidos
- ☑️ Estrutura para armazenar regras de produção
- ☑️ Estrutura para armazenar hipóteses / objetivos de diagnóstico

#### Módulo 3 - Motor de Inferência `P1`
- ☑️ Encadeamento para frente (Forward Chaining)
- ☑️ Encadeamento para trás (Backward Chaining)
- ☑️ Estratégia híbrida (Forward + Backward)
- ☑️ Identificação de regras disparáveis
- ☑️ Resolução de objetivos de diagnóstico
- ☑️ Solicitação de informações adicionais ao usuário quando necessário
- ☑️ Integração com a base de conhecimento

#### Módulo 4 - Mecanismo de Explicação `P3`
- ☑️ Resposta à pergunta **"Por quê?"** (Justificativa de contexto da pergunta atual)
- ☑️ Resposta à pergunta **"Como?"** (Reconstrução profunda da árvore causal)
- ☑️ Rastreamento cronológico de regras ativadas durante a inferência
- ☑️ Exibição do encadeamento lógico completo e recursivo que levou ao diagnóstico

#### Módulo 5 - Interface com o Usuário `P3`
- ☑️ Apresentação interativa de perguntas ao usuário durante a consulta
- ☑️ Coleta de respostas (`S` / `N` / `?` para interrogar o módulo explicativo)
- ☑️ Exibição detalhada do diagnóstico final com descrição e recomendação técnica
- ☑️ Integração do módulo de edição (`editor.py`) diretamente nos menus da interface
- ☑️ Interface CLI com estética Retrô (Terminal fósforo verde estilo PC dos anos 80)
- ☑️ Inicialização automática de terminal nativo otimizado e redimensionado para o operador

#### Aplicação Demonstrativa
- ☑️ Domínio escolhido: suporte técnico / diagnóstico de erros e performance em jogos de PC
- ☑️ Base com pelo menos 20 regras (21 regras integradas)
- ☑️ Base com pelo menos 30 fatos possíveis (31 fatos de entrada + 2 inferidos)
- ☑️ Base com pelo menos 5 hipóteses distintas (7 hipóteses/diagnósticos mapeados)
- [ ] Demonstração de pelo menos 3 consultas diferentes

### Questão 2 - Sistema A: Identificador estilo Akinator (2.1) `P4`
Sistema baseado em conhecimento que adivinha um personagem fictício (filmes, séries, cartoons, animes e jogos) por meio de perguntas binárias, reduzindo as hipóteses a cada resposta.

- ☑️ Base com 31 personagens e 26 atributos (requisito: ≥ 20 entidades e ≥ 15 atributos)
- ☑️ Conhecimento explícito e declarativo em JSON, editável sem alterar o código-fonte
- ☑️ Inferência por atualização bayesiana de crenças + escolha da pergunta por maior ganho de informação (entropia de Shannon)
- ☑️ Respostas `Sim` / `Não` / `Não Sei` e exibição da hipótese atual mais provável a cada rodada
- ☑️ Tolerância a respostas subjetivas (sem eliminação brusca) e palpite por dominância relativa
- ☑️ 15 testes automatizados — 100% de acerto, média de ~7 perguntas por personagem

Implementado em [`q2/q2-1.py/`](q2/q2-1.py/): `akinator.py` (motor de inferência), `interface.py` (CLI retrô) e `knowledge_base.json` (base). Para jogar e para rodar os testes, a partir da raiz do projeto:

python q2/q2-1.py/interface.py
python q2/q2-1.py/tests/test_akinator.py

> O Sistema B da Questão 2 (recomendação por ontologias, `P5`) fica em [`q2/q2-2.py/`](q2/q2-2.py/).

---

## 🕹️ Como Executar o Programa Principal

A interface unificada do usuário (`interface.py`) encapsula tanto o **Módulo de Diagnóstico Interativo** quanto o **Módulo de Edição de Regras (Modo Desenvolvedor)**, fornecendo uma experiência visual contida e estilizada.

Para iniciar o console, execute a partir da raiz do projeto:

python q1/interface.py

### Funcionalidades Integradas na Interface:
1. **Nova Consulta Diagnóstica:** Executa o motor híbrido. O utilizador responde às perguntas e pode digitar `?` ou `por que` a qualquer momento para que o sistema explique a hipótese que está a tentar avaliar naquele instante. No final, se um diagnóstico for confirmado, é possível inspecionar toda a cadeia causal cronológica através do comando **Como?**.
2. **Modo Desenvolvedor (Menu de Edição):** Permite listar os fatos e a matriz de regras, cadastrar novos sintomas, injetar novas regras logicamente validadas na árvore, modificar dados existentes ou remover regras obsoletas, com persistência direta e segura no ficheiro `knowledge_base.json`.

---

## 🛠️ Gestão Avançada da Base de Conhecimento (CLI Direta)

Se preferir manipular a base de dados em lote ou injetar dados programaticamente sem utilizar a interface interativa do terminal, o script `q1/editor.py` expõe os seus comandos diretamente para o terminal do sistema operacional:

### Listar fatos e regras

python q1/editor.py list-facts
python q1/editor.py list-rules

### Abrir menu interativo isolado do editor

python q1/editor.py interactive

### Cadastrar fato via linha de comando

python q1/editor.py add-fact \
  --attribute jogo_fecha_em_menu \
  --label "O jogo fecha ao entrar no menu principal" \
  --question "O jogo fecha ao entrar no menu principal?" \
  --category desempenho_execucao \
  --source user_input

*Se o parâmetro `--id` for omitido, o sistema gera o próximo identificador livre de forma sequencial (ex: F32 ou F_INF_03).*

### Cadastrar regra via linha de comando

python q1/editor.py add-rule \
  --label "Crash no menu + overlay Steam -> conflito de overlay" \
  --conditions F32,F24 \
  --conclusion-type hypothesis \
  --conclusion-id H1 \
  --priority 2 \
  --explanation-why "A regra verifica se o crash no menu está relacionado a overlay ativo." \
  --explanation-how "A conclusão foi obtida combinando o fato F32 com o overlay Steam F24."

### Editar regra existente

python q1/editor.py edit-rule R22 \
  --conditions F01,F23 \
  --priority 4 \
  --label "Crash + Discord -> conflito de overlay"

### Remover regra

python q1/editor.py remove-rule R22

### Utilizar outra base JSON customizada
Qualquer outra base de conhecimento que respeite o JSON Schema do projeto pode ser injetada e reutilizada pela shell:

python q1/editor.py --kb caminho/para/outra_base.json list-rules

---

## 🧪 Validação e Testes Automatizados

O ecossistema conta com uma suite completa de testes de integridade para garantir a robustez das inferências e das modificações feitas em modo de desenvolvimento.

### Validação do Schema e Relatório de Sanidade
Verifica se as correlações referenciais estão íntegras e se as metas de cobertura da disciplina foram cumpridas:

cd q1/tests
python validate.py

### Testes de Unidade do Editor

python -m unittest q1.tests.test_editor

### Testes de Unidade do Mecanismo de Explicação e Encadeamento Recursivo

python -m unittest q1.tests.test_explicador

### Testes de Integração da Interface e Teclado Simulado

python -m unittest q1.tests.test_interface

---

## Entregáveis Pendentes

- Relatório técnico completo da Questão 1.
- Demonstração de pelo menos 3 consultas diferentes.
- Questão 2 - Sistema B e Questão 3 conforme divisão de tarefas do grupo.

> ⚠️ Aviso: Os sistemas de diagnóstico desenvolvidos neste projeto têm finalidade exclusivamente educacional e académica, não devendo ser usados como ferramentas reais de diagnóstico técnico.
