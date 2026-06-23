# MachApe — Shell de Sistemas Especialistas com IA

> Ferramenta genérica para construção de aplicações baseadas em conhecimento voltadas a diagnóstico e recomendação, desenvolvida como trabalho da disciplina **Inteligência Artificial (2026.1)** — Prof. Evandro Costa.

---

## Equipe e Distribuição de Tarefas

| # | Responsável | Área principal |
|---|-------------|---------------|
| P1 | `[Manu](https://github.com/Manu-Vii)` | Motor de inferência & arquitetura geral |
| P2 | `[Indias](https://github.com/luizwhirl)` | Base de conhecimento & editor de regras |
| P3 | `[João](https://github.com/BrandaoJatoba)` | Mecanismo de explicação & interface com o usuário |
| P4 | `[Lucas](https://github.com/lucasqtl)` | Questão 2 — Sistema A (a definir pelo grupo) |
| P5 | `[Rayssa](https://github.com/rayssar9i)` | Questão 2 — Sistema B + Questão 3 (LLM) |

---

## Checklist Geral do Projeto

### Questão 1 — Shell de Sistema Especialista (0–5 pts)

#### Módulo 1 — Editor da Base de Conhecimento `P2`
- [ ] Cadastro de fatos
- [ ] Cadastro de regras no formato `SE condição1 E condição2 ENTÃO conclusão`
- [ ] Edição de regras existentes
- [ ] Remoção de regras
- [ ] Persistência da base em arquivo (JSON / YAML / banco de dados)
- [ ] Carregamento da base a partir de arquivo externo (sem alterar código-fonte)

#### Módulo 2 — Base de Conhecimento `P2`
- [ ] Estrutura para armazenar fatos iniciais
- [ ] Estrutura para armazenar fatos inferidos
- [ ] Estrutura para armazenar regras de produção
- [ ] Estrutura para armazenar hipóteses / objetivos de diagnóstico

#### Módulo 3 — Motor de Inferência `P1`
- [ ] Encadeamento para frente (Forward Chaining)
- [ ] Encadeamento para trás (Backward Chaining)
- [ ] Estratégia híbrida (Forward + Backward)
- [ ] Identificação de regras disparáveis (agenda de conflitos)
- [ ] Resolução de objetivos de diagnóstico
- [ ] Solicitação de informações adicionais ao usuário quando necessário
- [ ] Integração com os módulos de base e explicação

#### Módulo 4 — Mecanismo de Explicação `P3`
- [ ] Resposta à pergunta **"Por quê?"** — justificar por que determinada pergunta foi feita
- [ ] Resposta à pergunta **"Como?"** — explicar como uma conclusão foi obtida
- [ ] Rastreamento das regras ativadas durante a inferência
- [ ] Exibição do encadeamento de regras que levou ao diagnóstico

#### Módulo 5 — Interface com o Usuário `P3`
- [ ] Apresentação das perguntas ao usuário durante a consulta
- [ ] Coleta de respostas do usuário
- [ ] Exibição do diagnóstico final
- [ ] Exibição das explicações (Por quê / Como)
- [ ] Escolha do tipo de interface: `[ ] CLI` `[ ] GUI` `[ ] Web`

#### Extensão — Integração com LLM `P5`
- [ ] Interpretação de perguntas em linguagem natural
- [ ] Conversão de respostas livres em fatos estruturados
- [ ] Geração de explicações mais naturais via LLM
- [ ] Auxílio na construção da base de conhecimento via LLM
- [ ] **Garantir que o motor de regras continua sendo o responsável pela inferência** (LLM não substitui)

#### Aplicação Demonstrativa `P1` `P2` `P3`
- [ ] Escolha do domínio: `[ ] Diagnóstico médico` `[ ] Suporte técnico` `[ ] Veículos` `[ ] Educacional` `[ ] Agrícola`
- [ ] Base com **pelo menos 20 regras**
- [ ] Base com **pelo menos 30 fatos possíveis**
- [ ] Base com **pelo menos 5 hipóteses / diagnósticos distintos**
- [ ] Demonstração de pelo menos 3 consultas diferentes

---

### Questão 2 — Escolher 2 dos 4 sistemas abaixo (0–3 pts)

> O grupo deve escolher 2 itens. Marque os escolhidos:

#### 2.1 — Sistema Akinator `P4` ou `P5`
- [ ] **Escolhido pelo grupo**
- [ ] Base com **pelo menos 20 entidades** a identificar
- [ ] **Pelo menos 15 atributos / características**
- [ ] Representação explícita do conhecimento
- [ ] Mecanismo de inferência para eliminar hipóteses (árvore de decisão, regras, Bayes…)
- [ ] Perguntas sequenciais com respostas Sim / Não / Não sei
- [ ] Exibição da hipótese mais provável a cada rodada
- [ ] Encerramento quando identificar a solução ou esgotar hipóteses
- [ ] Experimentos com múltiplos usuários documentados
- [ ] Relatório: nº médio de perguntas, taxa de acerto, casos de falha

