"""
Testes de Integração da Interface com o Editor - Módulo 5 (P3)

Localização esperada: q1/tests/test_interface.py
Executar a partir da raiz do projeto:
    python -m unittest q1.tests.test_interface
"""

import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

# Garante que 'q1' seja encontrado
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from q1 import interface
from q1 import editor

class TestInterfaceEditor(unittest.TestCase):
    def setUp(self):
        # 1. Cria um diretório temporário e copia a base original para não sujar o JSON real
        self.tmpdir = tempfile.TemporaryDirectory()
        self.kb_path = Path(self.tmpdir.name) / "knowledge_base.json"
        shutil.copy2(Path(__file__).with_name("knowledge_base.json"), self.kb_path)
        
        # 2. Sobrescreve a variável global CAMINHO_KB dentro do módulo interface
        self.patcher_kb = patch('q1.interface.CAMINHO_KB', self.kb_path)
        self.patcher_kb.start()
        
        # 3. Zera os "sleeps" do print_retro para os testes rodarem instantaneamente
        self.patcher_sleep = patch('time.sleep', return_value=None)
        self.patcher_sleep.start()

    def tearDown(self):
        # Limpa os mocks e apaga o arquivo temporário
        self.patcher_kb.stop()
        self.patcher_sleep.stop()
        self.tmpdir.cleanup()

    @patch('builtins.input')
    def test_prompt_retro_comportamento(self, mock_input):
        """Testa se o prompt auxiliar respeita valores padrão e sobrescritas."""
        # Cenário 1: Usuário aperta enter vazio, deve usar o valor padrão
        mock_input.side_effect = [""]
        resultado = interface.prompt_retro("Teste", default="valor_padrao")
        self.assertEqual(resultado, "valor_padrao")
        
        # Cenário 2: Usuário digita algo, deve ignorar o padrão
        mock_input.side_effect = ["meu_valor_customizado"]
        resultado = interface.prompt_retro("Teste", default="valor_padrao")
        self.assertEqual(resultado, "meu_valor_customizado")

    @patch('builtins.input')
    @patch('sys.stdout') # Suprime os prints da interface no terminal de testes
    def test_menu_editor_cadastrar_fato(self, mock_stdout, mock_input):
        """Testa o fluxo completo de navegação do menu para criar um novo fato."""
        
        # Sequência exata de inputs que um usuário daria no terminal:
        mock_input.side_effect = [
            "2",                      # Seleciona Opção 2: Registrar novo fato
            "user_input",             # Fonte de dados
            "teste_novo_fato_cli",    # Nome da variável
            "Fato criado via Teste",  # Descrição
            "Isso é um teste?",       # Pergunta
            "boolean",                # Tipo
            "hardware",               # Categoria
            "",                       # Pressiona [ENTER] para continuar
            "0"                       # Opção 0: Sair do editor
        ]
        
        # Roda o menu (ele vai consumir o side_effect e sair automaticamente no "0")
        interface.menu_editor()
        
        # Verifica se o fato foi realmente salvo no arquivo JSON temporário
        kb_atualizada = editor.load_kb(self.kb_path)
        fatos_salvos = [f["attribute"] for f in editor.facts(kb_atualizada)]
        
        self.assertIn("teste_novo_fato_cli", fatos_salvos)

    @patch('builtins.input')
    @patch('sys.stdout')
    def test_menu_editor_deletar_regra(self, mock_stdout, mock_input):
        """Testa o fluxo de deleção de uma regra."""
        
        mock_input.side_effect = [
            "6",    # Seleciona Opção 6: Deletar Regra
            "R01",  # Digita o ID da regra
            "",     # Pressiona [ENTER] para continuar
            "0"     # Opção 0: Sair do editor
        ]
        
        interface.menu_editor()
        
        kb_atualizada = editor.load_kb(self.kb_path)
        ids_regras = {r["id"] for r in editor.rules(kb_atualizada)}
        
        self.assertNotIn("R01", ids_regras)

if __name__ == "__main__":
    unittest.main(verbosity=2)