"""
Mecanismo de Explicação do MechApe - Módulo 4 (P3)

Responde às perguntas clássicas de sistemas especialistas:
  - Por quê?  Justifica por que determinada pergunta foi feita ao usuário.
  - Como?     Explica como determinado diagnóstico foi obtido.

Não modifica o motor de inferência. Lê o estado da sessão e a base de
conhecimento após a inferência ter rodado para reconstruir as explicações.

Uso:
    from motor_inferencia import MotorInferencia
    from q1.explicador import ExplicadorInferencia

    motor = MotorInferencia("q1/tests/knowledge_base.json")
    motor.sessao["facts_confirmed"].update(["F02", "F19"])
    motor.encadeamento_para_frente()

    exp = ExplicadorInferencia(motor)
    print(exp.por_que("F19"))
    print(exp.como("H5"))
    print(exp.resumo_sessao())
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import Any


class ExplicadorInferencia:
    """
    Recebe o motor já executado e oferece os métodos de explicação clássicos.

    Todos os dados necessários já estão no motor após a inferência:
      - motor.sessao["questions_asked"]    → fatos que precisavam do usuário
      - motor.sessao["rules_fired"]        → regras que dispararam
      - motor.sessao["hypotheses_confirmed"] → hipóteses confirmadas
      - motor.base                         → base com explanation_why/how
    """

    def __init__(self, motor: Any) -> None:
        if hasattr(motor, "base") and hasattr(motor, "sessao"):
            self._motor = motor
            self._base: dict[str, Any] = motor.base
        elif isinstance(motor, dict):
            self._motor = SimpleNamespace(
                sessao={
                    "rules_fired": set(),
                    "hypotheses_confirmed": set(),
                    "questions_asked": set(),
                }
            )
            self._base = motor
        else:
            raise TypeError(
                "ExplicadorInferencia espera um motor com base/sessao ou um dict da base."
            )

    # ------------------------------------------------------------------
    # Lookups na base (O(n), n pequeno para domínios típicos)
    # ------------------------------------------------------------------

    def _fato(self, fato_id: str) -> dict[str, Any] | None:
        for f in self._base["facts"]["items"]:
            if f["id"] == fato_id:
                return f
        return None

    def _hipotese(self, hipotese_id: str) -> dict[str, Any] | None:
        for h in self._base["hypotheses"]["items"]:
            if h["id"] == hipotese_id:
                return h
        return None

    def _regra(self, regra_id: str) -> dict[str, Any] | None:
        for r in self._base["rules"]["items"]:
            if r["id"] == regra_id:
                return r
        return None

    # ------------------------------------------------------------------
    # Reconstrução das associações a partir da sessão
    # ------------------------------------------------------------------

    def _regras_que_confirmaram(self, hipotese_id: str) -> list[dict[str, Any]]:
        """
        Retorna as regras disparadas cuja conclusão é a hipótese dada.
        Usa rules_fired (já preenchido pelo motor) filtrado pelo campo
        hypothesis_id da conclusão.
        """
        resultado = []
        for regra_id in self._motor.sessao["rules_fired"]:
            regra = self._regra(regra_id)
            if regra and regra["conclusion"].get("hypothesis_id") == hipotese_id:
                resultado.append(regra)
        return resultado

    def _regra_que_exigiu(self, fato_id: str) -> dict[str, Any] | None:
        """
        Para o 'Por quê?': encontra a primeira regra disparável que tinha
        fato_id como condição mas ainda não pôde ser satisfeita — ou seja,
        uma regra cujas condições incluem fato_id e que ainda não disparou
        (pois o fato não estava confirmado).

        Também verifica regras que dispararam e usaram o fato, para o caso
        de o fato ter sido confirmado pelo usuário antes da inferência.
        """
        # Procura em todas as regras da base que mencionam fato_id
        for regra in self._base["rules"]["items"]:
            if fato_id in regra["conditions"]:
                return regra
        return None

    def _hipotese_alvo_de(self, fato_id: str) -> str | None:
        """
        Encontra o alvo que motivou a pergunta sobre fato_id,
        rastreando a cadeia: fato_id → regra → conclusão (hipótese ou
        fato inferido que leva a uma hipótese).
        """
        for regra in self._base["rules"]["items"]:
            if fato_id not in regra["conditions"]:
                continue
            conclusao = regra["conclusion"]
            if "hypothesis_id" in conclusao:
                return conclusao["hypothesis_id"]
            if "fact_id" in conclusao:
                # Fato inferido intermediário: usa o objetivo atual da cadeia.
                return conclusao["fact_id"]
        return None

    # ------------------------------------------------------------------
    # API pública de explicação
    # ------------------------------------------------------------------

    def por_que(self, fato_id: str) -> str:
        """
        Responde: "Por que você perguntou sobre X?"

        Justifica mostrando qual hipótese estava sendo avaliada e qual
        regra exigia aquele fato como condição necessária.

        Funciona para fatos que estavam em questions_asked (o motor não
        sabia o valor) ou que foram confirmados antes da inferência.
        """
        fato = self._fato(fato_id)
        if fato is None:
            return f"Fato '{fato_id}' não encontrado na base de conhecimento."

        label_fato = fato["label"]

        regra = self._regra_que_exigiu(fato_id)
        if regra is None:
            return (
                f'Não foi encontrada nenhuma regra que exija '
                f'"{label_fato}" como condição.'
            )

        hipotese_id = self._hipotese_alvo_de(fato_id)
        hipotese = self._hipotese(hipotese_id) if hipotese_id else None
        label_hipotese = (
            f"{hipotese_id} — {hipotese['label']}" if hipotese else str(hipotese_id)
        )

        return (
            f'Perguntei sobre "{label_fato}" porque estou avaliando '
            f"o alvo {label_hipotese}.\n"
            f"Motivo ({regra['id']}): {regra['explanation_why']}"
        )

    def como(self, hipotese_id: str) -> str:
        """
        Responde: "Como você chegou ao diagnóstico X?"

        Lista as regras disparadas que confirmaram a hipótese e o
        raciocínio de cada uma, usando explanation_how da base.
        """
        hipotese = self._hipotese(hipotese_id)
        label_hipotese = (
            f"{hipotese_id} — {hipotese['label']}" if hipotese else hipotese_id
        )

        if hipotese_id not in self._motor.sessao["hypotheses_confirmed"]:
            return (
                f"A hipótese {label_hipotese} não foi confirmada nesta sessão."
            )

        regras = self._regras_que_confirmaram(hipotese_id)
        if not regras:
            return (
                f"A hipótese {label_hipotese} foi confirmada, mas não foi "
                "possível identificar as regras responsáveis."
            )

        ids = " e ".join(r["id"] for r in regras)
        linhas = [
            f"A hipótese {label_hipotese} foi confirmada "
            f"pelas regras {ids}:\n"
        ]
        for regra in regras:
            linhas.append(f"  • {regra['id']}: {regra['explanation_how']}")

        return "\n".join(linhas)

    def resumo_sessao(self) -> str:
        """
        Exibe um resumo completo da sessão: fatos perguntados ao usuário,
        regras disparadas e hipóteses confirmadas.
        """
        sessao = self._motor.sessao
        linhas = ["=== Resumo da sessão ===\n"]

        perguntas = sessao.get("questions_asked", set())
        if perguntas:
            linhas.append("Fatos solicitados ao usuário:")
            for fato_id in sorted(perguntas):
                fato = self._fato(fato_id)
                label = fato["label"] if fato else fato_id
                linhas.append(f"  • {fato_id}: {label}")
        else:
            linhas.append("Nenhum fato foi solicitado ao usuário.")

        linhas.append("")

        hipoteses = sessao.get("hypotheses_confirmed", set())
        if hipoteses:
            linhas.append("Hipóteses confirmadas:")
            for hipotese_id in sorted(hipoteses):
                hipotese = self._hipotese(hipotese_id)
                label = hipotese["label"] if hipotese else hipotese_id
                regras = self._regras_que_confirmaram(hipotese_id)
                ids = ", ".join(r["id"] for r in regras) if regras else "—"
                linhas.append(f"  • {hipotese_id} — {label}")
                linhas.append(f"    Regras: {ids}")
        else:
            linhas.append("Nenhuma hipótese foi confirmada.")

        return "\n".join(linhas)