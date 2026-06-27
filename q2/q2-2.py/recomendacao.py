"""
Sistema de Recomendação Baseado em Ontologias
Questão 2.3 - Lista 1 de IA

Domínio: Filmes e Séries
Tecnologia: OWL 2.0 via Owlready2 + reasoner HermiT

A ontologia é construída por código (equivalente ao que se faria no Protégé),
o reasoner HermiT classifica indivíduos automaticamente, descobre relações
implícitas e verifica consistência. As recomendações usam tanto consultas
diretas quanto as inferências do reasoner.

Requisitos atendidos:
  - >=10 classes  (temos 16)
  - >=15 propriedades  (temos 8 de objeto + 8 de dados = 16)
  - hierarquia de classes (especialização/generalização)
  - restrições e axiomas (classes definidas por equivalência)
  - indivíduos suficientes (12 obras + gêneros + diretores + plataformas)
  - reasoner OWL 2.0 (HermiT): classificação, relações implícitas, consistência

  para rodar: 
  python recomendacao.py
"""

from owlready2 import *

# ============================================================
# 1. CRIAÇÃO DA ONTOLOGIA
# ============================================================

onto = get_ontology("http://exemplo.org/recomendacao_filmes.owl")

with onto:

    # ---------- HIERARQUIA DE CLASSES (generalização/especialização) ----------

    class Obra(Thing): pass                 # superclasse de tudo que é assistível
    class Filme(Obra): pass
    class Serie(Obra): pass

    class Genero(Thing): pass
    class Acao(Genero): pass
    class Drama(Genero): pass
    class Comedia(Genero): pass
    class FiccaoCientifica(Genero): pass
    class Terror(Genero): pass

    class Diretor(Thing): pass
    class Plataforma(Thing): pass
    class Publico(Thing): pass              # classificação indicativa
    class Livre(Publico): pass
    class Adulto(Publico): pass

    # ---------- PROPRIEDADES DE OBJETO (>=8) ----------

    class temGenero(ObjectProperty):
        domain = [Obra]; range = [Genero]

    class dirigidoPor(ObjectProperty):
        domain = [Obra]; range = [Diretor]

    class disponivelEm(ObjectProperty):
        domain = [Obra]; range = [Plataforma]

    class temClassificacao(ObjectProperty, FunctionalProperty):
        domain = [Obra]; range = [Publico]

    class similarA(ObjectProperty, SymmetricProperty):
        domain = [Obra]; range = [Obra]

    class dirigiu(ObjectProperty):
        domain = [Diretor]; range = [Obra]
        inverse_property = dirigidoPor       # relação inversa (inferida pelo reasoner)

    class recomendadoApos(ObjectProperty):
        domain = [Obra]; range = [Obra]

    class doMesmoDiretorQue(ObjectProperty, SymmetricProperty):
        domain = [Obra]; range = [Obra]

    # ---------- PROPRIEDADES DE DADOS (>=8 no total de propriedades) ----------

    class temTitulo(DataProperty, FunctionalProperty):
        domain = [Obra]; range = [str]

    class temAno(DataProperty, FunctionalProperty):
        domain = [Obra]; range = [int]

    class temNota(DataProperty, FunctionalProperty):
        domain = [Obra]; range = [float]

    class temDuracaoMin(DataProperty, FunctionalProperty):
        domain = [Filme]; range = [int]

    class numTemporadas(DataProperty, FunctionalProperty):
        domain = [Serie]; range = [int]

    class nomePessoa(DataProperty, FunctionalProperty):
        domain = [Diretor]; range = [str]

    class nomePlataforma(DataProperty, FunctionalProperty):
        domain = [Plataforma]; range = [str]

    class ehPremiado(DataProperty, FunctionalProperty):
        domain = [Obra]; range = [bool]

    # ---------- CLASSES DEFINIDAS (axiomas/restrições para o reasoner) ----------
    # Estas classes não recebem indivíduos diretamente: o HermiT classifica
    # automaticamente quais obras pertencem a elas (relações IMPLÍCITAS).

    class ObraAclamada(Obra):
        # obra com nota >= 8.5 (restrição em propriedade de dados)
        equivalent_to = [Obra & temNota.some(ConstrainedDatatype(float, min_inclusive=8.5))]

    class FilmeDeAcao(Filme):
        # filme que tem o gênero Ação (restrição existencial)
        equivalent_to = [Filme & temGenero.some(Acao)]

    class ObraParaMaratonar(Serie):
        # série com 3+ temporadas
        equivalent_to = [Serie & numTemporadas.some(ConstrainedDatatype(int, min_inclusive=3))]

    class RecomendacaoPremium(Obra):
        # obra aclamada E premiada
        equivalent_to = [Obra & ehPremiado.value(True)
                              & temNota.some(ConstrainedDatatype(float, min_inclusive=8.5))]


