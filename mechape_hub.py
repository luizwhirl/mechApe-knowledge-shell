import sys
import os
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LARANJA = "\033[38;5;214m"
VERMELHO_CLARO = "\033[91m"
REVERSE = "\033[7m"
RESET = "\033[0m"

def print_retro(texto: str, cor: str = LARANJA, atraso: float = 0.005, nova_linha: bool = True):
    for caractere in texto:
        sys.stdout.write(cor + caractere + RESET)
        sys.stdout.flush()
        time.sleep(atraso)
    if nova_linha:
        print()

# def exibir_cabecalho():
#     print(LARANJA)
#     print(' 888b     d888                   888            d8888 8888888b.  8888888888    ▒▒▒▒▒▄██████████▄▒▒▒▒▒')
#     print(' 8888b   d8888                   888           d88888 888   Y88b 888           ▒▒▒▄██████████████▄▒▒▒')
#     print(' 88888b.d88888                   888          d88P888 888    888 888           ▒▒██████████████████▒▒')
#     print(' 888Y88888P888  .d88b.  .d8888b. 88888b.     d88P 888 888   d88P 8888888       ▒▐███▀▀▀▀▀██▀▀▀▀▀███▌▒')
#     print(' 888 Y888P 888 d8P  Y8bd88P  Y88b888 "88b   d88P  888 8888888P"  888           ▒███▒▒▌■▐▒▒▒▒▌■▐▒▒███▒')
#     print(' 888  Y8P  888 88888888888       888  888  d88P   888 888        888           ▒▐██▄▒▀▀▀▒▒▒▒▀▀▀▒▄██▌▒')
#     print(' 888       888 Y8b.    Y88b  d88P888  888 d8888888888 888        888           ▒▒▀████▒▄▄▒▒▄▄▒████▀▒▒')
#     print(' 888       888  "Y8888  "Y8888P" 888  888d88P     888 888        8888888888    ▒▒▐███▒▒▒▀▒▒▀▒▒▒███▌▒▒')
#     print('                                                                               ▒▒███▒▒▒▒▒▒▒▒▒▒▒▒███▒▒')
#     print('                                                                               ▒▒▒██▒▒▀▀▀▀▀▀▀▀▒▒██▒▒▒')
#     print('                                                                               ▒▒▒▐██▄▒▒▒▒▒▒▒▒▄██▌▒▒▒')
#     print('                                                                               ▒▒▒▒▀████████████▀▒▒▒▒')
#     print("                                              team questions hub                           ")
#     print(RESET)

