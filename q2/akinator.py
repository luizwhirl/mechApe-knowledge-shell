"""
Motor de inferência probabilístico do Akinator — Questão 2.1

Cada resposta atualiza os scores de todos os candidatos via regra de Bayes
(likelihood × prior), em vez de eliminar candidatos estritamente.
Isso torna o sistema tolerante a respostas ambíguas ou imprecisas.
"""

from __future__ import annotations
import json
import math
from pathlib import Path


class Akinator:
    # P(resposta errada | atributo divergente) — tolerância a erros do usuário
    EPSILON: float = 0.05
    # Adivinha quando o personagem mais provável atinge este nível de confiança
    CONFIDENCE_THRESHOLD: float = 0.85

    def __init__(self, kb_path: str | Path | None = None):
        if kb_path is None:
            kb_path = Path(__file__).parent / "knowledge_base.json"
        with open(kb_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.attributes: list[dict] = self.kb["attributes"]
        self.all_characters: list[dict] = self.kb["characters"]
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
        """
        Entropia de Shannon ponderada pelas probabilidades atuais.
        Mede o ganho de informação esperado ao perguntar sobre este atributo.
        """
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
        """
        Retorna IDs de atributos que são logicamente determinados por
        respostas já dadas — perguntar sobre eles seria redundante.

        Regras:
        - A06 (adulto) ↔ A19 (criança) são inversas: responder uma elimina a outra.
        - A04=F (não animado) → A05=F (não pode ser anime se não é animado).
        - A05=T (anime) → A04=T (se é anime, com certeza é animado).
        """
        pular: set[str] = set()
        if "A06" in self.answered:
            pular.add("A19")
        if "A19" in self.answered:
            pular.add("A06")
        if self.answered.get("A04") is False:
            pular.add("A05")
        if self.answered.get("A05") is True:
            pular.add("A04")
        return pular

    def proxima_pergunta(self) -> dict | None:
        """Retorna o atributo não respondido com maior ganho de informação esperado."""
        pular = self._atributos_implicitos()
        nao_respondidos = [
            a for a in self.attributes
            if a["id"] not in self.answered and a["id"] not in pular
        ]
        if not nao_respondidos:
            return None
        return max(nao_respondidos, key=lambda a: self._entropia_ponderada(a["id"]))

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
        """
        Personagens com probabilidade normalizada >= 1/n (quinhão justo).
        Equivale aos candidatos 'ainda viáveis' na distribuição atual.
        """
        n = len(self.all_characters)
        threshold = 1.0 / n
        norm = self._normalized()
        ativos = [c for c in self.all_characters if norm[c["id"]] >= threshold]
        # Garante ao menos 1 candidato (o mais provável) mesmo se todos estão abaixo
        return ativos if ativos else [self.melhor_palpite()]

    def confianca_top(self) -> float:
        """Probabilidade normalizada do candidato mais provável (0.0–1.0)."""
        norm = self._normalized()
        return max(norm.values()) if norm else 0.0

    def pode_adivinhar(self) -> bool:
        return self.confianca_top() >= self.CONFIDENCE_THRESHOLD

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
