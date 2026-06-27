"""
Interface com o Usuário do MechApe - Módulo 5 (P3)
Estética Retrô PC Anos 80 / Terminal ASCII
Integração com Motor de Inferência (P1) e Editor de Base (P2)
"""

from __future__ import annotations
import sys
import time
import argparse
from pathlib import Path

# Garante a importação correta dos módulos locais
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from motor_inferencia import MotorInferencia
from q1.explicador import ExplicadorInferencia
from q1 import editor

# Cores ANSI para estética fósforo verde de terminal antigo
VERDE = "\033[0;32m"
VERDE_BRILHANTE = "\033[1;32m"
REVERSE = "\033[7m"
RESET = "\033[0m"

CAMINHO_KB = ROOT / "q1" / "tests" / "knowledge_base.json"

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
    print("      MECHAPE KNOWLEDGE SYSTEM - OS VERSION 1986.06         ")
    print("============================================================")
    print(RESET)

# ======================================================================
# MÓDULO DE CONSULTA E DIAGNÓSTICO
# ======================================================================

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

# ======================================================================
# MÓDULO DE EDIÇÃO DA BASE DE CONHECIMENTO (INTEGRAÇÃO P2)
# ======================================================================

def prompt_retro(texto: str, default: str | None = None) -> str:
    """Função auxiliar para coletar inputs obrigatórios estilizados."""
    sufixo = f" [{default}]" if default is not None else ""
    while True:
        valor = input(f"{VERDE_BRILHANTE}  > {texto}{sufixo}: {RESET}").strip()
        if valor:
            return valor
        if default is not None:
            return default
        print(f"{VERDE}[ERRO]: Campo de preenchimento obrigatório.{RESET}")

