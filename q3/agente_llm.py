"""
Agente de Tarefas Baseado em LLM (padrão ReAct)
Questão 3 - Lista 1 de IA

Um agente recebe um OBJETIVO em linguagem natural, PLANEJA os passos,
DECIDE quais FERRAMENTAS usar, EXECUTA cada uma, OBSERVA o resultado e
ITERA até concluir — então sintetiza a resposta final.

Padrão implementado: ReAct (Reasoning + Acting).
   Pensamento -> Ação (ferramenta) -> Observação -> ... -> Resposta Final

LLM por trás: Ollama (local, gratuito, sem chave de API).
   Se o Ollama não estiver instalado/rodando, o agente cai automaticamente
   em um MODO SIMULADO que demonstra a mesma arquitetura sem precisar de LLM.

Como instalar o Ollama (opcional):
   1. Baixe em https://ollama.com/download
   2. No terminal:  ollama pull llama3.2
   3. Deixe o Ollama aberto e rode este script.
"""

import json
import re
import math
import urllib.request
import datetime

# ============================================================
# 1. FERRAMENTAS (o que o agente pode "fazer no mundo")
# ============================================================
# Cada ferramenta é uma função Python. O agente escolhe qual chamar.

def ferramenta_calculadora(expressao: str) -> str:
    """Avalia uma expressão matemática. Ex.: '15 * 8 + raiz(144)'."""
    try:
        expr = expressao.lower()
        expr = expr.replace("raiz", "math.sqrt").replace("^", "**")
        expr = expr.replace("pi", str(math.pi))
        # ambiente restrito (segurança): só funções matemáticas
        permitido = {"math": math, "__builtins__": {}}
        resultado = eval(expr, permitido)
        return f"{resultado}"
    except Exception as e:
        return f"Erro ao calcular: {e}"


def ferramenta_data_hora(_: str = "") -> str:
    """Retorna a data e hora atuais."""
    agora = datetime.datetime.now()
    dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    return f"{agora.strftime('%d/%m/%Y %H:%M')} ({dias[agora.weekday()]}-feira)"


def ferramenta_conversor_moeda(consulta: str) -> str:
    """Converte valores entre moedas usando taxas fixas (offline, educacional).
    Formato esperado: 'VALOR DE PARA', ex.: '100 USD BRL'."""
    taxas = {  # taxas fixas para fins didáticos (relativas ao BRL)
        "BRL": 1.0, "USD": 5.40, "EUR": 5.90, "GBP": 6.80,
    }
    try:
        partes = consulta.upper().split()
        valor = float(partes[0])
        de, para = partes[1], partes[2]
        if de not in taxas or para not in taxas:
            return f"Moeda não suportada. Use: {', '.join(taxas)}"
        em_brl = valor * taxas[de]
        convertido = em_brl / taxas[para]
        return f"{valor} {de} = {convertido:.2f} {para}"
    except Exception:
        return "Formato inválido. Use: 'VALOR MOEDA_ORIGEM MOEDA_DESTINO', ex.: '100 USD BRL'"


def ferramenta_base_conhecimento(pergunta: str) -> str:
    """Consulta uma pequena base de fatos local (simula uma busca)."""
    fatos = {
        "capital do brasil": "Brasília é a capital do Brasil.",
        "maior planeta": "Júpiter é o maior planeta do Sistema Solar.",
        "velocidade da luz": "A velocidade da luz é aproximadamente 299.792 km/s.",
        "autor dom casmurro": "Dom Casmurro foi escrito por Machado de Assis.",
        "fórmula da água": "A fórmula química da água é H2O.",
    }
    p = pergunta.lower().strip()
    # 1) correspondência direta
    for chave, resposta in fatos.items():
        if chave in p:
            return resposta
    # 2) correspondência por sobreposição de palavras-chave
    stop = {"qual", "é", "e", "o", "a", "de", "do", "da", "me", "diga", "que",
            "the", "autor", "capital", "fórmula", "formula"}
    palavras_p = {w for w in re.findall(r"\w+", p) if w not in stop}
    melhor, score = None, 0
    for chave, resposta in fatos.items():
        palavras_c = set(re.findall(r"\w+", chave))
        comum = len(palavras_p & palavras_c)
        if comum > score:
            score, melhor = comum, resposta
    if melhor and score >= 1:
        return melhor
    return "Não encontrei esse fato na base de conhecimento local."


# Registro de ferramentas: nome -> (função, descrição para o LLM)
FERRAMENTAS = {
    "calculadora": (ferramenta_calculadora,
        "Faz cálculos matemáticos. Entrada: uma expressão como '15*8+raiz(144)'."),
    "data_hora": (ferramenta_data_hora,
        "Retorna a data e hora atuais. Entrada: vazio."),
    "conversor_moeda": (ferramenta_conversor_moeda,
        "Converte moedas (BRL, USD, EUR, GBP). Entrada: 'VALOR ORIGEM DESTINO', ex.: '100 USD BRL'."),
    "base_conhecimento": (ferramenta_base_conhecimento,
        "Consulta fatos gerais. Entrada: a pergunta em texto."),
}


