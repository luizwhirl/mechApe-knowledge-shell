"""
Interface CLI do Akinator — Questão 2.1 (P4)
Estética retro terminal fósforo verde, seguindo o padrão do MechApe.
"""

from __future__ import annotations
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from akinator import Akinator

SUGESTOES_PATH = Path(__file__).resolve().parent / "sugestoes_personagens.json"

# -- Paleta ANSI -----------------------------------------------------------
VERDE         = "\033[0;32m"
VERDE_BRILHANTE = "\033[1;32m"
AMARELO       = "\033[1;33m"
VERMELHO      = "\033[0;31m"
CYAN          = "\033[0;36m"
REVERSO       = "\033[7m"
DIM           = "\033[2m"
RESET         = "\033[0m"


def _digitar(texto: str, cor: str = VERDE, atraso: float = 0.008) -> None:
    for c in texto:
        sys.stdout.write(cor + c + RESET)
        sys.stdout.flush()
        time.sleep(atraso)
    print()


def _cabecalho() -> None:
    print(VERDE_BRILHANTE)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   █████╗ ██╗  ██╗██╗███╗  ██╗ █████╗ ████████╗ ██████╗ ██████╗ ║")
    print("║  ██╔══██╗██║ ██╔╝██║████╗ ██║██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗║")
    print("║  ███████║█████╔╝ ██║██╔██╗██║███████║   ██║   ██║   ██║██████╔╝║")
    print("║  ██╔══██║██╔═██╗ ██║██║╚████║██╔══██║   ██║   ██║   ██║██╔══██╗║")
    print("║  ██║  ██║██║  ██╗██║██║ ╚███║██║  ██║   ██║   ╚██████╔╝██║  ██║║")
    print("║  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║      MECHAPE — IDENTIFICADOR DE PERSONAGENS FICTÍCIOS  v2.0     ║")
    print("║           Filmes · Séries · Cartoons · Animes · Jogos            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(RESET)


def _listar_personagens() -> None:
    """Mostra todos os personagens da base, agrupados por tipo, para consulta rápida."""
    akinator = Akinator()
    por_tipo: dict[str, list[str]] = {}
    for c in akinator.all_characters:
        por_tipo.setdefault(c["type"], []).append(c["name"])

    print()
    print(f"  {VERDE_BRILHANTE}{'═' * 68}{RESET}")
    print(f"  {VERDE_BRILHANTE}PERSONAGENS DISPONÍVEIS NA BASE ({len(akinator.all_characters)}){RESET}")
    print(f"  {VERDE_BRILHANTE}{'═' * 68}{RESET}")

    for tipo in sorted(por_tipo):
        nomes = sorted(por_tipo[tipo])
        print(f"\n  {CYAN}{tipo.upper()} ({len(nomes)}){RESET}")
        for i in range(0, len(nomes), 2):
            linha = nomes[i:i + 2]
            print("    " + "".join(f"{VERDE}- {n:<32}{RESET}" for n in linha))

    print(f"\n  {VERDE_BRILHANTE}{'═' * 68}{RESET}")
    input(f"\n  {VERDE_BRILHANTE}[ PRESSIONE ENTER PARA VOLTAR AO MENU ]{RESET}")


def _mostrar_menu() -> str:
    print(f"  {VERDE_BRILHANTE}1. INICIAR NOVA PARTIDA{RESET}")
    print(f"  {VERDE}2. VER PERSONAGENS DISPONÍVEIS{RESET}")
    print(f"  {VERDE}0. SAIR{RESET}\n")
    return input(f"  {VERDE_BRILHANTE}Selecione uma opção: {RESET}").strip()


def _barra_candidatos(atual: int, total: int) -> str:
    eliminados = total - atual
    pct = eliminados / total if total > 0 else 0
    barras = int(pct * 32)
    barra = "█" * barras + "░" * (32 - barras)
    return f"{CYAN}[{barra}]{RESET} {VERDE}{atual}/{total} candidatos{RESET}"


def _pergunta_usuario(pergunta: str) -> str:
    """Solicita resposta (S/N/?) e retorna 'sim', 'nao' ou 'nao_sei'."""
    while True:
        print(f"  {VERDE_BRILHANTE}▶  {pergunta}{RESET}")
        r = input(f"  {VERDE}[S = Sim | N = Não | ? = Não sei]: {RESET}").strip().lower()
        if r in ("s", "sim"):
            return "sim"
        if r in ("n", "nao", "não"):
            return "nao"
        if r in ("?", "ns", "nao sei", "não sei"):
            return "nao_sei"
        print(f"  {AMARELO}  → Resposta inválida. Use S, N ou ?.{RESET}\n")


def _fazer_palpite(akinator: Akinator, palpite: dict) -> bool:
    """Apresenta o palpite. Retorna True se acertou."""
    nome    = palpite["name"]
    origem  = palpite["origin"]
    tipo    = palpite["type"].upper()
    desc    = palpite["description"]
    conf    = akinator.confianca_top()

    print()
    print(f"  {VERDE_BRILHANTE}{'═' * 64}{RESET}")
    _digitar("  Analisando padrões...  Cheguei à minha conclusão!", atraso=0.02)
    time.sleep(0.4)
    print()
    print(f"  {REVERSO}  ►  {nome}  ◄  {RESET}")
    print(f"  {CYAN}  Origem    : {origem}  [{tipo}]{RESET}")
    print(f"  {CYAN}  Confiança : {conf:.0%}{RESET}")
    print(f"  {DIM}  {desc}{RESET}")
    print(f"  {VERDE_BRILHANTE}{'═' * 64}{RESET}")
    print()

    r = input(f"  {VERDE_BRILHANTE}Acertei? [S/N]: {RESET}").strip().lower()
    acertou = r in ("s", "sim")

    if acertou:
        print(f"\n  {VERDE_BRILHANTE}██  ACERTO!  A mente não falha.  ██{RESET}\n")
    else:
        print(f"\n  {AMARELO}  Errei desta vez...{RESET}")
        nome_real = input(f"  {VERDE}Quem era o personagem? {RESET}").strip()
        if nome_real:
            _registrar_erro(akinator, nome_real)
    return acertou


def _palavras(texto: str) -> set[str]:
    return set(re.findall(r"[a-zà-ÿ0-9]+", texto.lower()))


def _buscar_personagem(akinator: Akinator, nome: str) -> dict | None:
    """Procura por nome completo ou por palavras inteiras (evita falso positivo tipo 'man' -> Mandalorian)."""
    alvo = nome.strip().lower()
    alvo_palavras = _palavras(nome)
    for c in akinator.all_characters:
        nome_c = c["name"].lower()
        if alvo == nome_c:
            return c
        if alvo_palavras and alvo_palavras.issubset(_palavras(c["name"])):
            return c
    return None


def _registrar_erro(akinator: Akinator, nome_real: str) -> None:
    """
    Dá utilidade ao erro relatado: se o personagem já está na base, mostra
    quais respostas da sessão conflitaram com os atributos reais dele (o
    motivo provável da confusão). Se não está, registra a sugestão em
    disco para uma futura expansão da base — igual ao Akinator de verdade.
    """
    conhecido = _buscar_personagem(akinator, nome_real)

    if conhecido:
        perguntas = {a["id"]: a["question"] for a in akinator.attributes}
        divergencias = [
            (perguntas[aid], resposta, conhecido["attributes"].get(aid))
            for aid, resposta in akinator.answered.items()
            if resposta is not None and resposta != conhecido["attributes"].get(aid)
        ]
        print(f"  {DIM}  '{conhecido['name']}' já está na base. Respostas que confundiram o motor:{RESET}")
        if divergencias:
            for pergunta, dado, esperado in divergencias:
                dado_txt = "Sim" if dado else "Não"
                esperado_txt = "Sim" if esperado else "Não"
                print(f"  {DIM}    - \"{pergunta}\" você disse {dado_txt}, o esperado era {esperado_txt}.{RESET}")
        else:
            print(f"  {DIM}    Suas respostas batiam com a base — foi só concorrência com outro candidato.{RESET}")
    else:
        _salvar_sugestao(nome_real, akinator)
        print(f"  {DIM}  '{nome_real}' não está na base. Registrei a sugestão em {SUGESTOES_PATH.name} para expansão futura.{RESET}")
    print()


def _salvar_sugestao(nome_real: str, akinator: Akinator) -> None:
    """Acrescenta o personagem sugerido (com o histórico de respostas) ao log de sugestões."""
    sugestoes = []
    if SUGESTOES_PATH.exists():
        try:
            sugestoes = json.loads(SUGESTOES_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            sugestoes = []
    sugestoes.append({
        "nome": nome_real,
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
        "respostas": akinator.answered,
    })
    SUGESTOES_PATH.write_text(json.dumps(sugestoes, ensure_ascii=False, indent=2), encoding="utf-8")


def _mostrar_estatisticas(akinator: Akinator, acertou: bool) -> None:
    total = len(akinator.all_characters)
    perguntas = akinator.total_perguntas()
    restantes = len(akinator.candidates)

    print(f"  {VERDE}{'─' * 40}{RESET}")
    print(f"  {VERDE}Perguntas feitas  : {perguntas}{RESET}")
    print(f"  {VERDE}Candidatos finais : {restantes}/{total}{RESET}")
    resultado = f"{VERDE_BRILHANTE}ACERTO{RESET}" if acertou else f"{VERMELHO}ERRO{RESET}"
    print(f"  {VERDE}Resultado         : {resultado}")
    print(f"  {VERDE}{'─' * 40}{RESET}\n")


def _rodar_partida() -> None:
    """Executa uma partida: pergunta, atualiza o motor e palpita quando há convicção."""
    akinator = Akinator()
    total = len(akinator.all_characters)

    print()
    _digitar("  Pense em um personagem fictício de filme, série, cartoon, anime ou jogo.")
    _digitar("  Responderei com Sim, Não ou Não Sei a cada pergunta.\n", atraso=0.006)
    input(f"  {VERDE_BRILHANTE}[ PRESSIONE ENTER QUANDO ESTIVER PRONTO ]{RESET}")
    print()

    acertou = False

    while True:
        if akinator.pode_adivinhar():
            acertou = _fazer_palpite(akinator, akinator.melhor_palpite())
            break

        if akinator.sem_candidatos():
            print(f"\n  {VERMELHO}  Respostas contraditórias — você me venceu!{RESET}\n")
            break

        attr = akinator.proxima_pergunta()
        if attr is None or akinator.perguntas_esgotadas():
            # Sem perguntas úteis: arrisca o melhor palpite em vez de desistir.
            palpite = akinator.melhor_palpite()
            if palpite:
                print(f"\n  {AMARELO}  Sem mais perguntas. Minha melhor aposta:{RESET}")
                acertou = _fazer_palpite(akinator, palpite)
            break

        cands = len(akinator.candidates)
        print(f"  {_barra_candidatos(cands, total)}")

        # Exibe a hipótese atual mais provável a cada rodada (requisito da questão).
        confianca = akinator.confianca_top()
        top3 = akinator.top_n(min(3, cands))
        nomes = ", ".join(c["name"].split(" ")[0] for c, _ in top3)
        print(f"  {DIM}  Hipótese atual: {nomes}  ({confianca:.0%}){RESET}")

        print(f"  {DIM}  Pergunta #{akinator.total_perguntas() + 1}{RESET}\n")

        resposta = _pergunta_usuario(attr["question"])
        akinator.responder(attr["id"], resposta)
        print()

    _mostrar_estatisticas(akinator, acertou)
    input(f"  {VERDE_BRILHANTE}[ PRESSIONE ENTER PARA VOLTAR AO MENU ]{RESET}")


def jogar() -> None:
    """Loop principal: exibe o menu e direciona para uma partida, a lista de personagens ou a saída."""
    while True:
        _cabecalho()
        opcao = _mostrar_menu()

        if opcao == "1":
            _rodar_partida()
        elif opcao == "2":
            _listar_personagens()
        elif opcao == "0":
            print(f"\n  {VERDE}Até a próxima!{RESET}\n")
            break
        else:
            print(f"\n  {AMARELO}  Opção inválida.{RESET}")
            time.sleep(0.8)


if __name__ == "__main__":
    jogar()