#### 2.2 — Diagnóstico Médico com Redes Bayesianas `P4` ou `P5`
- [ ] **Escolhido pelo grupo**
- [ ] Rede com **pelo menos 1 doença principal**
- [ ] **Mínimo de 5 variáveis** na rede
- [ ] **Pelo menos 3 sintomas observáveis**
- [ ] Relações de dependência justificadas entre os nós
- [ ] Tabelas de Probabilidades Condicionais (CPTs) definidas
- [ ] Modelagem gráfica da rede apresentada
- [ ] Implementação em ferramenta adequada (Netica / GeNIe / pgmpy / PyMC…)
- [ ] Experimento 1: inferência a partir de sintomas observados
- [ ] Experimento 2: atualização do diagnóstico com novas evidências
- [ ] Experimento 3: comparação entre conjuntos de evidências distintos
- [ ] Relatório: CPTs, exemplos de inferência, discussão de resultados

#### 2.3 — Sistema de Recomendação com Ontologias `P4` ou `P5`
- [ ] **Escolhido pelo grupo**
- [ ] Ontologia OWL 2.0 com **pelo menos 10 classes**
- [ ] **Pelo menos 15 propriedades** (objeto e/ou atributo)
- [ ] Hierarquia de classes (especialização / generalização)
- [ ] Restrições e axiomas definidos
- [ ] Indivíduos / instâncias suficientes para demonstração
- [ ] Consultas semânticas implementadas
- [ ] Reasoner utilizado (HermiT / Pellet / FaCT++)
- [ ] Demonstração de classificação automática de indivíduos
- [ ] Demonstração de descoberta de relacionamentos implícitos
- [ ] Verificação de consistência da ontologia
- [ ] Relatório: classes, propriedades, consultas, análise crítica

#### 2.4 — Diagnóstico Médico com Raciocínio Baseado em Casos (CBR) `P4` ou `P5`
- [ ] **Escolhido pelo grupo**
- [ ] Base com **pelo menos 15 casos médicos** fictícios
- [ ] **Pelo menos 5 tipos diferentes de doenças**
- [ ] Implementação da etapa **Retrieve** (recuperar casos similares)
- [ ] Implementação da etapa **Reuse** (propor diagnóstico com base nos casos)
- [ ] Implementação da etapa **Revise** (validar / corrigir diagnóstico)
- [ ] Implementação da etapa **Retain** (incluir novos casos na base)
- [ ] Mecanismo de cálculo de similaridade entre casos implementado
- [ ] Exibição dos casos mais similares encontrados
- [ ] Apresentação do diagnóstico e tratamento sugerido
- [ ] Relatório: representação dos casos, método de similaridade, análise

---

### Questão 3 — Aplicação com Agentes Baseados em LLM (0–2 pts) `P5`

- [ ] Definição do tipo de agente e do domínio de aplicação
- [ ] Implementação do agente com LLM
- [ ] Demonstração de pelo menos um fluxo de interação completo
- [ ] Integração com a Q1 (opcional, mas recomendada como extensão avançada)
- [ ] Documentação do funcionamento do agente

---

## Entregáveis

### Questão 1
- [ ] Código-fonte da shell
- [ ] Arquivo da base de conhecimento demonstrativa
- [ ] Relatório técnico contendo:
  - [ ] Arquitetura implementada
  - [ ] Estrutura de representação do conhecimento
  - [ ] Estratégia de inferência utilizada
  - [ ] Implementação do mecanismo de explicação
  - [ ] Exemplos de consultas realizadas
  - [ ] Limitações e possíveis melhorias
- [ ] Vídeo ou apresentação demonstrando o funcionamento

### Questão 2
- [ ] Código-fonte do sistema A
- [ ] Código-fonte do sistema B
- [ ] Base de conhecimento de cada sistema
- [ ] Relatório técnico de cada sistema
- [ ] Apresentação ou demonstração de cada sistema

### Questão 3
- [ ] Código-fonte da aplicação com agente LLM
- [ ] Relatório técnico

---

## 📅 Pontuação

| Questão | Valor |
|---------|-------|
| Q1 — Shell especialista | 0 – 5 pts |
| Q2 — 2 sistemas (escolha) | 0 – 3 pts |
| Q3 — Agente LLM | 0 – 2 pts |
| **Total** | **10 pts** |

---

> [!note] 
> Os sistemas de diagnóstico médico desenvolvidos neste projeto têm finalidade exclusivamente educacional e não devem ser utilizados como ferramentas reais de diagnóstico.
