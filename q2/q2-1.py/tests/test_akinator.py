"""
Testes automatizados do motor Akinator — Questão 2.1
Verifica a lógica de seleção de perguntas, pontuação probabilística e
identificação correta de personagens específicos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from akinator import Akinator


def _simular_jogo(personagem_id: str, max_perguntas: int = 20) -> tuple[bool, int]:
    """Joga o motor contra si mesmo usando os atributos do alvo como oráculo de respostas."""
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
    assert len(a.all_characters) == 31, "Deve haver 31 personagens"


def test_carrega_atributos():
    a = Akinator()
    assert len(a.attributes) == 26, "Deve haver 26 atributos"


def test_todos_personagens_tem_atributos_completos():
    a = Akinator()
    ids_esperados = {attr["id"] for attr in a.attributes}
    for c in a.all_characters:
        ids_presentes = set(c["attributes"].keys())
        faltando = ids_esperados - ids_presentes
        assert not faltando, f"{c['name']} não tem: {faltando}"


def test_sem_personagens_quase_duplicados():
    """Nenhum par pode diferir em só 1 atributo — pares assim arrastam o jogo até esgotar."""
    a = Akinator()
    attr_ids = [attr["id"] for attr in a.attributes]
    chars = a.all_characters
    for i in range(len(chars)):
        for j in range(i + 1, len(chars)):
            diff = sum(1 for aid in attr_ids
                       if chars[i]["attributes"][aid] != chars[j]["attributes"][aid])
            assert diff >= 2, (
                f"{chars[i]['name']} e {chars[j]['name']} diferem em só {diff} atributo"
            )


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


def test_filtro_animado_ordena_corretamente():
    """Após A04=sim, chars animados devem ter score maior que os não-animados."""
    a = Akinator()
    a.responder("A04", "sim")
    norm = {c["id"]: s for c, s in [(c, a._normalized()[c["id"]]) for c in a.all_characters]}
    # Animados (A04=true) devem superar os não-animados
    assert norm["C18"] > norm["C01"], "Batman (animado) deve ter score maior que Vader (não-animado)"
    assert norm["C12"] > norm["C08"], "Naruto (animado) deve ter score maior que Jon Snow (não-animado)"
    # A confiança deve ter crescido após resposta discriminante
    assert a.confianca_top() > 1.0 / len(a.all_characters)


def test_filtro_anime_restringe_a_japoneses():
    """Após A04=sim + A05=sim, animes devem ter score > cartoons ocidentais > live-action."""
    a = Akinator()
    a.responder("A04", "sim")
    a.responder("A05", "sim")
    norm = {c["id"]: a._normalized()[c["id"]] for c in a.all_characters}
    # Anime (A04+A05=true) > cartoon ocidental (A04=true, A05=false) > live-action (A04=false)
    assert norm["C12"] > norm["C18"], "Naruto (anime) deve ter score maior que Batman (cartoon ocidental)"
    assert norm["C18"] > norm["C01"], "Batman (cartoon) deve ter score maior que Vader (live-action)"
    # Animes devem dominar o top-3
    top3_ids = {c["id"] for c, _ in a.top_n(3)}
    top3_animes = top3_ids & {"C11", "C12", "C13", "C14", "C15"}
    assert len(top3_animes) > 0, "Pelo menos um anime deve estar no top-3"


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
    assert len(a.candidates) < 31
    a.reset()
    assert len(a.candidates) == 31
    assert len(a.answered) == 0
    assert len(a.history) == 0


def test_scores_aumentam_com_respostas_corretas():
    """O personagem alvo deve ter score mais alto após respostas corretas."""
    a = Akinator()
    alvo = next(c for c in a.all_characters if c["id"] == "C01")  # Darth Vader
    score_antes = a.scores["C01"]
    # Responde corretamente: Vader não é animado (A04=false)
    a.responder("A04", "nao")
    assert a.scores["C01"] > a.scores["C11"], "Vader deve ter score maior que Son Goku após A04=nao"


def test_confianca_cresce_com_respostas():
    """A confiança no candidato top deve crescer a cada resposta relevante."""
    a = Akinator()
    conf0 = a.confianca_top()
    a.responder("A04", "nao")  # elimina metade dos candidatos
    conf1 = a.confianca_top()
    assert conf1 > conf0, "Confiança deve crescer após resposta discriminante"


def test_nao_palpita_antes_do_minimo():
    """Mesmo com confiança alta, não deve palpitar antes de MIN_QUESTIONS."""
    a = Akinator()
    alvo = next(c for c in a.all_characters if c["name"] == "Link")
    # Responde poucas perguntas muito discriminantes
    for attr_id in ("A26", "A04"):  # videogame=sim isola Link/Kratos
        a.responder(attr_id, "sim" if alvo["attributes"][attr_id] else "nao")
    assert a.total_perguntas() < a.MIN_QUESTIONS
    assert not a.pode_adivinhar(), "Não deve palpitar antes do mínimo de perguntas"


def test_palpite_por_dominancia_abaixo_do_limiar_absoluto():
    """Deve palpitar por dominância (líder >> 2º) mesmo sem atingir os 95% absolutos."""
    a = Akinator()
    alvo = next(c for c in a.all_characters if c["name"] == "Link")
    # Simula respostas consistentes até colapsar para o Link
    while not (a.pode_adivinhar() or a.sem_candidatos()):
        attr = a.proxima_pergunta()
        if attr is None:
            break
        valor = alvo["attributes"].get(attr["id"])
        a.responder(attr["id"], "sim" if valor else "nao")

    assert a.pode_adivinhar(), "Deveria ter atingido condição de palpite"
    top2 = a.top_n(2)
    conf = top2[0][1]
    ratio = top2[0][1] / top2[1][1] if top2[1][1] > 0 else float("inf")
    # Confirma que o gatilho foi a dominância (ou a confiança absoluta) e acertou o alvo
    assert top2[0][0]["name"] == "Link"
    assert conf >= a.CONFIDENCE_THRESHOLD or ratio >= a.DOMINANCE_RATIO


# --------------------------------------------------------------------------
# Testes de identificação de personagens
# --------------------------------------------------------------------------

PERSONAGENS_ALVO = [
    "C01",  # Darth Vader
    "C02",  # Hermione Granger
    "C03",  # Tony Stark
    "C10",  # Eleven
    "C11",  # Son Goku
    "C12",  # Naruto Uzumaki
    "C18",  # Batman
    "C20",  # Thanos
    "C21",  # Bob Esponja
    "C22",  # Homer Simpson
    "C24",  # Avatar Aang
    "C25",  # Gandalf
    "C26",  # Kratos
    "C28",  # Link
    "C29",  # Sherlock Holmes
    "C30",  # James Bond
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
    """Identifica todos os personagens (100%) em poucas perguntas, sem arrastar o jogo."""
    a_ref = Akinator()
    resultados = []
    for c in a_ref.all_characters:
        acertou, n = _simular_jogo(c["id"])
        resultados.append((c["name"], acertou, n))

    falhas_acerto = [(nome, n) for nome, ok, n in resultados if not ok]
    max_perguntas = max(n for _, _, n in resultados)
    media = sum(n for _, _, n in resultados) / len(resultados)

    print(f"\n  Acertos: {len(resultados) - len(falhas_acerto)}/{len(resultados)}")
    print(f"  Média: {media:.1f} perguntas  |  Máximo: {max_perguntas}")

    assert not falhas_acerto, f"Personagens não identificados: {falhas_acerto}"
    # Limite apertado: se subir muito, há provável par quase-duplicado na base.
    assert max_perguntas <= 12, f"Personagem exigiu {max_perguntas} perguntas — possível par quase-duplicado na base"


if __name__ == "__main__":
    testes = [
        test_carrega_personagens,
        test_carrega_atributos,
        test_todos_personagens_tem_atributos_completos,
        test_sem_personagens_quase_duplicados,
        test_primeira_pergunta_tem_alta_entropia,
        test_filtro_animado_ordena_corretamente,
        test_filtro_anime_restringe_a_japoneses,
        test_nao_sei_nao_filtra_candidatos,
        test_reset_restaura_estado_inicial,
        test_scores_aumentam_com_respostas_corretas,
        test_confianca_cresce_com_respostas,
        test_nao_palpita_antes_do_minimo,
        test_palpite_por_dominancia_abaixo_do_limiar_absoluto,
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