def menu_editor():
    while True:
        try:
            kb = editor.load_kb(CAMINHO_KB)
        except Exception as e:
            print(f"{VERDE}[ERRO CRÍTICO]: Falha ao ler a base de dados: {e}{RESET}")
            break

        sys.stdout.write("\033[H\033[2J")
        exibir_cabecalho()
        print(f"{REVERSE}  MODO DESENVOLVEDOR: EDITOR DE CONHECIMENTO (ROOT)  {RESET}\n")
        print(f"{VERDE}  1. LISTAR FATOS CADASTRADOS{RESET}")
        print(f"{VERDE}  2. REGISTRAR NOVO FATO{RESET}")
        print(f"{VERDE}  3. LISTAR REGRAS DE INFERÊNCIA{RESET}")
        print(f"{VERDE}  4. REGISTRAR NOVA REGRA{RESET}")
        print(f"{VERDE}  5. MODIFICAR REGRA EXISTENTE{RESET}")
        print(f"{VERDE}  6. DELETAR REGRA{RESET}")
        print(f"{VERDE}  0. RETORNAR AO MENU PRINCIPAL{RESET}\n")
        
        opcao = input(f"{VERDE}SELECIONE UMA ROTINA_> {RESET}").strip()
        
        try:
            if opcao == "1":
                print(f"\n{VERDE_BRILHANTE}--- FATOS CONHECIDOS PELO SISTEMA ---{RESET}")
                for f in editor.facts(kb):
                    print(f"{VERDE}[{f['id']:<8}] {f['source']:<10} | {f['category']:<20} | {f['label']}{RESET}")
                input(f"\n{VERDE}Pressione [ENTER] para continuar...{RESET}")
                
            elif opcao == "2":
                print(f"\n{VERDE_BRILHANTE}--- CADASTRAR NOVO FATO ---{RESET}")
                source = prompt_retro("Fonte de dados (user_input ou inferred)", "user_input")
                ns = argparse.Namespace(
                    id=None,
                    attribute=prompt_retro("Nome da variável (snake_case)"),
                    label=prompt_retro("Descrição clara do fato"),
                    question=None if source == "inferred" else prompt_retro("Pergunta a ser feita ao usuário"),
                    type=prompt_retro("Tipo de dado", "boolean"),
                    category=prompt_retro("Categoria temática", "inferred" if source == "inferred" else "desempenho_execucao"),
                    source=source,
                )
                item = editor.add_fact(kb, ns)
                editor.validate_references(kb)
                editor.save_kb(kb, CAMINHO_KB)
                print(f"\n{VERDE_BRILHANTE}[SUCESSO]: Fato {item['id']} persistido na matriz de conhecimento!{RESET}")
                input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")

            elif opcao == "3":
                print(f"\n{VERDE_BRILHANTE}--- MATRIZ DE REGRAS (SE...ENTÃO) ---{RESET}")
                for r in editor.rules(kb):
                    conc = r["conclusion"]
                    alvo = conc.get("fact_id") or conc.get("hypothesis_id")
                    se = " E ".join(r["conditions"])
                    print(f"{VERDE}[{r['id']:<4}] SE {se} ENTÃO {alvo} (Tipo: {r['conclusion_type']} | Prio: {r['priority']}){RESET}")
                input(f"\n{VERDE}Pressione [ENTER] para continuar...{RESET}")
                
            elif opcao == "4":
                print(f"\n{VERDE_BRILHANTE}--- CADASTRAR NOVA REGRA LÓGICA ---{RESET}")
                ns = argparse.Namespace(
                    id=None,
                    label=prompt_retro("Descrição ou título da regra"),
                    conditions=prompt_retro("Condições SE (IDs separados por vírgula, ex: F01,F23)"),
                    conclusion_type=prompt_retro("Tipo de Conclusão (intermediate ou hypothesis)", "hypothesis"),
                    conclusion_id=prompt_retro("ID do Alvo (Fato inferido ou Hipótese final)"),
                    value=True,
                    priority=int(prompt_retro("Prioridade de execução (1-5)", "2")),
                    explanation_why=prompt_retro("Justificativa para o 'Por quê?'"),
                    explanation_how=prompt_retro("Justificativa para o 'Como?'"),
                )
                item = editor.add_rule(kb, ns)
                editor.validate_references(kb)
                editor.save_kb(kb, CAMINHO_KB)
                print(f"\n{VERDE_BRILHANTE}[SUCESSO]: Regra {item['id']} compilada e salva com sucesso!{RESET}")
                input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")

            elif opcao == "5":
                print(f"\n{VERDE_BRILHANTE}--- SOBRESCREVER REGRA EXISTENTE ---{RESET}")
                print(f"{VERDE}(Deixe os campos em branco e pressione ENTER para manter o valor atual){RESET}")
                id_regra = prompt_retro("Digite o ID da regra que deseja editar (ex: R01)")
                
                # Coleta os dados que podem ser opcionais
                prio_str = input(f"{VERDE_BRILHANTE}  > Nova prioridade 1-5 (vazio mantém): {RESET}").strip()
                
                ns = argparse.Namespace(
                    id=id_regra,
                    label=input(f"{VERDE_BRILHANTE}  > Novo título da regra (vazio mantém): {RESET}").strip() or None,
                    conditions=input(f"{VERDE_BRILHANTE}  > Novas condições CSV (vazio mantém): {RESET}").strip() or None,
                    conclusion_type=input(f"{VERDE_BRILHANTE}  > Novo tipo conclusão [intermediate/hypothesis] (vazio mantém): {RESET}").strip() or None,
                    conclusion_id=input(f"{VERDE_BRILHANTE}  > Novo ID de conclusão (vazio mantém): {RESET}").strip() or None,
                    value=None,
                    priority=int(prio_str) if prio_str.isdigit() else None,
                    explanation_why=input(f"{VERDE_BRILHANTE}  > Nova explicação Por que (vazio mantém): {RESET}").strip() or None,
                    explanation_how=input(f"{VERDE_BRILHANTE}  > Nova explicação Como (vazio mantém): {RESET}").strip() or None,
                )
                item = editor.edit_rule(kb, ns)
                editor.validate_references(kb)
                editor.save_kb(kb, CAMINHO_KB)
                print(f"\n{VERDE_BRILHANTE}[SUCESSO]: Estrutura da regra {item['id']} reescrita com sucesso!{RESET}")
                input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")

            elif opcao == "6":
                print(f"\n{VERDE_BRILHANTE}--- DELETAR REGRA ---{RESET}")
                ns = argparse.Namespace(id=prompt_retro("Digite o ID da regra a ser expurgada"))
                item = editor.remove_rule(kb, ns)
                editor.validate_references(kb)
                editor.save_kb(kb, CAMINHO_KB)
                print(f"\n{VERDE_BRILHANTE}[SUCESSO]: Regra {item['id']} removida permanentemente do sistema.{RESET}")
                input(f"{VERDE}Pressione [ENTER] para continuar...{RESET}")

            elif opcao == "0":
                print_retro(f"\n{VERDE}[SISTEMA]: Fechando conexão com o núcleo de edição...{RESET}")
                break
            else:
                print(f"{VERDE}[ERRO]: Opção inválida.{RESET}")
                time.sleep(1)
                
        except (editor.KnowledgeBaseError, ValueError, Exception) as exc:
            # Qualquer erro de validação (ex: regra apontando pra fato que não existe) cai aqui
            print(f"\n{VERDE}[ERRO DE COMPILAÇÃO]: {exc}{RESET}")
            input(f"{VERDE}Pressione [ENTER] para retornar...{RESET}")

