"""
Interface com o Usuário do MechApe - Módulo 5 (P3)
Estética Retrô PC Anos 80 / Terminal ASCII
"""

from __future__ import annotations
import sys
import time
from pathlib import Path

# Garante a importação correta dos módulos locais
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from motor_inferencia import MotorInferencia
from q1.explicador import ExplicadorInferencia

# Cores ANSI para estética fósforo verde de terminal antigo
VERDE = "\033[0;32m"
VERDE_BRILHANTE = "\033[1;32m"
REVERSE = "\033[7m"
RESET = "\033[0m"

def print_retro(texto: str, atraso: float = 0.005, nova_linha: bool = True):
    """Imprime o texto com um leve efeito de digitação de terminal antigo."""
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(atraso)
    if nova_linha:
        print()

def exibir_cabecalho():
    print(VERDE)
    print("============================================================")
    print(" ███▄ ▄███▓▓█████  ▄████▄   ██░ ██  ▄▄▄       ██▓███  ▓█████ ")
    print(" ▓██▒▀█▀ ██▒▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒▒████▄    ▓██░  ██▒▓█   ▀ ")
    print(" ▓██    ▓██░▒███   ▒▓█    ▄ ▒██▀▀██░▒██  ▀█▄  ▓██░ ██▓▒▒███   ")
    print(" ▒██    ▒██ ▒▓█  ▄ ▒▓▓▄ ▄██▒░██ ░██ ░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓█  ▄ ")
    print(" ▒██▒   ░██▒░▒████▒▒ ▓███▀ ░░██ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░░▒████▒")
    print(" ░ ▒░   ░  ░░░ ▒░ ░░ ░▒ ▒  ░░ ▒ ░▒░ ░▒▒   ▓▒█░▒▓ ░      ░░ ▒░ ░")
    print("============================================================")
    print("      MECHAPE KNOWLEDGE SYSTEM - OS VERSION 2026.06         ")
    print("============================================================")
    print(RESET)

