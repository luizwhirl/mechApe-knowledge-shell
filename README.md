# MechApe - Shell de Sistemas Especialistas com IA

Ferramenta genérica para construção de aplicações baseadas em conhecimento voltadas a diagnóstico e recomendação, desenvolvida como trabalho da disciplina **Inteligência Artificial (2026.1)**.

## Modulo 1 - Editor CRUD da Base de Conhecimento

O projeto agora possui um editor funcional para manter a base sem editar o JSON
manualmente, conforme o enunciado da Questao 1. O script fica em
`q1/editor_base_conhecimento.py` e permite cadastrar, editar, remover, listar e
validar fatos e regras com persistencia em arquivo JSON externo.

Abrir o menu interativo:

```bash
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json interactive
```

Exemplos de uso direto por comando:

```bash
# cadastrar fato
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json add-fact \
  --attribute uso_vram_alto \
  --label "Uso de VRAM acima do limite recomendado" \
  --question "O monitoramento mostra uso de VRAM acima de 95%?" \
  --category hardware

# cadastrar regra no formato SE ... E ... ENTAO ...
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json add-rule \
  --text "SE F02 E F25 ENTAO H1=true" \
  --label "Stuttering com overlay de GPU indica conflito de overlay" \
  --priority 2 \
  --why "Estou avaliando conflito de overlay em queda de FPS." \
  --how "A regra foi ativada por queda de FPS e overlay de GPU ativo."

# editar regra existente
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json edit-rule R03 \
  --conditions F02,F25 \
  --priority 3

# remover regra
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json remove-rule R03

# remover fato; se estiver em uso por regras, exige --force
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json remove-fact F23 --force

# validar integridade referencial da base
python q1/editor_base_conhecimento.py --base q1/tests/knowledge_base.json validate
```

Por padrao, cada alteracao cria uma copia de seguranca `.bak-AAAAMMDDHHMMSS`
antes de salvar. Para testes automatizados ou demonstracoes descartaveis, use
`--no-backup`.

---

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

Implementado em [q1/editor.py](q1/editor.py). O editor mantém a base no formato JSON validado pelo schema e permite uso por comandos ou por menu interativo.

#### Módulo 2 - Base de Conhecimento `P2`

- ☑️ Estrutura para armazenar fatos iniciais
- ☑️ Estrutura para armazenar fatos inferidos
- ☑️ Estrutura para armazenar regras de produção
- ☑️ Estrutura para armazenar hipóteses / objetivos de diagnóstico

Base demonstrativa em [q1/tests/knowledge_base.json](q1/tests/knowledge_base.json), com 31 fatos de entrada, 2 fatos inferidos, 21 regras e 7 hipóteses.

#### Módulo 3 - Motor de Inferência `P1`

- ☑️ Encadeamento para frente (Forward Chaining)
- ☑️ Encadeamento para trás (Backward Chaining)
- ☑️ Estratégia híbrida (Forward + Backward)
- ☑️ Identificação de regras disparáveis
- ☑️ Resolução de objetivos de diagnóstico
- ☑️ Solicitação de informações adicionais ao usuário quando necessário
- ☑️ Integração com a base de conhecimento

#### Módulo 4 - Mecanismo de Explicação `P3`

- [ ] Resposta à pergunta **"Por quê?"**
- [ ] Resposta à pergunta **"Como?"**
- [ ] Rastreamento das regras ativadas durante a inferência
- [ ] Exibição do encadeamento de regras que levou ao diagnóstico

#### Módulo 5 - Interface com o Usuário `P3`

- [ ] Apresentação das perguntas ao usuário durante a consulta
- [ ] Coleta de respostas do usuário
- [ ] Exibição do diagnóstico final
- [ ] Exibição das explicações
- [ ] Escolha do tipo de interface: CLI / GUI / Web

#### Aplicação Demonstrativa

- ☑️ Domínio escolhido: suporte técnico / diagnóstico de erros e performance em jogos de PC
- ☑️ Base com pelo menos 20 regras
- ☑️ Base com pelo menos 30 fatos possíveis
- ☑️ Base com pelo menos 5 hipóteses / diagnósticos distintos
- [ ] Demonstração de pelo menos 3 consultas diferentes

## Editor da Base de Conhecimento

O editor fica em `q1/editor.py` e usa por padrão `q1/tests/knowledge_base.json`.

### Abrir menu interativo

```bash
python q1/editor.py interactive
```

### Listar fatos e regras

```bash
python q1/editor.py list-facts
python q1/editor.py list-rules
```

### Cadastrar fato

```bash
python q1/editor.py add-fact \
  --attribute jogo_fecha_em_menu \
  --label "O jogo fecha ao entrar no menu principal" \
  --question "O jogo fecha ao entrar no menu principal?" \
  --category desempenho_execucao \
  --source user_input
```

Se `--id` for omitido, o editor gera o próximo ID livre (`F32`, `F33`, etc. para fatos de usuário; `F_INF_03`, etc. para fatos inferidos).

### Cadastrar regra

```bash
python q1/editor.py add-rule \
  --label "Crash no menu + overlay Steam -> conflito de overlay" \
  --conditions F32,F24 \
  --conclusion-type hypothesis \
  --conclusion-id H1 \
  --priority 2 \
  --explanation-why "A regra verifica se o crash no menu está relacionado a overlay ativo." \
  --explanation-how "A conclusão foi obtida combinando o fato F32 com o overlay Steam F24."
```

As condições são IDs de fatos separados por vírgula. A conclusão pode ser:

- `--conclusion-type intermediate`, apontando para um `fact_id`.
- `--conclusion-type hypothesis`, apontando para um `hypothesis_id`.

### Editar regra existente

```bash
python q1/editor.py edit-rule R22 \
  --conditions F01,F23 \
  --priority 4 \
  --label "Crash + Discord -> conflito de overlay"
```

Campos omitidos são preservados.

### Remover regra

```bash
python q1/editor.py remove-rule R22
```

### Usar outra base JSON

```bash
python q1/editor.py --kb caminho/para/outra_base.json list-rules
```

Isso atende ao requisito de reutilizar a shell em outros domínios sem alterar o código-fonte.

## Validação

Validação do schema e relatório de sanidade:

```bash
cd q1/tests
python validate.py
```

Testes automatizados do editor:

```bash
python -m unittest q1.tests.test_editor
```

## Entregáveis Pendentes

- Relatório técnico completo da Questão 1.
- Demonstração de pelo menos 3 consultas diferentes.
- Implementação final do mecanismo de explicação e da interface de consulta do usuário.
- Questão 2 e Questão 3 conforme divisão do grupo.

> Os sistemas de diagnóstico desenvolvidos neste projeto têm finalidade exclusivamente educacional e não devem ser usados como ferramentas reais de diagnóstico.
