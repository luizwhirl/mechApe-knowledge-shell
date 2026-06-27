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

    @patch('q1.interface.run_interactive')
    @patch('builtins.input')
    @patch('sys.stdout')
    def test_menu_principal_chama_editor_azul(self, mock_stdout, mock_input, mock_run_interactive):
        """Testa se a Opção 3 transfere o controle para o terminal azul corretamente."""
        
        # O usuário digita "3" (abrir modo desenvolvedor), e logo em seguida "0" (sair do sistema principal)
        mock_input.side_effect = ["3", "0"]
        
        # Executa o loop do menu principal
        interface.menu_principal()
        
        # Verifica se o run_interactive do terminal azul foi instanciado e chamado
        mock_run_interactive.assert_called_once()
        
        # Valida os argumentos passados para inicializar o terminal azul
        args, kwargs = mock_run_interactive.call_args
        self.assertTrue(kwargs.get("backup"))
        self.assertIsNotNone(args[0])  # Verifica se instanciou o KnowledgeBaseEditor

if __name__ == "__main__":
    unittest.main(verbosity=2)