def descricao_ferramentas() -> str:
    linhas = [f"- {nome}: {desc}" for nome, (_, desc) in FERRAMENTAS.items()]
    return "\n".join(linhas)


# ============================================================
# 2. CAMADA DO LLM (Ollama com fallback simulado)
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "llama3.2"


def chamar_ollama(prompt: str) -> str | None:
    """Tenta chamar o Ollama local. Retorna None se indisponível."""
    try:
        dados = json.dumps({
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }).encode("utf-8")
        req = urllib.request.Request(OLLAMA_URL, data=dados,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())["response"]
    except Exception:
        return None


def llm_decide(objetivo: str, historico: list) -> dict:
    """Pede ao LLM a próxima ação no formato ReAct.
    Retorna dict: {'pensamento':..., 'acao':..., 'entrada':...}
    ou {'pensamento':..., 'resposta_final':...}."""

    prompt = montar_prompt(objetivo, historico)
    resposta = chamar_ollama(prompt)

    if resposta is None:
        # MODO SIMULADO: heurística que imita o raciocínio do LLM
        return decisao_simulada(objetivo, historico)

    return parse_resposta_llm(resposta)


def montar_prompt(objetivo: str, historico: list) -> str:
    hist_txt = ""
    for h in historico:
        hist_txt += f"\nPensamento: {h['pensamento']}\nAção: {h['acao']}\nEntrada: {h['entrada']}\nObservação: {h['observacao']}\n"
    return f"""Você é um agente que resolve tarefas usando ferramentas.
Ferramentas disponíveis:
{descricao_ferramentas()}

Responda SEMPRE em JSON, em um destes dois formatos:
{{"pensamento": "...", "acao": "nome_da_ferramenta", "entrada": "..."}}
ou, quando já tiver a resposta:
{{"pensamento": "...", "resposta_final": "..."}}

Objetivo do usuário: {objetivo}
{hist_txt}
Próxima ação (apenas o JSON):"""


def parse_resposta_llm(texto: str) -> dict:
    """Extrai o JSON da resposta do LLM."""
    try:
        m = re.search(r"\{.*\}", texto, re.DOTALL)
        return json.loads(m.group(0))
    except Exception:
        return {"pensamento": "Não consegui interpretar; encerrando.",
                "resposta_final": texto.strip()[:300]}


# ---------- MODO SIMULADO (sem LLM) ----------

def decisao_simulada(objetivo: str, historico: list) -> dict:
    """Imita o raciocínio do agente por heurística, para funcionar sem Ollama.
    Detecta subtarefas no objetivo e as resolve uma a uma."""
    obj = objetivo.lower()
    ja_feitas = {h["acao"] for h in historico}

    # detecta necessidade de cálculo
    if re.search(r"\d+\s*[\+\-\*/x×]\s*\d+|raiz|calcul", obj) and "calculadora" not in ja_feitas:
        expr = extrair_expressao(objetivo)
        return {"pensamento": "O objetivo envolve uma conta; vou usar a calculadora.",
                "acao": "calculadora", "entrada": expr}

    # detecta conversão de moeda
    if re.search(r"\b(usd|eur|gbp|d[óo]lar|euro|libra)\b", obj) and "conversor_moeda" not in ja_feitas:
        return {"pensamento": "Há uma conversão de moeda a fazer.",
                "acao": "conversor_moeda", "entrada": extrair_conversao(objetivo)}

    # detecta pergunta de data/hora
    if re.search(r"\b(hoje|data|hora|dia)\b", obj) and "data_hora" not in ja_feitas:
        return {"pensamento": "Preciso saber a data/hora atual.",
                "acao": "data_hora", "entrada": ""}

    # detecta pergunta factual
    if re.search(r"\b(capital|planeta|autor|f[óo]rmula|velocidade|casmurro|luz|água|agua)\b", obj) and "base_conhecimento" not in ja_feitas:
        return {"pensamento": "É uma pergunta de conhecimento geral.",
                "acao": "base_conhecimento", "entrada": objetivo}

    # nada mais a fazer: sintetiza
    obs = " ".join(f"{h['acao']}={h['observacao']}" for h in historico)
    return {"pensamento": "Já reuni as informações necessárias.",
            "resposta_final": sintetizar_simulado(objetivo, historico)}