# ============================================================
# 2. POVOAMENTO (INDIVÍDUOS / INSTÂNCIAS)
# ============================================================

with onto:
    # Diretores
    nolan = Diretor("Nolan");          nolan.nomePessoa = "Christopher Nolan"
    villeneuve = Diretor("Villeneuve"); villeneuve.nomePessoa = "Denis Villeneuve"
    peele = Diretor("Peele");          peele.nomePessoa = "Jordan Peele"
    gilligan = Diretor("Gilligan");    gilligan.nomePessoa = "Vince Gilligan"
    waititi = Diretor("Waititi");      waititi.nomePessoa = "Taika Waititi"
    schur = Diretor("Schur");          schur.nomePessoa = "Michael Schur"

    # Plataformas
    netflix = Plataforma("Netflix");   netflix.nomePlataforma = "Netflix"
    prime = Plataforma("Prime");       prime.nomePlataforma = "Prime Video"
    max_ = Plataforma("Max");          max_.nomePlataforma = "Max"

    # Gêneros (instâncias)
    acao_i = Acao("g_acao")
    drama_i = Drama("g_drama")
    comedia_i = Comedia("g_comedia")
    ficcao_i = FiccaoCientifica("g_ficcao")
    terror_i = Terror("g_terror")

    livre_i = Livre("c_livre")
    adulto_i = Adulto("c_adulto")

    def novo_filme(id_, titulo, ano, nota, dur, generos, diretor, plats, classif, premiado):
        f = Filme(id_)
        f.temTitulo = titulo; f.temAno = ano; f.temNota = nota; f.temDuracaoMin = dur
        f.temGenero = generos; f.dirigidoPor = [diretor]; f.disponivelEm = plats
        f.temClassificacao = classif; f.ehPremiado = premiado
        return f

    def nova_serie(id_, titulo, ano, nota, temps, generos, diretor, plats, classif, premiado):
        s = Serie(id_)
        s.temTitulo = titulo; s.temAno = ano; s.temNota = nota; s.numTemporadas = temps
        s.temGenero = generos; s.dirigidoPor = [diretor]; s.disponivelEm = plats
        s.temClassificacao = classif; s.ehPremiado = premiado
        return s

    # 8 filmes + 4 séries = 12 obras
    inception   = novo_filme("Inception", "A Origem", 2010, 8.8, 148, [acao_i, ficcao_i], nolan, [netflix, prime], adulto_i, True)
    interstellar= novo_filme("Interstellar", "Interestelar", 2014, 8.7, 169, [drama_i, ficcao_i], nolan, [prime], livre_i, True)
    tenet       = novo_filme("Tenet", "Tenet", 2020, 7.3, 150, [acao_i, ficcao_i], nolan, [max_], adulto_i, False)
    dune        = novo_filme("Dune", "Duna", 2021, 8.0, 155, [acao_i, ficcao_i], villeneuve, [max_], livre_i, True)
    arrival     = novo_filme("Arrival", "A Chegada", 2016, 7.9, 116, [drama_i, ficcao_i], villeneuve, [netflix], livre_i, True)
    getout      = novo_filme("GetOut", "Corra!", 2017, 7.7, 104, [terror_i], peele, [netflix], adulto_i, True)
    nope        = novo_filme("Nope", "Não! Não Olhe!", 2022, 6.8, 130, [terror_i, ficcao_i], peele, [prime], adulto_i, False)
    us          = novo_filme("Us", "Nós", 2019, 6.8, 116, [terror_i], peele, [max_], adulto_i, False)

    breakingbad = nova_serie("BreakingBad", "Breaking Bad", 2008, 9.5, 5, [drama_i, acao_i], gilligan, [netflix], adulto_i, True)
    bettercall  = nova_serie("BetterCall", "Better Call Saul", 2015, 8.9, 6, [drama_i], gilligan, [netflix], adulto_i, True)
    westworld   = nova_serie("Westworld", "Westworld", 2016, 8.5, 4, [drama_i, ficcao_i], nolan, [max_], adulto_i, True)
    darkseries  = nova_serie("Dark", "Dark", 2017, 8.7, 3, [drama_i, ficcao_i], villeneuve, [netflix], adulto_i, True)

    # Comédias (para o gênero não ficar vazio)
    jojo        = novo_filme("Jojo", "Jojo Rabbit", 2019, 7.9, 108, [comedia_i, drama_i], waititi, [max_], livre_i, True)
    thor        = novo_filme("ThorRag", "Thor: Ragnarok", 2017, 7.9, 130, [comedia_i, acao_i], waititi, [prime], livre_i, False)
    goodplace   = nova_serie("GoodPlace", "The Good Place", 2016, 8.2, 4, [comedia_i], schur, [netflix], livre_i, True)
    brooklyn    = nova_serie("Brooklyn99", "Brooklyn Nine-Nine", 2013, 8.4, 8, [comedia_i], schur, [netflix], livre_i, False)

    # Algumas relações explícitas de similaridade (o reasoner propaga simetria)
    inception.similarA = [interstellar, tenet]
    dune.similarA = [arrival]
    breakingbad.similarA = [bettercall]
    goodplace.similarA = [brooklyn]
    jojo.similarA = [thor]