def exibir_cabecalho():
    print(LARANJA)
    print(' 888b     d888                   888            d8888 8888888b.  8888888888 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
    print(' 8888b   d8888                   888           d88888 888   Y88b 888        ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⣿⣿⣿⣿⣷⣦⠀⠀⠀⠀⠀⠀⠀⠀')
    print(' 88888b.d88888                   888          d88P888 888    888 888        ⠀⠀⠀⠀⠀⠀⠀⠀⣺⣿⠟⠻⡿⠿⢿⣿⡇⠀⠀⠀⠀⠀⠀⠀')
    print(' 888Y88888P888  .d88b.  .d8888b. 88888b.     d88P 888 888   d88P 8888888    ⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⢰⡿⠐⣿⠀⣿⣧⠀⠀⠀⠀⠀⠀⠀')
    print(' 888 Y888P 888 d8P  Y8bd88P  Y88b888 "88b   d88P  888 8888888P"  888        ⠀⠀⠀⠀⠀⠀⢴⡿⠉⠑⠴⢶⣷⠶⠤⠉⠻⣶⡄⠀⠀⠀⠀⠀')
    print(' 888  Y8P  888 88888888888       888  888  d88P   888 888        888        ⠀⠀⠀⠀⠀⠀⠀⡇⢢⠀⠀⠀⠀⠀⠀⣠⠄⡏⠀⠀⠀⠀⠀⠀')
    print(' 888       888 Y8b.    Y88b  d88P888  888 d8888888888 888        888        ⠀⠀⠀⠀⠀⠀⠀⢑⡤⠑⠢⠤⠤⠤⠚⢁⣴⠁⠀⠀⠀⠀⠀⠀')
    print(' 888       888  "Y8888  "Y8888P" 888  888d88P     888 888        8888888888 ⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣶⣶⣶⣶⣒⣺⣿⣶⣄⠀⠀⠀⠀⠀')
    print('                                                                            ⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡄⠀⠀⠀')
    print('                                                                            ⠀⢠⣰⣿⣿⣿⣿⡿⠿⠿⠿⠿⠿⠏⠉⠛⠛⢿⣿⣿⣿⣷⣄⠀')
    print('                      ╔══════════════════════════════════╗                  ⠀⣿⣿⣿⠿⣿⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠻⣿⣿⣿⠇')
    print('                      ║ ► TEAM QUESTIONS HUB • v2026.1 ◄ ║                  ⠀⠈⠉⠁⠀⣹⣷⡀⠀⠀⠀⠘⠃⠀⠀⠀⠀⣼⣟⠀⠀⠉⠉⠀')
    print('                      ╚══════════════════════════════════╝                  ⠀⠀⠀⠀⠀⣿⣿⣿⣆⣄⣀⡀⠀⣀⣠⣴⣾⣿⣿⠀⠀⠀⠀⠀')
    print('                                                                            ⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⠋⠉⠉⠙⣿⣿⣿⣿⡿⠀⠀⠀⠀⠀')
    print('                                                                            ⠀⠀⠀⠀⠀⠘⠿⣿⣿⣿⣆⠀⠀⣰⣿⣿⣿⣟⠁⠀⠀⠀⠀⠀')
    print('                                                                            ⠀⠀⠀⠀⣠⣶⣿⣿⣿⣿⣿⠅⠀⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀')
    print('                                                                            ⠀⠀⠀⠈⠻⠿⠿⠟⠁⠈⠁⠀⠀⠈⠁⠉⠻⠿⠻⠟⠁⠀⠀⠀')
    print('                                                                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
    print(RESET)

def menu_principal():
    while True:
        sys.stdout.write("\033[H\033[2J")
        exibir_cabecalho()
        
        print(f"{LARANJA}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{LARANJA}║{RESET}  {VERMELHO_CLARO}1. EXECUTAR QUESTÃO 1 (Motor de Inferência){RESET}                 {LARANJA}║{RESET}")
        print(f"{LARANJA}║{RESET}  {VERMELHO_CLARO}2. EXECUTAR QUESTÃO 2 (Identificador de Personagens){RESET}        {LARANJA}║{RESET}")
        print(f"{LARANJA}║{RESET}  {VERMELHO_CLARO}3. EXECUTAR QUESTÃO 3 (Agente LLM){RESET}                          {LARANJA}║{RESET}")
        print(f"{LARANJA}║{RESET}  {VERMELHO_CLARO}0. DESLIGAR TERMINAL (SAIR){RESET}                                 {LARANJA}║{RESET}")
        print(f"{LARANJA}╚══════════════════════════════════════════════════════════════╝{RESET}")
        print()
        
        opcao = input(f"{LARANJA}SELECIONE O MÓDULO DESEJADO > {RESET}").strip()
        
        if opcao == "1":
            print_retro("\n[SISTEMA]: Inicializando Questão 1...", LARANJA)
            time.sleep(0.5)
            script_path = ROOT / "q1" / "interface.py"
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path), "--child-process"])
            else:
                print_retro(f"[ERRO]: Arquivo não encontrado: {script_path}", VERMELHO_CLARO)
                time.sleep(2)
        elif opcao == "2":
            print_retro("\n[SISTEMA]: Inicializando Questão 2...", LARANJA)
            time.sleep(0.5)
            script_path = ROOT / "q2" / "q2-1.py" / "interface.py"
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path), "--child-process"])
            else:
                print_retro(f"[ERRO]: Arquivo não encontrado: {script_path}", VERMELHO_CLARO)
                time.sleep(2)
        elif opcao == "3":
            # print_retro("\n[SISTEMA]: Inicializando Questão 3...", LARANJA)
            # time.sleep(0.5)
            # script_path = ROOT / "q3" / "agente_llm.py"
            # if script_path.exists():
            #     subprocess.run([sys.executable, str(script_path), "--child-process"])
            # else:
            #     print_retro(f"[ERRO]: Arquivo não encontrado: {script_path}", VERMELHO_CLARO)
            #     time.sleep(2)
            
            print_retro("\n[AVISO]: Módulo da Questão 3 ainda em desenvolvimento.", VERMELHO_CLARO)
            time.sleep(1.5)
            
        elif opcao == "0":
            print_retro("\n[SISTEMA]: Encerrando Hub... Desligando terminal. Adeus.", LARANJA)
            time.sleep(1)
            break
        else:
            print_retro("[ERRO]: Código de instrução inválido.", VERMELHO_CLARO)
            time.sleep(1)

if __name__ == "__main__":
    if "--child-process" not in sys.argv:
        caminho_script = sys.argv[0]
        
        if sys.platform == "win32":
            comando = f'start "MechApe Questions Hub" cmd /c "mode con: cols=120 lines=35 && python {caminho_script} --child-process"'
            os.system(comando)
            
        elif sys.platform == "darwin":
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = "osascript -e 'tell application \"Terminal\" to do script \"python3 " + caminho_absoluto + " --child-process\"'"
            os.system(comando)
            
        else:
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = f"gnome-terminal --geometry=120x35 -- bash -c 'python3 {caminho_absoluto} --child-process; exec bash'"
            os.system(comando)
            
        sys.exit(0)

    try:
        menu_principal()
    except KeyboardInterrupt:
        print(f"\n{LARANJA}[SISTEMA]: Interrupção forçada pelo operador. Encerrando.{RESET}")
