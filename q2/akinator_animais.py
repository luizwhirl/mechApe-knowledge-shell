"""
Akinator de Animais - Sistema Inteligente de Perguntas e Respostas
Questão 2.1 - Lista 1 de IA

Abordagem: pontuação probabilística (scoring). Cada animal tem um score
que sobe ou desce conforme as respostas. Tolera respostas "Não Sei" e
erros do usuário (pesos suaves em vez de eliminação rígida).

A próxima pergunta é escolhida por GANHO DE INFORMAÇÃO: o atributo que
melhor divide os candidatos atuais (mais próximo de 50/50).
"""

import math

# ============================================================
# BASE DE CONHECIMENTO
# 22 entidades x 16 atributos (requisito: >=20 e >=15)
# ============================================================

ATRIBUTOS = [
    "é_mamífero", "tem_pelo", "voa", "vive_na_água", "doméstico",
    "é_carnívoro", "tem_quatro_patas", "tem_penas", "põe_ovos",
    "é_grande", "vive_na_áfrica", "tem_chifres_ou_presas",
    "é_réptil", "nada_bem", "é_predador", "tem_cauda_longa",
]

# True = possui o atributo, False = não possui
KB = {
    "Cachorro":  [True, True, False, False, True, True, True, False, False, False, False, False, False, False, False, True],
    "Gato":      [True, True, False, False, True, True, True, False, False, False, False, False, False, False, True, True],
    "Cavalo":    [True, True, False, False, True, False, True, False, False, True, False, False, False, False, False, True],
    "Vaca":      [True, True, False, False, True, False, True, False, False, True, False, True, False, False, False, True],
    "Leão":      [True, True, False, False, False, True, True, False, False, True, True, False, False, False, True, True],
    "Tigre":     [True, True, False, False, False, True, True, False, False, True, False, False, False, True, True, True],
    "Elefante":  [True, False, False, False, False, False, True, False, False, True, True, True, False, False, False, False],
    "Águia":     [False, False, True, False, False, True, False, True, True, False, False, False, False, False, True, False],
    "Pinguim":   [False, False, False, True, False, True, False, True, True, False, False, False, False, True, True, False],
    "Tubarão":   [False, False, False, True, False, True, False, False, False, True, False, True, False, True, True, True],
    "Golfinho":  [True, False, False, True, False, True, False, False, False, True, False, False, False, True, True, False],
    "Baleia":    [True, False, False, True, False, True, False, False, False, True, False, False, False, True, True, False],
    "Cobra":     [False, False, False, False, False, True, False, False, True, False, False, True, True, True, True, True],
    "Crocodilo": [False, False, False, True, False, True, True, False, True, True, True, True, True, True, True, True],
    "Tartaruga": [False, False, False, True, False, False, True, False, True, False, False, False, True, True, False, False],
    "Galinha":   [False, False, False, False, True, False, False, True, True, False, False, False, False, False, False, False],
    "Papagaio":  [False, False, True, False, True, False, False, True, True, False, False, False, False, False, False, True],
    "Morcego":   [True, True, True, False, False, True, False, False, False, False, False, False, False, False, True, False],
    "Coelho":    [True, True, False, False, True, False, True, False, False, False, False, False, False, False, False, False],
    "Macaco":    [True, True, False, False, False, False, False, False, False, False, True, False, False, False, False, True],
    "Urso":      [True, True, False, False, False, True, True, False, False, True, False, True, False, True, True, False],
    "Sapo":      [False, False, False, True, False, True, True, False, True, False, False, False, False, True, True, False],
}

# ============================================================
# MOTOR DE INFERÊNCIA
# ============================================================

# Pesos suaves: tolerância a respostas imperfeitas
P_ACERTO = 0.85   # prob. de a resposta bater com o atributo real
P_ERRO = 0.15     # prob. de divergência (ruído)


