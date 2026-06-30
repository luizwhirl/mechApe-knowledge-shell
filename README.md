# MechApe — Shell de Sistemas Especialistas com IA

Ferramenta genérica para construção de aplicações baseadas em conhecimento voltadas a diagnóstico e recomendação, desenvolvida como trabalho da disciplina **Inteligência Artificial (2026.1)**, ministrada pelo Prof. Evandro Costa.

O projeto resolve as três questões da Lista 1 de Exercícios:

| Questão | Conteúdo | Pasta |
|---|---|---|
| 1 | Shell de sistema especialista (editor de base, motor de inferência, explicação, interface) | [`q1/`](q1/) |
| 2.1 | Sistema de perguntas e respostas estilo Akinator | [`q2/q2-1.py/`](q2/q2-1.py/) |
| 2.3 | Sistema de recomendação baseado em ontologia OWL | [`q2/q2-2.py/`](q2/q2-2.py/) |
| 3 | Agente baseado em LLM (padrão ReAct) | [`q3/`](q3/) |

## Equipe

| # | Responsável | Área principal |
|---|-------------|---------------|
| P1 | [Manu](https://github.com/Manu-Vii) | Motor de inferência e arquitetura geral |
| P2 | [Indias](https://github.com/luizwhirl) | Base de conhecimento e editor de regras |
| P3 | [João](https://github.com/BrandaoJatoba) | Mecanismo de explicação e interface com o usuário |
| P4 | [Lucas](https://github.com/lucasqtl) | Questão 2.1 — Akinator |
| P5 | [Rayssa](https://github.com/rayssar9i) | Questão 2.3 — Ontologias + Questão 3 |

---

## Estrutura do Repositório

```
.
├── mechape_hub.py              # Hub principal — menu para escolher qual questão executar
├── q1/                         # Questão 1 — Shell de sistema especialista
│   ├── editor_base_conhecimento.py   # Módulo 1: Editor da Base de Conhecimento (CRUD)
│   ├── motor_inferencia.py           # Módulo 3: Motor de Inferência (forward/backward/híbrido)
│   ├── explicador.py                 # Módulo 4: Mecanismo de Explicação ("Por quê?" / "Como?")
│   ├── interface.py                  # Módulo 5: Interface com o usuário (CLI retrô)
│   ├── docs/                         # Documentação da base de conhecimento + diagrama de arquitetura
│   └── tests/                        # Base de conhecimento de demonstração + testes automatizados
├── q2/
│   ├── q2-1.py/                # Questão 2.1 — Akinator (motor + interface + base de personagens)
│   └── q2-2.py/                # Questão 2.3 — Recomendação por ontologia OWL (Owlready2 + HermiT)
├── q3/
│   └── agente_llm.py           # Questão 3 — Agente ReAct com ferramentas (calculadora, data/hora, etc.)
├── requeriments.txt            # Dependências Python
├── run.sh / run.bat            # Atalhos para iniciar o hub (Linux/macOS e Windows)
├── Makefile                    # Atalhos make run / make test-q1 / make test-q2
└── Dockerfile                  # Imagem para rodar o hub em container
```

---

## Requisitos

- Python 3.10 ou superior
- Dependências listadas em `requeriments.txt`:
  - `jsonschema` — validação da base de conhecimento (Questão 1)
  - `owlready2` — ontologia OWL e reasoner HermiT (Questão 2.3)
- Opcional, apenas para a Questão 3: [Ollama](https://ollama.com/download) instalado localmente com o modelo `llama3.2` (`ollama pull llama3.2`). Se o Ollama não estiver disponível, o agente da Questão 3 cai automaticamente em um **modo simulado**, que demonstra a mesma arquitetura sem precisar de LLM.

### Instalação

```bash
git clone https://github.com/luizwhirl/mechApe-knowledge-shell.git
cd mechApe-knowledge-shell
pip install -r requeriments.txt
```

---

## Como Executar

### Opção 1 — Hub principal (recomendado)

O hub abre um menu único de onde dá para acessar as três questões:

```bash
python mechape_hub.py
```

```
1. EXECUTAR QUESTÃO 1 (Motor de Inferência)
2. EXECUTAR QUESTÃO 2 (Sistemas A e B)
3. EXECUTAR QUESTÃO 3 (Agente LLM)
4. EXIBIR CRÉDITOS DA EQUIPE
0. DESLIGAR TERMINAL (SAIR)
```

Atalhos equivalentes: `bash run.sh` (Linux/macOS), `run.bat` (Windows) ou `make run`.

> O hub abre cada questão em uma nova janela de terminal redimensionada (120x35). Caso o terminal nativo não abra no seu sistema, execute os scripts de cada questão diretamente, como descrito abaixo.

### Opção 2 — Executar cada questão individualmente

**Questão 1 — Shell de sistema especialista:**
```bash
python q1/interface.py
```

**Questão 2.1 — Akinator:**
```bash
python q2/q2-1.py/interface.py
```

**Questão 2.3 — Recomendação por ontologia:**
```bash
python q2/q2-2.py/recomendacao.py
```

**Questão 3 — Agente LLM:**
```bash
python q3/agente_llm.py
```

### Opção 3 — Docker

```bash
docker build -t mechape .
docker run -it mechape
```

---

## Questão 1 — Shell de Sistema Especialista

Domínio da aplicação demonstrativa: **suporte técnico / diagnóstico de erros e desempenho em jogos de PC**, com 21 regras, 33 fatos (31 de entrada + 2 inferidos) e 7 hipóteses de diagnóstico.

### Arquitetura

| Módulo | Arquivo | Responsável |
|---|---|---|
| Editor da Base de Conhecimento | `q1/editor_base_conhecimento.py` | P2 |
| Base de Conhecimento (JSON + schema) | `q1/tests/knowledge_base.json` | P2 |
| Motor de Inferência | `q1/motor_inferencia.py` | P1 |
| Mecanismo de Explicação | `q1/explicador.py` | P3 |
| Interface com o Usuário | `q1/interface.py` | P3 |

As regras seguem o formato `SE condição1 E condição2 ENTÃO conclusão`, e a base de conhecimento é totalmente externa ao código-fonte (arquivo `knowledge_base.json`), podendo ser substituída por qualquer outra base que respeite o schema do projeto (`q1/tests/knowledge_base.schema.json`).

O motor de inferência implementa encadeamento para frente (forward chaining), encadeamento para trás (backward chaining) e uma estratégia híbrida, conforme exigido pelo enunciado.

### Usando a interface interativa

```bash
python q1/interface.py
```

A interface oferece dois modos:

1. **Nova Consulta Diagnóstica** — o motor híbrido faz perguntas ao usuário (responda `S`, `N` ou `?`). Digitar `?` ou `por que` a qualquer momento explica por que aquela pergunta está sendo feita. Ao final, se um diagnóstico for confirmado, é possível pedir `Como?` para ver a cadeia de regras que levou à conclusão.
2. **Modo Desenvolvedor** — menu para listar fatos/regras, cadastrar, editar ou remover regras, com persistência direta no `knowledge_base.json`.

### Editando a base de conhecimento via linha de comando

O script `q1/editor_base_conhecimento.py` também pode ser usado diretamente, sem abrir o menu interativo. A base padrão é `q1/tests/knowledge_base.json`; use `--base <caminho>` para apontar para outra base.

```bash
# Listar fatos ou regras
python q1/editor_base_conhecimento.py list facts
python q1/editor_base_conhecimento.py list rules

# Validar a integridade referencial da base (regras -> fatos -> hipóteses)
python q1/editor_base_conhecimento.py validate

# Abrir o menu interativo isolado do editor
python q1/editor_base_conhecimento.py interactive

# Cadastrar um fato
python q1/editor_base_conhecimento.py add-fact \
  --attribute jogo_fecha_em_menu \
  --label "O jogo fecha ao entrar no menu principal" \
  --question "O jogo fecha ao entrar no menu principal?" \
  --category desempenho_execucao \
  --source user_input

# Cadastrar uma regra
python q1/editor_base_conhecimento.py add-rule \
  --label "Crash no menu + overlay Steam -> conflito de overlay" \
  --conditions F32,F24 \
  --conclusion-type hypothesis \
  --conclusion-id H1 \
  --priority 2 \
  --why "A regra verifica se o crash no menu está relacionado a overlay ativo." \
  --how "A conclusão foi obtida combinando o fato F32 com o overlay Steam F24."

# Editar uma regra existente
python q1/editor_base_conhecimento.py edit-rule R22 \
  --conditions F01,F23 \
  --priority 4 \
  --label "Crash + Discord -> conflito de overlay"

# Remover uma regra
python q1/editor_base_conhecimento.py remove-rule R22

# Usar outra base JSON customizada
python q1/editor_base_conhecimento.py --base caminho/para/outra_base.json list rules
```

*Se `--id` for omitido em `add-fact`/`add-rule`, o sistema gera automaticamente o próximo identificador livre (ex: `F32`, `R23`).*

### Testes automatizados

```bash
# Validação de schema + relatório de cobertura da base de conhecimento
python q1/tests/validate.py

# Testes de unidade
python -m unittest q1.tests.test_editor_base_conhecimento
python -m unittest q1.tests.test_explicador
python -m unittest q1.tests.test_interface
```

Documentação adicional da base de conhecimento (descrição de fatos, regras e hipóteses) e o diagrama de arquitetura estão em [`q1/docs/`](q1/docs/).

---

## Questão 2.1 — Akinator

Sistema que adivinha um personagem fictício (filmes, séries, cartoons, animes e jogos) por meio de perguntas binárias, reduzindo o conjunto de hipóteses a cada resposta.

- Base com 31 personagens e 26 atributos (requisito mínimo: 20 entidades / 15 atributos), representada de forma declarativa em [`knowledge_base.json`](q2/q2-1.py/knowledge_base.json), editável sem alterar o código-fonte.
- Inferência por atualização bayesiana de crenças, com escolha da próxima pergunta pelo maior ganho de informação (entropia de Shannon).
- Aceita respostas `Sim` / `Não` / `Não sei`, com tolerância a respostas subjetivas (sem eliminação brusca de hipóteses) e palpite final por dominância relativa.

```bash
# Jogar
python q2/q2-1.py/interface.py

# Rodar os testes automatizados (15 cenários, ~7 perguntas por personagem em média)
python q2/q2-1.py/tests/test_akinator.py
```

---

## Questão 2.3 — Recomendação por Ontologias

Sistema de recomendação de filmes e séries baseado em uma ontologia OWL 2.0, construída em código com **Owlready2** e raciocinada pelo reasoner **HermiT**.

- 16 classes, com hierarquia de especialização/generalização (`Obra` → `Filme`/`Série`).
- 16 propriedades (8 de objeto + 8 de dados).
- 12 indivíduos (obras), além de gêneros, diretores e plataformas de streaming.
- O reasoner HermiT realiza classificação automática de indivíduos, descoberta de relações implícitas e verificação de consistência da ontologia, usados como base para as recomendações.

```bash
python q2/q2-2.py/recomendacao.py
```

A ontologia gerada é salva em [`recomendacao_filmes.owl`](q2/q2-2.py/recomendacao_filmes.owl) e pode ser aberta no [Protégé](https://protege.stanford.edu/) para inspeção visual.

---

## Questão 3 — Agente Baseado em LLM

Agente de tarefas no padrão **ReAct** (Reasoning + Acting): recebe um objetivo em linguagem natural, planeja os passos, decide quais ferramentas usar, executa cada uma, observa o resultado e itera até concluir, sintetizando uma resposta final.

Ferramentas disponíveis ao agente: calculadora, data/hora atual e conversor de moedas (taxas fixas, offline, para fins didáticos).

O LLM utilizado é o **Ollama** (local e gratuito, sem necessidade de chave de API):

```bash
# 1. Baixe o Ollama em https://ollama.com/download
# 2. No terminal:
ollama pull llama3.2
# 3. Deixe o Ollama em execução e rode o agente:
python q3/agente_llm.py
```

Se o Ollama não estiver instalado ou em execução, o agente detecta isso automaticamente e cai em um **modo simulado**, que demonstra o mesmo ciclo Pensamento → Ação → Observação sem depender de um LLM externo.

---

> [!NOTE]
Os sistemas de diagnóstico desenvolvidos neste projeto têm finalidade exclusivamente educacional e acadêmica, e não devem ser usados como ferramentas reais de diagnóstico técnico ou médico.
