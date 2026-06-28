"""
Interface com o Usuário do MechApe - Módulo 5 (P3)
Estética Retrô PC Anos 80 / Terminal ASCII
Integração com Motor de Inferência (P1) e Editor de Base (P2)
"""

from __future__ import annotations
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from q1.motor_inferencia import MotorInferencia
from q1.explicador import ExplicadorInferencia

from q1.editor_base_conhecimento import KnowledgeBaseEditor, run_interactive

VERDE = "\033[0;32m"
VERDE_BRILHANTE = "\033[1;32m"
REVERSE = "\033[7m"
RESET = "\033[0m"

CAMINHO_KB = ROOT / "q1" / "tests" / "knowledge_base.json"

def print_retro(texto: str, atraso: float = 0.005, nova_linha: bool = True):
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
    print("      MECHAPE KNOWLEDGE SYSTEM - OS VERSION 1986.06         ")
    print("============================================================")
    print(RESET)

def executar_consulta():
    motor = MotorInferencia(caminho_base=str(CAMINHO_KB))
    explicador = ExplicadorInferencia(motor)
    
    print_retro(f"\n{VERDE}[SISTEMA]: Inicializando matriz de inferência híbrida...{RESET}")
    time.sleep(0.5)

    fatos_usuario = [f for f in motor.base["facts"]["items"] if f["source"] == "user_input"]
    print_retro(f"{VERDE}[SISTEMA]: Responda às perguntas com (S)im, (N)ão ou solicite ajuda (?){RESET}\n")

    for fato in fatos_usuario:
        fato_id = fato["id"]
        pergunta = fato["question"]
        
        while True:
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
                print_retro(f"{VERDE}{explicador.por_que(fato_id)}{RESET}\n")
            else:
                print(f"{VERDE}[AVISO]: Entrada inválida. Use S, N ou ?{RESET}\n")
        
        motor.encadeamento_para_frente()
        if motor.sessao["hypotheses_confirmed"]:
            break

    if not motor.sessao["hypotheses_confirmed"]:
        hipoteses_totais = [h["id"] for h in motor.base["hypotheses"]["items"]]
        for h_id in hipoteses_totais:
            motor.encadeamento_para_tras(h_id)
            if motor.sessao["hypotheses_confirmed"]:
                break

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
            
            ver_como = input(f"{VERDE}Deseja inspecionar o encadeamento lógico de regras ('Como?')? [S/N]: {RESET}").strip().lower()
            if ver_como in ['s', 'sim']:
                print(f"\n{REVERSE}  MECANISMO DE EXPLICAÇÃO: 'COMO?'  {RESET}")
                print_retro(f"{VERDE}{explicador.como(hip_id)}{RESET}\n")
    else:
        print_retro(f"\n{VERDE_BRILHANTE}[RESULTADO]: Nenhuma hipótese conhecida pôde ser comprovada.{RESET}\n")

    print(f"{VERDE}------------------------------------------------------------{RESET}")
    print_retro(f"{VERDE}{explicador.resumo_sessao()}{RESET}")
    print(f"{VERDE}------------------------------------------------------------{RESET}")
    input(f"\n{VERDE}Pressione [ENTER] para retornar...{RESET}")

def menu_principal():
    while True:
        sys.stdout.write("\033[H\033[2J")
        exibir_cabecalho()
        print(f"{VERDE_BRILHANTE}  1. INICIAR NOVA CONSULTA DIAGNÓSTICA{RESET}")
        print(f"{VERDE}  2. MODO DESENVOLVEDOR (EDITAR BASE DE CONHECIMENTO){RESET}")
        print(f"{VERDE}  0. RETORNAR AO HUB PRINCIPAL{RESET}\n")
        
        opcao = input(f"{VERDE}SELECIONE UMA OPÇÃO COGNITIVA_> {RESET}").strip()
        
        if opcao == "1":
            executar_consulta()
        elif opcao == "2":
            print_retro(f"\n{VERDE}[SISTEMA]: Transferindo controle para o subsistema de edição (Terminal Azul)...{RESET}")
            time.sleep(0.5)
            try:
                editor_kb = KnowledgeBaseEditor(CAMINHO_KB)
                run_interactive(editor_kb, backup=True)
            except Exception as e:
                print(f"{VERDE}[ERRO CRÍTICO]: Falha ao iniciar o editor: {e}{RESET}")
                input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")
        elif opcao == "0":
            print_retro(f"\n{VERDE}[SISTEMA]: Finalizando buffers... Retornando ao Hub.{RESET}")
            break
        else:
            print(f"{VERDE}[ERRO]: Código de instrução inválido.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    import os
    
    if "--child-process" not in sys.argv:
        caminho_script = sys.argv[0]
        
        if sys.platform == "win32":
            comando = f'start "MechApe OS 1986" cmd /c "mode con: cols=120 lines=35 && python {caminho_script} --child-process"'
            os.system(comando)
            
        elif sys.platform == "darwin":
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = f"""osascript -e 'tell application "Terminal" to do script "python3 {caminho_absoluto} --child-process"'"""
            os.system(comando)
            
        else:
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = f"gnome-terminal --geometry=120x35 -- bash -c 'python3 {caminho_absoluto} --child-process; exec bash'"
            os.system(comando)
            
        sys.exit(0)

    try:
        menu_principal()
    except KeyboardInterrupt:
        print(f"\n{VERDE}[SISTEMA]: Interrupção forçada pelo operador. Encerrando.{RESET}")