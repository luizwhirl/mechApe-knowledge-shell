"""
Interface CLI do Akinator — Questão 2.1 (P4)
Estética retro terminal fósforo verde, seguindo o padrão do MechApe.
"""

from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from akinator import Akinator

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
    print("║           Filmes · Séries · Cartoons · Animes                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(RESET)


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
            print(f"  {DIM}  Anotei '{nome_real}' para análise futura.{RESET}\n")
    return acertou


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


def jogar() -> None:
    """Laço principal: pergunta, atualiza o motor e palpita quando há convicção."""
    akinator = Akinator()
    total = len(akinator.all_characters)

    _cabecalho()
    _digitar("  Pense em um personagem fictício de filme, série, cartoon ou anime.")
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

    continuar = input(f"  {VERDE_BRILHANTE}Jogar novamente? [S/N]: {RESET}").strip().lower()
    if continuar in ("s", "sim"):
        print("\n" * 2)
        jogar()


if __name__ == "__main__":
    jogar()
