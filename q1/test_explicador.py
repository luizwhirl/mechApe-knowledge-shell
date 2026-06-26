"""
Testes do Mecanismo de Explicação - Módulo 4 (P3)

Localização esperada: q1/test_explicador.py
Executar a partir da raiz do projeto:
    python -m unittest q1.test_explicador

Ou diretamente de dentro de q1/:
    python -m unittest test_explicador

Cobre:
  - por_que(): fato perguntado durante o backward chaining
  - como():    hipótese confirmada pelo forward e backward chaining
  - resumo_sessao(): visão geral da sessão
  - Uso sem explicador (retrocompatibilidade do motor)
  - Fatos/hipóteses sem registro (respostas de fallback)
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

# Garante que 'q1' seja encontrado independentemente de onde o teste é chamado.
# parents[1] = raiz do projeto (sobe de q1/ para /)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from q1.explicador import ExplicadorInferencia
from q1.motor_inferencia import MotorInferencia

KB = Path(__file__).resolve().parent / "tests" / "knowledge_base.json"


def _motor_com_fatos(fatos: list[str]) -> tuple[MotorInferencia, ExplicadorInferencia]:
    """Monta motor + explicador e confirma os fatos dados antes de rodar."""
    with open(KB, encoding="utf-8") as f:
        base = json.load(f)
    exp = ExplicadorInferencia(base)
    motor = MotorInferencia(caminho_base=KB, explicador=exp)
    for fato in fatos:
        motor.sessao["facts_confirmed"].add(fato)
    return motor, exp


class TestPorQue(unittest.TestCase):

    def test_por_que_retorna_texto_com_regra_e_hipotese(self):
        """
        Cenário: backward em H3 (arquivos corrompidos) sem fatos confirmados.
        R08 exige F_INF_01 (fato inferido) + F06. O motor tenta provar
        F_INF_01 recursivamente via R07, que exige F16 (DLL ausente).
        por_que("F16") deve mencionar R07 e o objetivo corrente (F_INF_01).
        """
        motor, exp = _motor_com_fatos([])
        motor.encadeamento_para_tras("H3")

        resposta = exp.por_que("F16")

        self.assertIn("DLL", resposta)
        self.assertIn("R07", resposta)
        self.assertIn("F_INF_01", resposta)

    def test_por_que_fato_nao_registrado(self):
        """Fato que nunca foi perguntado → resposta de fallback, sem exceção."""
        with open(KB, encoding="utf-8") as f:
            base = json.load(f)
        exp = ExplicadorInferencia(base)
        resposta = exp.por_que("F99")
        self.assertIsInstance(resposta, str)
        self.assertGreater(len(resposta), 0)


class TestComo(unittest.TestCase):

    def test_como_hipotese_confirmada_por_forward(self):
        """
        Cenário: forward chaining com F02 + F19 confirmados.
        R14 deve disparar e confirmar H5 (driver desatualizado).
        como("H5") deve mencionar R14.
        """
        motor, exp = _motor_com_fatos(["F02", "F19"])
        motor.encadeamento_para_frente()

        self.assertIn("H5", motor.sessao["hypotheses_confirmed"])
        resposta = exp.como("H5")

        self.assertIn("H5", resposta)
        self.assertIn("R14", resposta)

    def test_como_hipotese_confirmada_por_backward(self):
        """
        Cenário: backward em H4 (superaquecimento) com F09 + F28 confirmados.
        R12 deve disparar.
        """
        motor, exp = _motor_com_fatos(["F09", "F28"])
        motor.encadeamento_para_tras("H4")

        self.assertIn("H4", motor.sessao["hypotheses_confirmed"])
        resposta = exp.como("H4")

        self.assertIn("H4", resposta)
        self.assertIn("R12", resposta)

    def test_como_multiplas_regras_para_mesma_hipotese(self):
        """
        Cenário: forward com F02+F19 (R14→H5) e F17+F19 (R15→H5).
        como("H5") deve citar R14 e R15.
        """
        motor, exp = _motor_com_fatos(["F02", "F19", "F17"])
        motor.encadeamento_para_frente()

        resposta = exp.como("H5")
        self.assertIn("R14", resposta)
        self.assertIn("R15", resposta)

    def test_como_hipotese_nao_confirmada(self):
        """Hipótese não confirmada → resposta de fallback, sem exceção."""
        with open(KB, encoding="utf-8") as f:
            base = json.load(f)
        exp = ExplicadorInferencia(base)
        resposta = exp.como("H7")
        self.assertIsInstance(resposta, str)
        self.assertGreater(len(resposta), 0)


class TestResumoSessao(unittest.TestCase):

    def test_resumo_contem_hipotese_e_regra(self):
        motor, exp = _motor_com_fatos(["F02", "F19"])
        motor.encadeamento_para_frente()

        resumo = exp.resumo_sessao()
        self.assertIn("H5", resumo)
        self.assertIn("R14", resumo)

    def test_resumo_sessao_vazia(self):
        """Sem nenhuma inferência o resumo não lança exceção."""
        with open(KB, encoding="utf-8") as f:
            base = json.load(f)
        exp = ExplicadorInferencia(base)
        resumo = exp.resumo_sessao()
        self.assertIsInstance(resumo, str)


class TestRetrocompatibilidade(unittest.TestCase):

    def test_motor_sem_explicador_nao_quebra(self):
        """Motor instanciado sem explicador deve funcionar normalmente."""
        motor = MotorInferencia(caminho_base=KB)
        motor.sessao["facts_confirmed"].update(["F02", "F19"])
        motor.encadeamento_para_frente()
        self.assertIn("H5", motor.sessao["hypotheses_confirmed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