# ============================================================
# 3. RACIOCÍNIO (REASONER HermiT)
# ============================================================

def rodar_reasoner():
    print("Executando reasoner HermiT (classificação + consistência)...")
    with onto:
        sync_reasoner(infer_property_values=True)
    print("Ontologia consistente. Inferências aplicadas.\n")


# ============================================================
# 4. SISTEMA DE RECOMENDAÇÃO
# ============================================================

class Recomendador:
    def __init__(self, onto):
        self.onto = onto

    def por_genero(self, classe_genero):
        """Recomenda obras de um gênero (consulta semântica direta)."""
        return [o for o in self.onto.Obra.instances()
                if any(isinstance(g, classe_genero) for g in o.temGenero)]

    def aclamadas(self):
        """Usa a CLASSE INFERIDA pelo reasoner (nota >= 8.5)."""
        return list(self.onto.ObraAclamada.instances())

    def premium(self):
        """Classe inferida: aclamada E premiada."""
        return list(self.onto.RecomendacaoPremium.instances())

    def para_maratonar(self):
        """Classe inferida: séries com 3+ temporadas."""
        return list(self.onto.ObraParaMaratonar.instances())

    def do_mesmo_diretor(self, obra):
        """Relação implícita via propriedade inversa 'dirigiu'."""
        diretor = obra.dirigidoPor[0]
        return [o for o in diretor.dirigiu if o != obra]

    def similares(self, obra):
        """Inclui similaridade simétrica propagada pelo reasoner."""
        return list(obra.similarA)

    def recomendar(self, generos_preferidos=None, plataforma=None,
                   apenas_aclamadas=False, evitar_classif=None):
        """Recomendação combinando perfil do usuário + inferências."""
        candidatos = list(self.onto.Obra.instances())
        justificativas = {}

        resultado = []
        for o in candidatos:
            motivos = []
            ok = True

            if generos_preferidos:
                nomes_gen = {type(g).__name__ for g in o.temGenero}
                if nomes_gen & set(generos_preferidos):
                    motivos.append(f"gênero {nomes_gen & set(generos_preferidos)}")
                else:
                    ok = False

            if plataforma and ok:
                plats = {p.nomePlataforma for p in o.disponivelEm}
                if plataforma in plats:
                    motivos.append(f"disponível em {plataforma}")
                else:
                    ok = False

            if apenas_aclamadas and ok:
                if o in self.onto.ObraAclamada.instances():
                    motivos.append(f"aclamada (nota {o.temNota})")
                else:
                    ok = False

            if evitar_classif and ok:
                if o.temClassificacao and type(o.temClassificacao).__name__ == evitar_classif:
                    ok = False

            if ok:
                resultado.append((o, o.temNota or 0, motivos))

        resultado.sort(key=lambda x: x[1], reverse=True)
        return resultado