def extrair_expressao(texto: str) -> str:
    # normaliza símbolos de multiplicação só entre números (evita virar 'a'->'*')
    t = texto.lower()
    t = re.sub(r"(\d)\s*[x×]\s*(\d)", r"\1*\2", t)
    # captura o trecho que parece uma expressão (números, operadores, raiz, parênteses)
    m = re.search(r"(?:raiz|\d|\()[\d\.\s\+\-\*/\(\)\^]*(?:raiz\([\d\.]+\))?[\d\.\s\+\-\*/\(\)\^]*", t)
    if not m:
        return texto
    expr = m.group(0).strip()
    # garante que 'raiz(...)' não tenha sido cortado
    raiz_match = re.search(r"raiz\([\d\.]+\)", t)
    if raiz_match and raiz_match.group(0) not in expr:
        expr += "+" + raiz_match.group(0)
    return expr


def extrair_conversao(texto: str) -> str:
    t = texto.upper()
    val = re.search(r"\d+(?:[\.,]\d+)?", t)
    valor = val.group(0).replace(",", ".") if val else "1"
    moedas = re.findall(r"\b(BRL|USD|EUR|GBP)\b", t)
    de = moedas[0] if len(moedas) > 0 else "USD"
    para = moedas[1] if len(moedas) > 1 else "BRL"
    return f"{valor} {de} {para}"


def sintetizar_simulado(objetivo: str, historico: list) -> str:
    if not historico:
        return "Não foram necessárias ferramentas para esta tarefa."
    partes = [f"{h['observacao']}" for h in historico]
    return "Com base nas etapas executadas: " + "; ".join(partes) + "."


# ============================================================
# 3. O AGENTE (ciclo ReAct)
# ============================================================

class AgenteTarefas:
    def __init__(self, max_passos=6, verbose=True):
        self.max_passos = max_passos
        self.verbose = verbose

    def executar(self, objetivo: str) -> str:
        if self.verbose:
            print(f"\n{'='*60}\nOBJETIVO: {objetivo}\n{'='*60}")
        historico = []

        for passo in range(1, self.max_passos + 1):
            decisao = llm_decide(objetivo, historico)

            # caso o agente decida finalizar
            if "resposta_final" in decisao:
                if self.verbose:
                    print(f"\n[Passo {passo}] Pensamento: {decisao.get('pensamento','')}")
                    print(f"\n>>> RESPOSTA FINAL: {decisao['resposta_final']}")
                return decisao["resposta_final"]

            acao = decisao.get("acao")
            entrada = decisao.get("entrada", "")

            if self.verbose:
                print(f"\n[Passo {passo}] Pensamento: {decisao.get('pensamento','')}")
                print(f"           Ação: {acao}  |  Entrada: '{entrada}'")

            # executa a ferramenta escolhida
            if acao in FERRAMENTAS:
                func = FERRAMENTAS[acao][0]
                observacao = func(entrada)
            else:
                observacao = f"Ferramenta '{acao}' não existe."

            if self.verbose:
                print(f"           Observação: {observacao}")

            historico.append({
                "pensamento": decisao.get("pensamento", ""),
                "acao": acao, "entrada": entrada, "observacao": observacao,
            })

        # se esgotou os passos, sintetiza o que tem
        final = sintetizar_simulado(objetivo, historico)
        if self.verbose:
            print(f"\n>>> RESPOSTA FINAL (limite de passos): {final}")
        return final


# ============================================================
# 4. DEMONSTRAÇÃO / INTERAÇÃO
# ============================================================

def status_llm():
    if chamar_ollama("responda apenas: ok") is not None:
        print(f"[LLM] Ollama conectado (modelo {MODELO}).")
    else:
        print("[LLM] Ollama indisponível — rodando em MODO SIMULADO.")
        print("      (Para usar o LLM real: instale o Ollama e rode 'ollama pull llama3.2')")


def demo():
    status_llm()
    agente = AgenteTarefas()
    tarefas = [
        "Quanto é 15 * 8 + raiz(144)?",
        "Converta 250 dólares (USD) para reais (BRL).",
        "Qual é a capital do Brasil e que dia é hoje?",
        "Calcule 100 * 5.40 e depois me diga o autor de Dom Casmurro.",
    ]
    for t in tarefas:
        agente.executar(t)


def interativo():
    status_llm()
    agente = AgenteTarefas()
    print("\n" + "=" * 60)
    print("  AGENTE DE TAREFAS — digite um objetivo (ou 'sair')")
    print("  Ferramentas: calculadora, conversor de moeda, data/hora,")
    print("               base de conhecimento")
    print("=" * 60)
    while True:
        try:
            objetivo = input("\nObjetivo > ").strip()
        except EOFError:
            break
        if objetivo.lower() in ("sair", "exit", "quit", ""):
            print("Encerrando.")
            break
        agente.executar(objetivo)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        interativo()