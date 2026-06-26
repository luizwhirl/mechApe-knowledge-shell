import argparse
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from q1 import editor


class EditorCliTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.kb_path = Path(self.tmpdir.name) / "knowledge_base.json"
        shutil.copy2(Path(__file__).with_name("knowledge_base.json"), self.kb_path)
        self.kb = editor.load_kb(self.kb_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_fact_generates_next_user_fact_id(self):
        fact = editor.add_fact(
            self.kb,
            argparse.Namespace(
                id=None,
                attribute="teste_novo_sintoma",
                label="Novo sintoma de teste",
                question="O novo sintoma apareceu?",
                type="boolean",
                category="hardware",
                source="user_input",
            ),
        )

        self.assertEqual(fact["id"], "F32")
        self.assertEqual(fact["source"], "user_input")
        editor.validate_references(self.kb)

    def test_add_edit_and_remove_rule(self):
        added = editor.add_rule(
            self.kb,
            argparse.Namespace(
                id=None,
                label="Regra de teste",
                conditions="F01,F23",
                conclusion_type="hypothesis",
                conclusion_id="H1",
                value=True,
                priority=2,
                explanation_why="Teste do motivo.",
                explanation_how="Teste do caminho.",
            ),
        )

        self.assertEqual(added["id"], "R22")
        self.assertEqual(added["conditions"], ["F01", "F23"])

        edited = editor.edit_rule(
            self.kb,
            argparse.Namespace(
                id="R22",
                label="Regra de teste editada",
                conditions="F02,F25",
                conclusion_type=None,
                conclusion_id=None,
                value=None,
                priority=4,
                explanation_why=None,
                explanation_how=None,
            ),
        )

        self.assertEqual(edited["label"], "Regra de teste editada")
        self.assertEqual(edited["conditions"], ["F02", "F25"])
        self.assertEqual(edited["priority"], 4)

        removed = editor.remove_rule(self.kb, argparse.Namespace(id="R22"))
        self.assertEqual(removed["id"], "R22")
        self.assertNotIn("R22", {rule["id"] for rule in editor.rules(self.kb)})
        editor.validate_references(self.kb)

    def test_rejects_rule_with_unknown_fact(self):
        with self.assertRaises(editor.KnowledgeBaseError):
            editor.add_rule(
                self.kb,
                argparse.Namespace(
                    id=None,
                    label="Regra invalida",
                    conditions="F999",
                    conclusion_type="hypothesis",
                    conclusion_id="H1",
                    value=True,
                    priority=2,
                    explanation_why="Teste.",
                    explanation_how="Teste.",
                ),
            )


if __name__ == "__main__":
    unittest.main()
