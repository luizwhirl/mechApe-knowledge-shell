"""
Testes automatizados do motor Akinator — Questão 2.1
Verifica a lógica de seleção de perguntas, pontuação probabilística e
identificação correta de personagens específicos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from q2.akinator import Akinator


def _simular_jogo(personagem_id: str, max_perguntas: int = 20) -> tuple[bool, int]:
    """
    Simula o motor jogando contra si mesmo: usa os atributos do personagem
    como oráculo de respostas e conta quantas perguntas foram necessárias.
    """
    a = Akinator()
    alvo = next(c for c in a.all_characters if c["id"] == personagem_id)

    while not (a.pode_adivinhar() or a.sem_candidatos() or a.perguntas_esgotadas()):
        attr = a.proxima_pergunta()
        if attr is None:
            break
        valor = alvo["attributes"].get(attr["id"])
        if valor is True:
            a.responder(attr["id"], "sim")
        elif valor is False:
            a.responder(attr["id"], "nao")
        else:
            a.responder(attr["id"], "nao_sei")

    palpite = a.melhor_palpite()
    acertou = palpite is not None and palpite["id"] == personagem_id
    return acertou, a.total_perguntas()


# --------------------------------------------------------------------------
# Testes de carga
# --------------------------------------------------------------------------

def test_carrega_personagens():
    a = Akinator()
    assert len(a.all_characters) == 35, "Deve haver 35 personagens"


def test_carrega_atributos():
    a = Akinator()
    assert len(a.attributes) == 23, "Deve haver 23 atributos"


def test_todos_personagens_tem_atributos_completos():
    a = Akinator()
    ids_esperados = {attr["id"] for attr in a.attributes}
    for c in a.all_characters:
        ids_presentes = set(c["attributes"].keys())
        faltando = ids_esperados - ids_presentes
        assert not faltando, f"{c['name']} não tem: {faltando}"


# --------------------------------------------------------------------------
# Testes de lógica de inferência probabilística
# --------------------------------------------------------------------------

def test_primeira_pergunta_tem_alta_entropia():
    """A primeira pergunta deve ter entropia ponderada > 0.9 (split equilibrado)."""
    a = Akinator()
    q = a.proxima_pergunta()
    assert q is not None
    entropia = a._entropia_ponderada(q["id"])
    assert entropia > 0.9, f"Entropia baixa ({entropia:.3f}) para {q['id']}"


def test_filtro_animado_elimina_corretos():
    """Após A04=sim, chars não-animados devem sair dos candidatos ativos."""
    a = Akinator()
    a.responder("A04", "sim")
    nomes = {c["name"] for c in a.candidates}
    assert "Batman" in nomes
    assert "Naruto Uzumaki" in nomes
    assert "Darth Vader" not in nomes
    assert "Jon Snow" not in nomes


def test_filtro_anime_restringe_a_japoneses():
    """Após A04=sim + A05=sim, apenas animes devem permanecer ativos."""
    a = Akinator()
    a.responder("A04", "sim")
    a.responder("A05", "sim")
    nomes = {c["name"] for c in a.candidates}
    assert "Naruto Uzumaki" in nomes
    assert "Son Goku" in nomes
    assert "Batman" not in nomes
    assert "Bob Esponja" not in nomes


def test_nao_sei_nao_filtra_candidatos():
    """Resposta 'não sei' não deve alterar os candidatos ativos."""
    a = Akinator()
    total_antes = len(a.candidates)
    a.responder("A01", "nao_sei")
    assert len(a.candidates) == total_antes


def test_reset_restaura_estado_inicial():
    """Após reset, todos os candidatos devem estar ativos novamente."""
    a = Akinator()
    a.responder("A04", "sim")
    a.responder("A05", "sim")
    assert len(a.candidates) < 35
    a.reset()
    assert len(a.candidates) == 35
    assert len(a.answered) == 0
    assert len(a.history) == 0


def test_scores_aumentam_com_respostas_corretas():
    """O personagem alvo deve ter score mais alto após respostas corretas."""
    a = Akinator()
    alvo = next(c for c in a.all_characters if c["id"] == "C01")  # Darth Vader
    score_antes = a.scores["C01"]
    # Responde corretamente: Vader não é animado (A04=false)
    a.responder("A04", "nao")
    assert a.scores["C01"] > a.scores["C11"], "Vader deve ter score maior que Batman após A04=nao"


def test_confianca_cresce_com_respostas():
    """A confiança no candidato top deve crescer a cada resposta relevante."""
    a = Akinator()
    conf0 = a.confianca_top()
    a.responder("A04", "nao")  # elimina metade dos candidatos
    conf1 = a.confianca_top()
    assert conf1 > conf0, "Confiança deve crescer após resposta discriminante"


# --------------------------------------------------------------------------
# Testes de identificação de personagens
# --------------------------------------------------------------------------

PERSONAGENS_ALVO = [
    "C01",  # Darth Vader
    "C02",  # Hermione Granger
    "C03",  # Tony Stark
    "C11",  # Batman
    "C16",  # Naruto
    "C17",  # Son Goku
    "C20",  # Light Yagami
    "C25",  # Saitama
    "C26",  # Thanos
    "C27",  # Spider-Man
    "C28",  # Gandalf
    "C33",  # L Lawliet
    "C34",  # Kakashi
    "C35",  # Mikasa
]


def test_identifica_personagens_alvo():
    resultados = []
    for pid in PERSONAGENS_ALVO:
        acertou, n_perguntas = _simular_jogo(pid)
        resultados.append((pid, acertou, n_perguntas))

    falhas = [(pid, n) for pid, ok, n in resultados if not ok]
    acertos = sum(1 for _, ok, _ in resultados if ok)
    media_perguntas = sum(n for _, _, n in resultados) / len(resultados)

    print(f"\n  Taxa de acerto: {acertos}/{len(PERSONAGENS_ALVO)} ({100*acertos/len(PERSONAGENS_ALVO):.0f}%)")
    print(f"  Média de perguntas: {media_perguntas:.1f}")
    for pid, n in falhas:
        nome = next(c["name"] for c in Akinator().all_characters if c["id"] == pid)
        print(f"  FALHA: {nome} ({n} perguntas)")

    assert not falhas, f"Falhou ao identificar: {falhas}"


def test_media_perguntas_razoavel():
    """Motor deve identificar qualquer personagem em no máximo 15 perguntas."""
    a_ref = Akinator()
    for c in a_ref.all_characters:
        acertou, n = _simular_jogo(c["id"])
        assert n <= 15, f"{c['name']} exigiu {n} perguntas (máximo esperado: 15)"
        assert acertou, f"Não identificou {c['name']} em {n} perguntas"


if __name__ == "__main__":
    testes = [
        test_carrega_personagens,
        test_carrega_atributos,
        test_todos_personagens_tem_atributos_completos,
        test_primeira_pergunta_tem_alta_entropia,
        test_filtro_animado_elimina_corretos,
        test_filtro_anime_restringe_a_japoneses,
        test_nao_sei_nao_filtra_candidatos,
        test_reset_restaura_estado_inicial,
        test_scores_aumentam_com_respostas_corretas,
        test_confianca_cresce_com_respostas,
        test_identifica_personagens_alvo,
        test_media_perguntas_razoavel,
    ]

    falhas = 0
    for t in testes:
        try:
            t()
            print(f"  OK  {t.__name__}")
        except AssertionError as e:
            print(f"  FALHA  {t.__name__}: {e}")
            falhas += 1
        except Exception as e:
            print(f"  ERRO  {t.__name__}: {e}")
            falhas += 1

    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram.")