# ============================================================
# 5. DEMONSTRAÇÃO
# ============================================================

def titulo(o):
    return o.temTitulo or o.name

def demo():
    rodar_reasoner()
    rec = Recomendador(onto)

    print("=" * 60)
    print("  CLASSES INFERIDAS PELO REASONER (relações implícitas)")
    print("=" * 60)

    print("\n[Obras Aclamadas] (nota >= 8.5 — inferido, não declarado):")
    for o in rec.aclamadas():
        print(f"   - {titulo(o):20s} nota {o.temNota}")

    print("\n[Recomendação Premium] (aclamada E premiada — inferido):")
    for o in rec.premium():
        print(f"   - {titulo(o):20s} nota {o.temNota}")

    print("\n[Para Maratonar] (séries com 3+ temporadas — inferido):")
    for o in rec.para_maratonar():
        print(f"   - {titulo(o):20s} {o.numTemporadas} temporadas")

    print("\n" + "=" * 60)
    print("  RECOMENDAÇÃO POR PERFIL DO USUÁRIO")
    print("=" * 60)

    print("\nPerfil: gosta de Ficção Científica, na Netflix, só aclamadas")
    res = rec.recomendar(generos_preferidos=["FiccaoCientifica"],
                         plataforma="Netflix", apenas_aclamadas=True)
    if res:
        for o, nota, motivos in res:
            print(f"   * {titulo(o):20s} (nota {nota}) — {'; '.join(motivos)}")
    else:
        print("   (nenhuma obra atende todos os critérios)")

    print("\nPerfil: gosta de Terror, evita conteúdo Adulto")
    res = rec.recomendar(generos_preferidos=["Terror"], evitar_classif="Adulto")
    print(f"   {len(res)} resultado(s)" + (" — nenhum, pois todos os terrores da base são +18" if not res else ""))

    print("\n" + "=" * 60)
    print("  RECOMENDAÇÃO BASEADA EM RELAÇÕES (reasoner)")
    print("=" * 60)

    print(f"\nQuem viu 'A Origem' também pode gostar de (similaridade simétrica):")
    for o in rec.similares(onto.Inception):
        print(f"   - {titulo(o)}")

    print(f"\nDo mesmo diretor de 'Interestelar' (propriedade inversa inferida):")
    for o in rec.do_mesmo_diretor(onto.Interstellar):
        print(f"   - {titulo(o)}")

    # Salva a ontologia em .owl (entregável obrigatório)
    onto.save(file="recomendacao_filmes.owl", format="rdfxml")
    print("\n[Ontologia salva em recomendacao_filmes.owl]")


# ============================================================
# 6. MODO INTERATIVO (recebe informações do usuário)
# ============================================================

GENEROS_MENU = {
    "1": ("Acao", "Ação"),
    "2": ("Drama", "Drama"),
    "3": ("Comedia", "Comédia"),
    "4": ("FiccaoCientifica", "Ficção Científica"),
    "5": ("Terror", "Terror"),
}

PLATAFORMAS_MENU = {
    "1": ("Netflix", "Netflix"),
    "2": ("Prime Video", "Prime Video"),
    "3": ("Max", "Max"),
    "0": (None, "Qualquer plataforma"),
}


def perguntar_opcao(menu, prompt, permite_varios=False):
    print(prompt)
    for k, (_, label) in menu.items():
        print(f"   {k}) {label}")
    escolha = input("  > ").strip()
    if permite_varios:
        ids = [c.strip() for c in escolha.replace(",", " ").split()]
        return [menu[i][0] for i in ids if i in menu and menu[i][0]]
    return menu.get(escolha, (None, None))[0]