class Akinator:
    def __init__(self, kb, atributos):
        self.kb = kb
        self.atributos = atributos
        # score inicial uniforme (prior)
        self.scores = {nome: 1.0 / len(kb) for nome in kb}
        self.perguntados = set()

    def _idx(self, atributo):
        return self.atributos.index(atributo)

    def atualizar(self, atributo, resposta):
        """resposta: True (sim), False (não), None (não sei)."""
        if resposta is None:
            self.perguntados.add(atributo)
            return
        i = self._idx(atributo)
        for nome, score in self.scores.items():
            tem = self.kb[nome][i]
            # verossimilhança: a resposta do usuário bate com o atributo?
            if tem == resposta:
                self.scores[nome] = score * P_ACERTO
            else:
                self.scores[nome] = score * P_ERRO
        self.perguntados.add(atributo)
        self._normalizar()

    def _normalizar(self):
        total = sum(self.scores.values())
        if total > 0:
            for nome in self.scores:
                self.scores[nome] /= total

    def melhor_pergunta(self):
        """Escolhe o atributo que melhor divide os candidatos (ganho de info).
        Mede a divisão ponderada pelos scores; ideal é o mais próximo de 50/50."""
        melhor_attr = None
        melhor_valor = -1.0
        for attr in self.atributos:
            if attr in self.perguntados:
                continue
            i = self.atributos.index(attr)
            # massa de probabilidade dos que TÊM o atributo
            massa_sim = sum(s for nome, s in self.scores.items() if self.kb[nome][i])
            # quão próximo de 0.5? usa entropia binária como medida de divisão
            ganho = self._entropia_binaria(massa_sim)
            if ganho > melhor_valor:
                melhor_valor = ganho
                melhor_attr = attr
        return melhor_attr

    @staticmethod
    def _entropia_binaria(p):
        if p <= 0 or p >= 1:
            return 0.0
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    def ranking(self):
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

    def melhor_candidato(self):
        return self.ranking()[0]



# INTERFACE (terminal)


def texto_pergunta(atributo):
    perguntas = {
        "é_mamífero": "O animal é mamífero?",
        "tem_pelo": "O animal tem pelo?",
        "voa": "O animal voa?",
        "vive_na_água": "O animal vive na água?",
        "doméstico": "É um animal doméstico?",
        "é_carnívoro": "O animal é carnívoro?",
        "tem_quatro_patas": "O animal tem quatro patas?",
        "tem_penas": "O animal tem penas?",
        "põe_ovos": "O animal põe ovos?",
        "é_grande": "É um animal grande?",
        "vive_na_áfrica": "Vive (também) na África?",
        "tem_chifres_ou_presas": "Tem chifres ou presas?",
        "é_réptil": "O animal é réptil?",
        "nada_bem": "O animal nada bem?",
        "é_predador": "O animal é predador?",
        "tem_cauda_longa": "O animal tem cauda longa?",
    }
    return perguntas.get(atributo, atributo + "?")


def ler_resposta():
    while True:
        r = input("  > ").strip().lower()
        if r in ("s", "sim", "y"):
            return True
        if r in ("n", "não", "nao", "no"):
            return False
        if r in ("ns", "não sei", "nao sei", "?", "talvez"):
            return None
        print("  Responda: s (sim) / n (não) / ns (não sei)")


def jogar():
    print("=" * 50)
    print("  AKINATOR DE ANIMAIS")
    print("  Pense em um animal e responda às perguntas.")
    print("  Respostas: s = sim | n = não | ns = não sei")
    print("=" * 50)

    aki = Akinator(KB, ATRIBUTOS)
    LIMIAR = 0.90          # confiança para arriscar o palpite
    MAX_PERGUNTAS = len(ATRIBUTOS)
    n = 0

    while n < MAX_PERGUNTAS:
        nome, prob = aki.melhor_candidato()
        if prob >= LIMIAR:
            break

        attr = aki.melhor_pergunta()
        if attr is None:
            break

        n += 1
        print(f"\nPergunta {n}: {texto_pergunta(attr)}")
        resposta = ler_resposta()
        aki.atualizar(attr, resposta)

        topo, p = aki.melhor_candidato()
        print(f"  (hipótese atual: {topo} — {p*100:.1f}%)")

    nome, prob = aki.melhor_candidato()
    print("\n" + "=" * 50)
    print(f"  Meu palpite: é um(a) {nome.upper()}!")
    print(f"  Confiança: {prob*100:.1f}%  |  Perguntas feitas: {n}")
    print("=" * 50)

    print("\n  Top 3 hipóteses:")
    for nome, p in aki.ranking()[:3]:
        print(f"    {nome:12s} {p*100:5.1f}%")

    acertou = input("\n  Acertei? (s/n) > ").strip().lower()
    if acertou in ("s", "sim"):
        print("  :) Obrigado por jogar!")
    else:
        print("  Ainda estou aprendendo. Anote esse caso de falha para o relatório!")


if __name__ == "__main__":
    jogar()