def executar_consulta():
    # Instancia o motor carregando a base de testes criada pelo P2
    caminho_kb = ROOT / "q1" / "tests" / "knowledge_base.json"
    
    # Criamos o explicador e acoplamos ao motor
    motor = MotorInferencia(caminho_base=str(caminho_kb))
    explicador = ExplicadorInferencia(motor)
    
    print_retro(f"\n{VERDE}[SISTEMA]: Inicializando matriz de inferência híbrida...{RESET}")
    time.sleep(0.5)

    # Coleta de todos os fatos interativos disponíveis na base que necessitam de input do usuário
    fatos_usuario = [f for f in motor.base["facts"]["items"] if f["source"] == "user_input"]
    
    print_retro(f"{VERDE}[SISTEMA]: Responda às perguntas com (S)im, (N)ão ou solicite ajuda.{RESET}\n")

    for fato in fatos_usuario:
        fato_id = fato["id"]
        pergunta = fato["question"]
        
        while True:
            # Layout de prompt clássico de sistema operacional antigo
            print(f"{VERDE_BRILHANTE}■ {pergunta}{RESET}")
            resposta = input(f"{VERDE}[S/N/? para 'Por quê?']: {RESET}").strip().lower()
            
            if resposta in ['s', 'sim']:
                motor.sessao["facts_confirmed"].add(fato_id)
                break
            elif resposta in ['n', 'nao', 'não']:
                motor.sessao["facts_denied"].add(fato_id)
                break
            elif resposta in ['?', 'por que', 'por quê']:
                print(f"\n{REVERSE}  MECANISMO DE EXPLICAÇÃO: 'POR QUÊ?'  {RESET}")
                # O por_que() busca qual regra/hipótese usaria esse fato
                print_retro(f"{VERDE}{explicador.por_que(fato_id)}{RESET}\n")
            else:
                print(f"{VERDE}[AVISO]: Entrada inválida. Use S, N ou ?{RESET}\n")
        
        # Roda a inferência para frente parcial com os dados fornecidos até aqui
        motor.encadeamento_para_frente()
        
        # Se uma hipótese final já foi confirmada, podemos encerrar mais cedo (Otimização)
        if motor.sessao["hypotheses_confirmed"]:
            break

    # Se terminou as perguntas e não disparou via forward, avalia os alvos via backward
    if not motor.sessao["hypotheses_confirmed"]:
        hipoteses_totais = [h["id"] for h in motor.base["hypotheses"]["items"]]
        for h_id in hipoteses_totais:
            motor.encadeamento_para_tras(h_id)
            if motor.sessao["hypotheses_confirmed"]:
                break

    # Exibição dos Resultados Finais
    print_retro(f"\n{VERDE}============================================================{RESET}")
    print_retro(f"{VERDE_BRILHANTE}>> PROCESSO DE DIAGNÓSTICO CONCLUÍDO <<{RESET}")
    print_retro(f"{VERDE}============================================================{RESET}")
    
    hipoteses_confirmadas = motor.sessao["hypotheses_confirmed"]
    
    if hipoteses_confirmadas:
        for hip_id in hipoteses_confirmadas:
            hipotese_dados = next(h for h in motor.base["hypotheses"]["items"] if h["id"] == hip_id)
            print(f"\n{VERDE_BRILHANTE}DIAGNÓSTICO DETECTADO: {hipotese_dados['label']} ({hip_id}){RESET}")
            print_retro(f"{VERDE}DESCRIÇÃO: {hipotese_dados['description']}{RESET}")
            print_retro(f"{VERDE_BRILHANTE}RECOMENDAÇÃO TÉCNICA: {hipotese_dados['recommendation']}{RESET}\n")
            
            # Pergunta se deseja o detalhamento do "Como?"
            ver_como = input(f"{VERDE}Deseja inspecionar o encadeamento lógico de regras ('Como?')? [S/N]: {RESET}").strip().lower()
            if ver_como in ['s', 'sim']:
                print(f"\n{REVERSE}  MECANISMO DE EXPLICAÇÃO: 'COMO?'  {RESET}")
                print_retro(f"{VERDE}{explicador.como(hip_id)}{RESET}\n")
    else:
        print_retro(f"\n{VERDE_BRILHANTE}[RESULTADO]: Nenhuma hipótese conhecida pôde ser comprovada com os fatos fornecidos.{RESET}\n")

    # Exibe resumo da sessão
    print(f"{VERDE}------------------------------------------------------------{RESET}")
    print_retro(f"{VERDE}{explicador.resumo_sessao()}{RESET}")
    print(f"{VERDE}------------------------------------------------------------{RESET}")
    input(f"\n{VERDE}Pressione [ENTER] para retornar ao menu principal...{RESET}")

def menu_principal():
    while True:
        sys.stdout.write("\033[H\033[2J") # Limpa a tela do terminal de forma limpa
        exibir_cabecalho()
        print(f"{VERDE_BRILHANTE}  1. INICIAR NOVA CONSULTA DIAGNÓSTICA{RESET}")
        print(f"{VERDE}  2. EXIBIR CRÉDITOS DO SISTEMA OPERACIONAL{RESET}")
        print(f"{VERDE}  0. DESLIGAR TERMINAL (SAIR){RESET}\n")
        
        opcao = input(f"{VERDE}SELECIONE UMA OPÇÃO COGNITIVA_> {RESET}").strip()
        
        if opcao == "1":
            executar_consulta()
        elif opcao == "2":
            print(f"\n{VERDE}SISTEMA DESENVOLVIDO PELA EQUIPE MECHAPE (IA 2026.1):{RESET}")
            print_retro(f"{VERDE}  • Arquitetura & Motor (P1): Manu")
            print_retro(f"{VERDE}  • Base de Dados & Editor (P2): Indias")
            print_retro(f"{VERDE}  • Interface & Explicação (P3): João Felipe")
            print_retro(f"{VERDE}  • Diagnósticos Específicos (P4/P5): Lucas & Rayssa{RESET}\n")
            input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")
        elif opcao == "0":
            print_retro(f"\n{VERDE}[SISTEMA]: Finalizando buffers... Desligando. Adeus.{RESET}")
            break
        else:
            print(f"{VERDE}[ERRO]: Código de instrução inválido.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print(f"\n{VERDE}[SISTEMA]: Interrupção forçada pelo operador. Encerrando.{RESET}")