def modo_interativo():
    rec = Recomendador(onto)
    print("\n" + "=" * 60)
    print("  RECOMENDADOR DE FILMES E SÉRIES")
    print("  Monte seu perfil e receba recomendações.")
    print("=" * 60 + "\n")

    generos = perguntar_opcao(
        GENEROS_MENU,
        "Quais gêneros você gosta? (pode escolher vários, ex.: 1 4)",
        permite_varios=True,
    )

    print()
    plataforma = perguntar_opcao(
        PLATAFORMAS_MENU,
        "Em qual plataforma você assiste?",
    )

    print("\nQuer ver apenas obras aclamadas (nota >= 8.5)? (s/n)")
    apenas_aclamadas = input("  > ").strip().lower() in ("s", "sim")

    print("\nQuer evitar conteúdo adulto (+18)? (s/n)")
    evitar = "Adulto" if input("  > ").strip().lower() in ("s", "sim") else None

    res = rec.recomendar(
        generos_preferidos=generos if generos else None,
        plataforma=plataforma,
        apenas_aclamadas=apenas_aclamadas,
        evitar_classif=evitar,
    )

    print("\n" + "=" * 60)
    print("  RECOMENDAÇÕES PARA VOCÊ")
    print("=" * 60)
    if res:
        for o, nota, motivos in res:
            print(f"\n  * {titulo(o)}  (nota {nota})")
            print(f"     porque: {'; '.join(motivos)}")
            sims = rec.similares(o)
            if sims:
                print(f"     se gostar, veja também: {', '.join(titulo(s) for s in sims)}")
    else:
        print("\n  Nenhuma obra atende todos os critérios escolhidos.")
        # diagnóstico: relaxa um filtro de cada vez para mostrar o que pesou
        so_genero = rec.recomendar(generos_preferidos=generos if generos else None)
        print(f"  - Só pelo gênero escolhido: {len(so_genero)} obra(s).")
        if plataforma:
            sem_plat = rec.recomendar(generos_preferidos=generos if generos else None,
                                      apenas_aclamadas=apenas_aclamadas, evitar_classif=evitar)
            print(f"  - Ignorando a plataforma: {len(sem_plat)} obra(s).")
        if apenas_aclamadas:
            sem_acl = rec.recomendar(generos_preferidos=generos if generos else None,
                                     plataforma=plataforma, evitar_classif=evitar)
            print(f"  - Sem exigir 'aclamada': {len(sem_acl)} obra(s).")
        if evitar:
            sem_ev = rec.recomendar(generos_preferidos=generos if generos else None,
                                    plataforma=plataforma, apenas_aclamadas=apenas_aclamadas)
            print(f"  - Permitindo +18: {len(sem_ev)} obra(s).")
        print("  Tente afrouxar o filtro que está zerando os resultados.")
    print()


def menu_principal():
    rodar_reasoner()   # roda o reasoner uma vez no início
    while True:
        print("\n" + "=" * 60)
        print("  MENU")
        print("=" * 60)
        print("  1) Receber recomendações (modo interativo)")
        print("  2) Ver demonstração automática (inferências do reasoner)")
        print("  3) Sair")
        op = input("  > ").strip()
        if op == "1":
            modo_interativo()
        elif op == "2":
            demo_sem_reasoner()
        elif op == "3":
            print("  Até logo!")
            break
        else:
            print("  Opção inválida.")


def demo_sem_reasoner():
    """Mostra as inferências sem rodar o reasoner de novo (já foi rodado)."""
    rec = Recomendador(onto)
    print("\n[Obras Aclamadas] (nota >= 8.5 — inferido):")
    for o in rec.aclamadas():
        print(f"   - {titulo(o):20s} nota {o.temNota}")
    print("\n[Para Maratonar] (séries com 3+ temporadas — inferido):")
    for o in rec.para_maratonar():
        print(f"   - {titulo(o):20s} {o.numTemporadas} temporadas")
    print("\nDo mesmo diretor de 'Interestelar' (propriedade inversa inferida):")
    for o in rec.do_mesmo_diretor(onto.Interstellar):
        print(f"   - {titulo(o)}")
    onto.save(file="recomendacao_filmes.owl", format="rdfxml")
    print("\n[Ontologia salva em recomendacao_filmes.owl]")


if __name__ == "__main__":
    menu_principal()