"""
Motor de inferência probabilístico do Akinator — Questão 2.1

Cada resposta atualiza os scores via regra de Bayes, em vez de eliminar
candidatos — o que torna o sistema tolerante a respostas ambíguas.
"""

from __future__ import annotations
import json
import math
import random
from pathlib import Path


class Akinator:
    # Parâmetros de calibração do motor
    EPSILON: float = 0.20               # Tolerância a respostas subjetivas/divergentes
    CONFIDENCE_THRESHOLD: float = 0.95  # Confiança absoluta para palpitar
    MIN_QUESTIONS: int = 7              # Mínimo de perguntas antes de qualquer palpite
    DOMINANCE_RATIO: float = 8.0        # Palpita se o líder for N× mais provável que o 2º
    DOMINANCE_MIN_CONF: float = 0.50    # Confiança mínima para o palpite por dominância
    ENTROPIA_TOLERANCIA: float = 0.01   # Faixa de empate para sortear entre as melhores perguntas

    def __init__(self, kb_path: str | Path | None = None, seed: int | None = None):
        if kb_path is None:
            kb_path = Path(__file__).parent / "knowledge_base.json"
        with open(kb_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.attributes: list[dict] = self.kb["attributes"]
        self.all_characters: list[dict] = self.kb["characters"]
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        # Score inicial uniforme (prior equiprovável)
        self.scores: dict[str, float] = {c["id"]: 1.0 for c in self.all_characters}
        self.answered: dict[str, bool | None] = {}
        self.history: list[tuple[str, str, int]] = []

    # ------------------------------------------------------------------
    # Núcleo probabilístico
    # ------------------------------------------------------------------

    def _normalized(self) -> dict[str, float]:
        total = sum(self.scores.values())
        if total == 0:
            return {cid: 0.0 for cid in self.scores}
        return {cid: s / total for cid, s in self.scores.items()}

    def _update_scores(self, attr_id: str, valor: bool) -> None:
        """Atualiza scores via regra de Bayes: score *= P(resposta | personagem)."""
        for c in self.all_characters:
            c_val = c["attributes"].get(attr_id)
            if c_val == valor:
                self.scores[c["id"]] *= (1.0 - self.EPSILON)
            else:
                self.scores[c["id"]] *= self.EPSILON

    def _entropia_ponderada(self, attr_id: str) -> float:
        """Ganho de informação esperado da pergunta (entropia de Shannon ponderada pelas probabilidades)."""
        norm = self._normalized()
        p_sim = sum(
            norm[c["id"]] for c in self.all_characters
            if c["attributes"].get(attr_id) is True
        )
        p_nao = 1.0 - p_sim
        if p_sim <= 0.0 or p_nao <= 0.0:
            return 0.0
        return -(p_sim * math.log2(p_sim) + p_nao * math.log2(p_nao))

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def _atributos_implicitos(self) -> set[str]:
        """IDs já determinados pela lógica das respostas anteriores (perguntá-los seria redundante)."""
        pular: set[str] = set()
        # Pares de atributos logicamente ligados: adulto↔criança, animado↔anime↔videogame.
        if "A06" in self.answered:
            pular.add("A19")
        if "A19" in self.answered:
            pular.add("A06")
        if self.answered.get("A04") is False:
            pular.add("A05")
        if self.answered.get("A05") is True:
            pular.add("A04")
        if self.answered.get("A04") is True:
            pular.add("A26")
        if self.answered.get("A26") is True:
            pular.add("A04")
            pular.add("A05")
        return pular

    def proxima_pergunta(self) -> dict | None:
        """Sorteia entre os atributos de maior ganho de informação (evita ordem sempre igual)."""
        pular = self._atributos_implicitos()
        nao_respondidos = [
            a for a in self.attributes
            if a["id"] not in self.answered and a["id"] not in pular
        ]
        if not nao_respondidos:
            return None
        entropias = {a["id"]: self._entropia_ponderada(a["id"]) for a in nao_respondidos}
        melhor = max(entropias.values())
        candidatas = [a for a in nao_respondidos if entropias[a["id"]] >= melhor - self.ENTROPIA_TOLERANCIA]
        return self._rng.choice(candidatas)

    def responder(self, attr_id: str, resposta: str) -> None:
        """
        Processa a resposta do usuário e atualiza os scores.
        resposta: 'sim' | 'nao' | 'nao_sei'
        """
        candidatos_antes = len(self.candidates)
        if resposta != "nao_sei":
            self._update_scores(attr_id, resposta == "sim")
            self.answered[attr_id] = resposta == "sim"
        else:
            self.answered[attr_id] = None
        self.history.append((attr_id, resposta, candidatos_antes))

    @property
    def candidates(self) -> list[dict]:
        """Candidatos ainda viáveis: probabilidade >= 10% da do líder atual (limiar relativo)."""
        norm = self._normalized()
        if not norm:
            return self.all_characters[:]
        top_score = max(norm.values())
        threshold = top_score * 0.10
        ativos = [c for c in self.all_characters if norm[c["id"]] >= threshold]
        return ativos if ativos else [self.melhor_palpite()]

    def confianca_top(self) -> float:
        """Probabilidade normalizada do candidato mais provável (0.0–1.0)."""
        norm = self._normalized()
        return max(norm.values()) if norm else 0.0

    def _distingue(self, c1: dict, c2: dict) -> str | None:
        """ID de um atributo ainda não perguntado que separaria c1 de c2, se existir."""
        pular = self._atributos_implicitos()
        for a in self.attributes:
            aid = a["id"]
            if aid in self.answered or aid in pular:
                continue
            if c1["attributes"].get(aid) != c2["attributes"].get(aid):
                return aid
        return None

    def pode_adivinhar(self) -> bool:
        """
        Palpita por confiança absoluta alta, ou por dominância sobre o 2º colocado —
        mas a dominância só vale se não sobrar pergunta capaz de separar os dois.
        """
        if self.total_perguntas() < self.MIN_QUESTIONS:
            return False
        top2 = self.top_n(2)
        if not top2:
            return False
        conf = top2[0][1]
        if conf >= self.CONFIDENCE_THRESHOLD:
            return True
        if len(top2) < 2 or top2[1][1] <= 0 or conf < self.DOMINANCE_MIN_CONF:
            return False
        dominante = (top2[0][1] / top2[1][1]) >= self.DOMINANCE_RATIO
        if not dominante:
            return False
        return self._distingue(top2[0][0], top2[1][0]) is None

    def sem_candidatos(self) -> bool:
        """True apenas se todos os scores colapsaram a valores ínfimos."""
        return all(s < 1e-15 for s in self.scores.values())

    def perguntas_esgotadas(self) -> bool:
        return all(a["id"] in self.answered for a in self.attributes)

    def melhor_palpite(self) -> dict | None:
        if not self.all_characters:
            return None
        return max(self.all_characters, key=lambda c: self.scores[c["id"]])

    def top_n(self, n: int = 3) -> list[tuple[dict, float]]:
        """Retorna os N personagens mais prováveis com suas probabilidades."""
        norm = self._normalized()
        sorted_chars = sorted(
            self.all_characters, key=lambda c: norm[c["id"]], reverse=True
        )
        return [(c, norm[c["id"]]) for c in sorted_chars[:n]]

    def total_perguntas(self) -> int:
        return len(self.history)

    def resumo_sessao(self) -> dict:
        return {
            "perguntas_feitas": self.total_perguntas(),
            "candidatos_ativos": len(self.candidates),
            "palpite": self.melhor_palpite()["name"] if self.melhor_palpite() else None,
            "confianca": f"{self.confianca_top():.1%}",
            "top3": [(c["name"], f"{p:.1%}") for c, p in self.top_n(3)],
        }
