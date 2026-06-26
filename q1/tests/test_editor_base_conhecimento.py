import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from editor_base_conhecimento import EditorError, KnowledgeBaseEditor


class KnowledgeBaseEditorTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.tmpdir.name) / "knowledge_base.json"
        shutil.copy2(ROOT / "tests" / "knowledge_base.json", self.base_path)
        self.editor = KnowledgeBaseEditor(self.base_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_edit_and_remove_fact(self):
        fact = self.editor.add_fact(
            attribute="teste_crud_fato",
            label="Fato criado pelo teste de CRUD",
            question="Este fato foi criado pelo teste?",
            category="hardware",
        )

        self.assertRegex(fact["id"], r"^F\d+$")
        self.assertEqual(fact["source"], "user_input")

        edited = self.editor.edit_fact(
            fact["id"],
            label="Fato editado pelo teste de CRUD",
            question="Este fato foi editado pelo teste?",
        )
        self.assertEqual(edited["label"], "Fato editado pelo teste de CRUD")

        report = self.editor.remove_fact(fact["id"])
        self.assertEqual(report.removed_id, fact["id"])
        self.assertNotIn(fact["id"], self.editor.fact_ids())

    def test_add_edit_and_remove_rule(self):
        rule = self.editor.add_rule_from_text(
            "SE F01 E F23 ENTAO H1=true",
            label="Regra temporaria de CRUD",
            priority=4,
            explanation_why="Teste de explicacao por que.",
            explanation_how="Teste de explicacao como.",
        )

        self.assertRegex(rule["id"], r"^R\d+$")
        self.assertEqual(rule["conditions"], ["F01", "F23"])
        self.assertEqual(rule["conclusion"]["hypothesis_id"], "H1")

        edited = self.editor.edit_rule(rule["id"], conditions=["F02", "F25"], priority=2)
        self.assertEqual(edited["conditions"], ["F02", "F25"])
        self.assertEqual(edited["priority"], 2)

        removed = self.editor.remove_rule(rule["id"])
        self.assertEqual(removed["id"], rule["id"])
        self.assertNotIn(rule["id"], self.editor.rule_ids())

    def test_remove_referenced_fact_requires_force(self):
        with self.assertRaises(EditorError):
            self.editor.remove_fact("F23")

        report = self.editor.remove_fact("F23", force=True)
        self.assertIn("R01", report.removed_rules)
        self.assertNotIn("F23", self.editor.fact_ids())
        self.assertNotIn("R01", self.editor.rule_ids())

    def test_save_persists_changes(self):
        fact = self.editor.add_fact(
            attribute="persistencia_crud",
            label="Fato persistido pelo editor",
            question="O fato persistiu no JSON?",
        )
        self.editor.save(backup=False)

        with self.base_path.open(encoding="utf-8") as file:
            data = json.load(file)
        ids = {item["id"] for item in data["facts"]["items"]}
        self.assertIn(fact["id"], ids)

    def test_integrity_rejects_missing_references(self):
        with self.assertRaises(EditorError):
            self.editor.add_rule(
                conditions=["F_NAO_EXISTE"],
                conclusion_id="H1",
                explanation_why="Teste",
                explanation_how="Teste",
            )


if __name__ == "__main__":
    unittest.main()