# ======================================================================
# MENU PRINCIPAL
# ======================================================================

def menu_principal():
    while True:
        sys.stdout.write("\033[H\033[2J")
        exibir_cabecalho()
        print(f"{VERDE_BRILHANTE}  1. INICIAR NOVA CONSULTA DIAGNÓSTICA{RESET}")
        print(f"{VERDE}  2. EXIBIR CRÉDITOS DO SISTEMA OPERACIONAL{RESET}")
        print(f"{VERDE}  3. MODO DESENVOLVEDOR (EDITAR BASE DE CONHECIMENTO){RESET}")
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
        elif opcao == "3":
            menu_editor()
        elif opcao == "0":
            print_retro(f"\n{VERDE}[SISTEMA]: Finalizando buffers... Desligando. Adeus.{RESET}")
            break
        else:
            print(f"{VERDE}[ERRO]: Código de instrução inválido.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    import os
    
    # Verifica se o script já está rodando na nova janela
    if "--child-process" not in sys.argv:
        caminho_script = sys.argv[0]
        
        if sys.platform == "win32":
            # No Windows: Usa o 'start cmd' e o 'mode con' para definir colunas (largura) e linhas (altura)
            # cols=120 e lines=35 é uma excelente resolução para menus de texto
            comando = f'start "MechApe OS 1986" cmd /c "mode con: cols=120 lines=35 && python {caminho_script} --child-process"'
            os.system(comando)
            
        elif sys.platform == "darwin":
            # No macOS: Usa AppleScript para abrir o Terminal.app
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = f"""osascript -e 'tell application "Terminal" to do script "python3 {caminho_absoluto} --child-process"'"""
            os.system(comando)
            
        else:
            # No Linux: Tenta usar o gnome-terminal (comum no Ubuntu)
            caminho_absoluto = os.path.abspath(caminho_script)
            comando = f"gnome-terminal --geometry=120x35 -- bash -c 'python3 {caminho_absoluto} --child-process; exec bash'"
            os.system(comando)
            
        # Encerra o processo "pai" silenciosamente, deixando apenas a nova janela aberta
        sys.exit(0)

    # Se a flag --child-process estiver presente, executa o programa normalmente
    try:
        menu_principal()
    except KeyboardInterrupt:
        print(f"\n{VERDE}[SISTEMA]: Interrupção forçada pelo operador. Encerrando.{RESET}")