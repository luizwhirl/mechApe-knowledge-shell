from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_KB_PATH = Path(__file__).parent / "tests" / "knowledge_base.json"
FACT_ID_RE = re.compile(r"^F(?:(?:_INF)?_?\d+|\d+)$")
RULE_ID_RE = re.compile(r"^R\d+$")
HYPOTHESIS_ID_RE = re.compile(r"^H\d+$")
ATTRIBUTE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
RULE_TEXT_RE = re.compile(
    r"^\s*SE\s+(?P<conditions>.+?)\s+ENT(?:A|Ã)O\s+(?P<conclusion>.+?)\s*$",
    re.IGNORECASE,
)

FACT_CATEGORIES = {
    "desempenho_execucao",
    "launchers",
    "software_so",
    "overlays",
    "hardware",
    "inferred",
}
FACT_TYPES = {"boolean", "numeric", "categorical"}
FACT_SOURCES = {"user_input", "inferred"}

AZUL = "\033[0;34m"
AZUL_BRILHANTE = "\033[1;34m"
REVERSE = "\033[7m"
RESET = "\033[0m"

def print_retro(texto: str, atraso: float = 0.005, nova_linha: bool = True):
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(atraso)
    if nova_linha:
        print()

def exibir_cabecalho():
    print(AZUL)
    print("============================================================")
    print(" ███▄ ▄███▓▓█████  ▄████▄   ██░ ██  ▄▄▄       ██▓███  ▓█████ ")
    print(" ▓██▒▀█▀ ██▒▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒▒████▄    ▓██░  ██▒▓█   ▀ ")
    print(" ▓██    ▓██░▒███   ▒▓█    ▄ ▒██▀▀██░▒██  ▀█▄  ▓██░ ██▓▒▒███   ")
    print(" ▒██    ▒██ ▒▓█  ▄ ▒▓▓▄ ▄██▒░██ ░██ ░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓█  ▄ ")
    print(" ▒██▒   ░██▒░▒████▒▒ ▓███▀ ░░██ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░░▒████▒")
    print(" ░ ▒░   ░  ░░░ ▒░ ░░ ░▒ ▒  ░░ ▒ ░▒░ ░▒▒   ▓▒█░▒▓ ░      ░░ ▒░ ░")
    print("                                                            ")
    print("   ███████╗██████╗ ██╗████████╗██████╗ ██████╗              ")
    print("   ██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██╔══██╗             ")
    print("   █████╗  ██║  ██║██║   ██║   ██║  ██║██████╔╝             ")
    print("   ██╔══╝  ██║  ██║██║   ██║   ██║  ██║██╔══██╗             ")
    print("   ███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║            ")
    print("   ╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝            ")
    print("============================================================")
    print("      MECHAPE KNOWLEDGE EDITOR - OS VERSION 2026.06         ")
    print("============================================================")
    print(RESET)

def prompt_choice(texto: str, opcoes: list[str], padrao: str | None = None) -> str:
    print(f"\n{AZUL_BRILHANTE}{texto}{RESET}")
    for i, op in enumerate(opcoes, 1):
        marcador = " (Padrão)" if padrao == op else ""
        print(f"{AZUL}  [{i}] {op}{marcador}{RESET}")
    
    while True:
        sufixo = f" ou ENTER para padrão" if padrao else ""
        escolha = input(f"{AZUL}Selecione uma opção (1-{len(opcoes)}){sufixo}: {RESET}").strip()
        if not escolha and padrao:
            return padrao
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx]
        print(f"{AZUL}[ERRO]: Opção inválida. Digite um número de 1 a {len(opcoes)}.{RESET}")

def prompt_choice_edit(texto: str, opcoes: list[str], atual: str) -> str | None:
    print(f"\n{AZUL_BRILHANTE}{texto} [Atual: {atual}] (Pressione ENTER para manter){RESET}")
    for i, op in enumerate(opcoes, 1):
        print(f"{AZUL}  [{i}] {op}{RESET}")
    
    while True:
        escolha = input(f"{AZUL}Selecione uma opção (1-{len(opcoes)}) ou ENTER para manter: {RESET}").strip()
        if not escolha:
            return None
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx]
        print(f"{AZUL}[ERRO]: Opção inválida. Digite um número de 1 a {len(opcoes)}.{RESET}")

class EditorError(ValueError):
    pass

@dataclass(frozen=True)
class RemovalReport:
    removed_id: str
    removed_rules: list[str]

def _now_backup_stamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")

def _parse_scalar(value: str | bool | int | float | None) -> Any:
    if not isinstance(value, str):
        return value
    normalized = value.strip()
    lowered = normalized.lower()
    if lowered in {"true", "sim", "yes", "1"}:
        return True
    if lowered in {"false", "nao", "não", "no", "0"}:
        return False
    if lowered in {"null", "none", ""}:
        return None
    try:
        if "." in normalized:
            return float(normalized)
        return int(normalized)
    except ValueError:
        return normalized

def _format_rule(rule: dict[str, Any]) -> str:
    conclusion = rule["conclusion"]
    if "fact_id" in conclusion:
        target = conclusion["fact_id"]
    else:
        target = conclusion["hypothesis_id"]
    return (
        f"{rule['id']} | SE {' E '.join(rule['conditions'])} ENTAO "
        f"{target} = {conclusion['value']} | prioridade {rule['priority']}"
    )

class KnowledgeBaseEditor:

    def __init__(self, path: str | Path = DEFAULT_KB_PATH) -> None:
        self.path = Path(path)
        self.data = self.load(self.path)

    @staticmethod
    def load(path: str | Path) -> dict[str, Any]:
        kb_path = Path(path)
        if not kb_path.exists():
            raise EditorError(f"Arquivo de base nao encontrado: {kb_path}")
        with kb_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, path: str | Path | None = None, backup: bool = True) -> Path:
        target = Path(path) if path else self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        if backup and target.exists():
            backup_dir = target.parent / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{target.name}.bak-{_now_backup_stamp()}"
            shutil.copy2(target, backup_path)
        with target.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        self.path = target
        return target

    @property
    def facts(self) -> list[dict[str, Any]]:
        return self.data["facts"]["items"]

    @property
    def rules(self) -> list[dict[str, Any]]:
        return self.data["rules"]["items"]

    @property
    def hypotheses(self) -> list[dict[str, Any]]:
        return self.data["hypotheses"]["items"]

    def fact_ids(self) -> set[str]:
        return {fact["id"] for fact in self.facts}

    def rule_ids(self) -> set[str]:
        return {rule["id"] for rule in self.rules}

    def hypothesis_ids(self) -> set[str]:
        return {hypothesis["id"] for hypothesis in self.hypotheses}

    def get_fact(self, fact_id: str) -> dict[str, Any]:
        for fact in self.facts:
            if fact["id"] == fact_id:
                return fact
        raise EditorError(f"Fato nao encontrado: {fact_id}")

    def get_rule(self, rule_id: str) -> dict[str, Any]:
        for rule in self.rules:
            if rule["id"] == rule_id:
                return rule
        raise EditorError(f"Regra nao encontrada: {rule_id}")

    def next_fact_id(self, inferred: bool = False) -> str:
        prefix = "F_INF_" if inferred else "F"
        numbers: list[int] = []
        for fact in self.facts:
            fact_id = fact["id"]
            if inferred and fact_id.startswith("F_INF_"):
                numbers.append(int(fact_id.rsplit("_", 1)[1]))
            elif not inferred and re.fullmatch(r"F\d+", fact_id):
                numbers.append(int(fact_id[1:]))
        return f"{prefix}{max(numbers, default=0) + 1:02d}"

    def next_rule_id(self) -> str:
        numbers = [int(rule["id"][1:]) for rule in self.rules if re.fullmatch(r"R\d+", rule["id"])]
        return f"R{max(numbers, default=0) + 1:02d}"

    def add_fact(
        self,
        *,
        attribute: str,
        label: str,
        question: str | None = None,
        fact_type: str = "boolean",
        category: str = "desempenho_execucao",
        source: str = "user_input",
        value: Any = None,
        fact_id: str | None = None,
    ) -> dict[str, Any]:
        inferred = source == "inferred" or category == "inferred"
        new_id = fact_id or self.next_fact_id(inferred=inferred)
        fact = {
            "id": new_id,
            "attribute": attribute,
            "label": label,
            "question": question,
            "type": fact_type,
            "category": "inferred" if inferred else category,
            "value": value,
            "source": "inferred" if inferred else source,
        }
        self._validate_fact(fact, creating=True)
        self.facts.append(fact)
        return fact

    def edit_fact(self, fact_id: str, **updates: Any) -> dict[str, Any]:
        fact = self.get_fact(fact_id)
        editable = {"attribute", "label", "question", "type", "category", "value", "source"}
        unknown = set(updates) - editable
        if unknown:
            raise EditorError(f"Campos invalidos para fato: {', '.join(sorted(unknown))}")
        candidate = deepcopy(fact)
        for key, value in updates.items():
            if value is not None:
                candidate[key] = value
        if candidate["source"] == "inferred":
            candidate["category"] = "inferred"
            candidate["question"] = None
        self._validate_fact(candidate, creating=False, original_id=fact_id)
        fact.clear()
        fact.update(candidate)
        return fact

    def remove_fact(self, fact_id: str, force: bool = False) -> RemovalReport:
        self.get_fact(fact_id)
        dependent_rules = self.rules_referencing_fact(fact_id)
        if dependent_rules and not force:
            ids = ", ".join(rule["id"] for rule in dependent_rules)
            raise EditorError(
                f"O fato {fact_id} e usado pelas regras {ids}. "
                "Use --force para remover o fato e essas regras dependentes."
            )
        removed_rule_ids: list[str] = []
        if dependent_rules:
            dependent_ids = {rule["id"] for rule in dependent_rules}
            self.data["rules"]["items"] = [
                rule for rule in self.rules if rule["id"] not in dependent_ids
            ]
            removed_rule_ids = sorted(dependent_ids)
        self.data["facts"]["items"] = [fact for fact in self.facts if fact["id"] != fact_id]
        return RemovalReport(removed_id=fact_id, removed_rules=removed_rule_ids)

    def add_rule(
        self,
        *,
        conditions: list[str],
        conclusion_id: str,
        value: Any = True,
        label: str | None = None,
        conclusion_type: str | None = None,
        priority: int = 1,
        explanation_why: str = "",
        explanation_how: str = "",
        rule_id: str | None = None,
    ) -> dict[str, Any]:
        new_id = rule_id or self.next_rule_id()
        rule = self._build_rule(
            rule_id=new_id,
            conditions=conditions,
            conclusion_id=conclusion_id,
            value=value,
            label=label,
            conclusion_type=conclusion_type,
            priority=priority,
            explanation_why=explanation_why,
            explanation_how=explanation_how,
        )
        self._validate_rule(rule, creating=True)
        self.rules.append(rule)
        return rule

    def edit_rule(self, rule_id: str, **updates: Any) -> dict[str, Any]:
        rule = self.get_rule(rule_id)
        candidate = deepcopy(rule)
        allowed = {
            "conditions",
            "conclusion_id",
            "value",
            "label",
            "conclusion_type",
            "priority",
            "explanation_why",
            "explanation_how",
        }
        unknown = set(updates) - allowed
        if unknown:
            raise EditorError(f"Campos invalidos para regra: {', '.join(sorted(unknown))}")

        conclusion_id = updates.get("conclusion_id")
        value = updates.get("value")
        conclusion_type = updates.get("conclusion_type")
        if conclusion_id is not None or value is not None or conclusion_type is not None:
            current_target = (
                candidate["conclusion"].get("fact_id")
                or candidate["conclusion"].get("hypothesis_id")
            )
            rebuilt = self._build_rule(
                rule_id=rule_id,
                conditions=updates.get("conditions", candidate["conditions"]),
                conclusion_id=conclusion_id or current_target,
                value=candidate["conclusion"]["value"] if value is None else value,
                label=updates.get("label", candidate["label"]),
                conclusion_type=conclusion_type or updates.get(
                    "conclusion_type", candidate["conclusion_type"]
                ),
                priority=updates.get("priority", candidate["priority"]),
                explanation_why=updates.get("explanation_why", candidate["explanation_why"]),
                explanation_how=updates.get("explanation_how", candidate["explanation_how"]),
            )
            rebuilt["fired_count"] = candidate.get("fired_count", 0)
            rebuilt["last_fired"] = candidate.get("last_fired")
            candidate = rebuilt
        else:
            for key, value_to_set in updates.items():
                if value_to_set is not None:
                    candidate[key] = value_to_set

        self._validate_rule(candidate, creating=False, original_id=rule_id)
        rule.clear()
        rule.update(candidate)
        return rule

    def remove_rule(self, rule_id: str) -> dict[str, Any]:
        rule = deepcopy(self.get_rule(rule_id))
        self.data["rules"]["items"] = [item for item in self.rules if item["id"] != rule_id]
        return rule

    def add_rule_from_text(
        self,
        text: str,
        *,
        label: str | None = None,
        priority: int = 1,
        explanation_why: str = "",
        explanation_how: str = "",
        rule_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = self.parse_rule_text(text)
        return self.add_rule(
            conditions=parsed["conditions"],
            conclusion_id=parsed["conclusion_id"],
            value=parsed["value"],
            label=label,
            priority=priority,
            explanation_why=explanation_why,
            explanation_how=explanation_how,
            rule_id=rule_id,
        )

    def rules_referencing_fact(self, fact_id: str) -> list[dict[str, Any]]:
        dependent: list[dict[str, Any]] = []
        for rule in self.rules:
            conclusion = rule["conclusion"]
            if fact_id in rule["conditions"] or conclusion.get("fact_id") == fact_id:
                dependent.append(rule)
        return dependent

    def validate_integrity(self) -> None:
        fact_ids = self.fact_ids()
        hypothesis_ids = self.hypothesis_ids()
        errors: list[str] = []
        for fact in self.facts:
            try:
                self._validate_fact(fact, creating=False, original_id=fact["id"])
            except EditorError as error:
                errors.append(f"Fato {fact.get('id', '?')}: {error}")
        for rule in self.rules:
            try:
                self._validate_rule(rule, creating=False, original_id=rule["id"])
            except EditorError as error:
                errors.append(f"Regra {rule.get('id', '?')}: {error}")
            for condition_id in rule.get("conditions", []):
                if condition_id not in fact_ids:
                    errors.append(f"Regra {rule['id']}: condicao inexistente {condition_id}")
            conclusion = rule.get("conclusion", {})
            if "fact_id" in conclusion and conclusion["fact_id"] not in fact_ids:
                errors.append(f"Regra {rule['id']}: fato conclusivo inexistente {conclusion['fact_id']}")
            if "hypothesis_id" in conclusion and conclusion["hypothesis_id"] not in hypothesis_ids:
                errors.append(
                    f"Regra {rule['id']}: hipotese conclusiva inexistente {conclusion['hypothesis_id']}"
                )
        if errors:
            raise EditorError("\n".join(errors))

    @staticmethod
    def parse_rule_text(text: str) -> dict[str, Any]:
        match = RULE_TEXT_RE.match(text)
        if not match:
            raise EditorError("Use o formato: SE F01 E F02 ENTAO H1=true")
        conditions = [
            condition.strip()
            for condition in re.split(r"\s+E\s+", match.group("conditions"), flags=re.IGNORECASE)
            if condition.strip()
        ]
        conclusion_text = match.group("conclusion").strip()
        if "=" in conclusion_text:
            conclusion_id, raw_value = [part.strip() for part in conclusion_text.split("=", 1)]
            value = _parse_scalar(raw_value)
        else:
            conclusion_id = conclusion_text
            value = True
        return {"conditions": conditions, "conclusion_id": conclusion_id, "value": value}

    def _validate_fact(
        self, fact: dict[str, Any], *, creating: bool, original_id: str | None = None
    ) -> None:
        fact_id = fact.get("id")
        if not isinstance(fact_id, str) or not FACT_ID_RE.fullmatch(fact_id):
            raise EditorError("ID de fato invalido. Use F01, F32 ou F_INF_03.")
        if creating and fact_id in self.fact_ids():
            raise EditorError(f"Ja existe um fato com ID {fact_id}")
        if not creating and original_id and fact_id != original_id:
            raise EditorError("Edicao de ID de fato nao e permitida; remova e cadastre outro.")
        attribute = fact.get("attribute")
        if not isinstance(attribute, str) or not ATTRIBUTE_RE.fullmatch(attribute):
            raise EditorError("attribute deve estar em snake_case, ex.: driver_gpu_desatualizado")
        if not fact.get("label"):
            raise EditorError("label e obrigatorio")
        if fact.get("type") not in FACT_TYPES:
            raise EditorError(f"type deve ser um de: {', '.join(sorted(FACT_TYPES))}")
        if fact.get("category") not in FACT_CATEGORIES:
            raise EditorError(f"category deve ser um de: {', '.join(sorted(FACT_CATEGORIES))}")
        if fact.get("source") not in FACT_SOURCES:
            raise EditorError(f"source deve ser um de: {', '.join(sorted(FACT_SOURCES))}")
        if fact["source"] == "user_input" and not fact.get("question"):
            raise EditorError("fatos de usuario precisam de question")
        if fact["source"] == "inferred" and fact.get("question") is not None:
            raise EditorError("fatos inferidos devem ter question = null")

    def _build_rule(
        self,
        *,
        rule_id: str,
        conditions: list[str],
        conclusion_id: str,
        value: Any,
        label: str | None,
        conclusion_type: str | None,
        priority: int,
        explanation_why: str,
        explanation_how: str,
    ) -> dict[str, Any]:
        inferred_type = conclusion_type or (
            "hypothesis" if conclusion_id.startswith("H") else "intermediate"
        )
        if inferred_type == "hypothesis":
            conclusion = {"hypothesis_id": conclusion_id, "value": value}
        elif inferred_type == "intermediate":
            conclusion = {"fact_id": conclusion_id, "value": value}
        else:
            raise EditorError("conclusion_type deve ser 'intermediate' ou 'hypothesis'")
        readable_label = label or (
            f"SE {' E '.join(conditions)} ENTAO {conclusion_id} = {value}"
        )
        return {
            "id": rule_id,
            "label": readable_label,
            "conditions": conditions,
            "conclusion": conclusion,
            "conclusion_type": inferred_type,
            "priority": int(priority),
            "explanation_why": explanation_why or f"Estou avaliando a regra {rule_id}.",
            "explanation_how": explanation_how
            or f"A regra {rule_id} foi ativada pelas condicoes: {', '.join(conditions)}.",
            "fired_count": 0,
            "last_fired": None,
        }

    def _validate_rule(
        self, rule: dict[str, Any], *, creating: bool, original_id: str | None = None
    ) -> None:
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not RULE_ID_RE.fullmatch(rule_id):
            raise EditorError("ID de regra invalido. Use R01, R22 etc.")
        if creating and rule_id in self.rule_ids():
            raise EditorError(f"Ja existe uma regra com ID {rule_id}")
        if not creating and original_id and rule_id != original_id:
            raise EditorError("Edicao de ID de regra nao e permitida; remova e cadastre outra.")
        conditions = rule.get("conditions")
        if not isinstance(conditions, list) or not conditions:
            raise EditorError("conditions deve conter pelo menos um fato")
        fact_ids = self.fact_ids()
        missing = [condition for condition in conditions if condition not in fact_ids]
        if missing:
            raise EditorError(f"Condicoes inexistentes: {', '.join(missing)}")
        if rule.get("conclusion_type") not in {"intermediate", "hypothesis"}:
            raise EditorError("conclusion_type deve ser 'intermediate' ou 'hypothesis'")
        conclusion = rule.get("conclusion", {})
        if rule["conclusion_type"] == "intermediate":
            fact_id = conclusion.get("fact_id")
            if fact_id not in fact_ids:
                raise EditorError(f"Fato de conclusao inexistente: {fact_id}")
        if rule["conclusion_type"] == "hypothesis":
            hypothesis_id = conclusion.get("hypothesis_id")
            if hypothesis_id not in self.hypothesis_ids():
                raise EditorError(f"Hipotese de conclusao inexistente: {hypothesis_id}")
        priority = rule.get("priority")
        if not isinstance(priority, int) or not 1 <= priority <= 5:
            raise EditorError("priority deve ser inteiro de 1 a 5")
        if not rule.get("label"):
            raise EditorError("label e obrigatorio")
        if not rule.get("explanation_why"):
            raise EditorError("explanation_why e obrigatorio")
        if not rule.get("explanation_how"):
            raise EditorError("explanation_how e obrigatorio")


def _csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Editor CRUD da Base de Conhecimento do MechApe."
    )
    parser.add_argument(
        "--base",
        default=str(DEFAULT_KB_PATH),
        help="Caminho do arquivo JSON da base de conhecimento.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Nao cria copia .bak antes de salvar alteracoes.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("interactive", help="Abre o menu interativo.")

    list_parser = subparsers.add_parser("list", help="Lista fatos ou regras.")
    list_parser.add_argument("kind", choices=["facts", "rules"])

    validate_parser = subparsers.add_parser("validate", help="Valida referencias internas.")
    validate_parser.set_defaults(validate=True)

    add_fact = subparsers.add_parser("add-fact", help="Cadastra um fato.")
    add_fact.add_argument("--id", dest="fact_id")
    add_fact.add_argument("--attribute", required=True)
    add_fact.add_argument("--label", required=True)
    add_fact.add_argument("--question")
    add_fact.add_argument("--type", default="boolean", dest="fact_type")
    add_fact.add_argument("--category", default="desempenho_execucao")
    add_fact.add_argument("--source", default="user_input")
    add_fact.add_argument("--value")

    edit_fact = subparsers.add_parser("edit-fact", help="Edita um fato existente.")
    edit_fact.add_argument("fact_id")
    edit_fact.add_argument("--attribute")
    edit_fact.add_argument("--label")
    edit_fact.add_argument("--question")
    edit_fact.add_argument("--type", dest="fact_type")
    edit_fact.add_argument("--category")
    edit_fact.add_argument("--source")
    edit_fact.add_argument("--value")

    remove_fact = subparsers.add_parser("remove-fact", help="Remove um fato.")
    remove_fact.add_argument("fact_id")
    remove_fact.add_argument("--force", action="store_true")

    add_rule = subparsers.add_parser("add-rule", help="Cadastra uma regra.")
    add_rule.add_argument("--id", dest="rule_id")
    add_rule.add_argument("--text", help="Formato: SE F01 E F02 ENTAO H1=true")
    add_rule.add_argument("--conditions", help="IDs separados por virgula. Ex.: F01,F23")
    add_rule.add_argument("--conclusion-id")
    add_rule.add_argument("--value", default="true")
    add_rule.add_argument("--label")
    add_rule.add_argument("--conclusion-type", choices=["intermediate", "hypothesis"])
    add_rule.add_argument("--priority", type=int, default=1)
    add_rule.add_argument("--why", default="", dest="explanation_why")
    add_rule.add_argument("--how", default="", dest="explanation_how")

    edit_rule = subparsers.add_parser("edit-rule", help="Edita uma regra existente.")
    edit_rule.add_argument("rule_id")
    edit_rule.add_argument("--conditions", help="IDs separados por virgula. Ex.: F01,F23")
    edit_rule.add_argument("--conclusion-id")
    edit_rule.add_argument("--value")
    edit_rule.add_argument("--label")
    edit_rule.add_argument("--conclusion-type", choices=["intermediate", "hypothesis"])
    edit_rule.add_argument("--priority", type=int)
    edit_rule.add_argument("--why", dest="explanation_why")
    edit_rule.add_argument("--how", dest="explanation_how")

    remove_rule = subparsers.add_parser("remove-rule", help="Remove uma regra.")
    remove_rule.add_argument("rule_id")

    return parser


def run_interactive(editor: KnowledgeBaseEditor, *, backup: bool) -> None:
    actions = {
        "1": "list_facts",
        "2": "list_rules",
        "3": "add_fact",
        "4": "edit_fact",
        "5": "remove_fact",
        "6": "add_rule",
        "7": "edit_rule",
        "8": "remove_rule",
        "9": "validate",
        "0": "exit",
    }
    while True:
        sys.stdout.write("\033[H\033[2J") 
        exibir_cabecalho()
        
        print(f"{AZUL_BRILHANTE}  1. Listar fatos{RESET}")
        print(f"{AZUL_BRILHANTE}  2. Listar regras{RESET}")
        print(f"{AZUL_BRILHANTE}  3. Cadastrar fato{RESET}")
        print(f"{AZUL_BRILHANTE}  4. Editar fato{RESET}")
        print(f"{AZUL_BRILHANTE}  5. Remover fato{RESET}")
        print(f"{AZUL_BRILHANTE}  6. Cadastrar regra{RESET}")
        print(f"{AZUL_BRILHANTE}  7. Editar regra{RESET}")
        print(f"{AZUL_BRILHANTE}  8. Remover regra{RESET}")
        print(f"{AZUL_BRILHANTE}  9. Validar integridade{RESET}")
        print(f"{AZUL}  0. Sair (Desligar Terminal){RESET}\n")
        
        choice = input(f"{AZUL}SELECIONE UMA OPÇÃO DO EDITOR_> {RESET}").strip()
        action = actions.get(choice)
        
        if action == "exit":
            print_retro(f"\n{AZUL}[SISTEMA]: Finalizando buffers do editor... Desligando. Adeus.{RESET}")
            break
        
        try:
            if action == "list_facts":
                print_retro(f"\n{AZUL_BRILHANTE}--- FATOS CADASTRADOS ---{RESET}")
                for fact in editor.facts:
                    print(f"{AZUL}{fact['id']} | {fact['attribute']} | {fact['label']}{RESET}")
            elif action == "list_rules":
                print_retro(f"\n{AZUL_BRILHANTE}--- REGRAS CADASTRADAS ---{RESET}")
                for rule in editor.rules:
                    print(f"{AZUL}{_format_rule(rule)}{RESET}")
            elif action == "add_fact":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Iniciando cadastro de fato...{RESET}")
                fact = editor.add_fact(
                    fact_id=input(f"{AZUL}ID (vazio = automático): {RESET}").strip() or None,
                    attribute=input(f"{AZUL}Attribute (obrigatório: snake_case, ex: falha_rede): {RESET}").strip(),
                    label=input(f"{AZUL}Rótulo (descrição legível): {RESET}").strip(),
                    question=input(f"{AZUL}Pergunta (vazio para inferido): {RESET}").strip() or None,
                    fact_type=prompt_choice("Tipo de dado do fato:", sorted(list(FACT_TYPES)), "boolean"),
                    category=prompt_choice("Categoria do fato:", sorted(list(FACT_CATEGORIES)), "desempenho_execucao"),
                    source=prompt_choice("Fonte do fato:", sorted(list(FACT_SOURCES)), "user_input"),
                )
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Fato cadastrado com ID: {fact['id']}{RESET}")
            elif action == "edit_fact":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Editando fato existente...{RESET}")
                fact_id = input(f"{AZUL}ID do fato: {RESET}").strip()
                fact = editor.get_fact(fact_id)
                
                attribute = input(f"{AZUL}Attribute (obrigatório: snake_case) [{fact['attribute']}]: {RESET}").strip() or None
                label = input(f"{AZUL}Rótulo [{fact['label']}]: {RESET}").strip() or None
                question = input(f"{AZUL}Pergunta [{fact.get('question')}]: {RESET}").strip() or None
                
                fact_type = prompt_choice_edit("Novo Tipo", sorted(list(FACT_TYPES)), fact['type'])
                category = prompt_choice_edit("Nova Categoria", sorted(list(FACT_CATEGORIES)), fact['category'])
                source = prompt_choice_edit("Nova Fonte", sorted(list(FACT_SOURCES)), fact['source'])

                updates = {
                    "attribute": attribute,
                    "label": label,
                    "question": question,
                    "type": fact_type,
                    "category": category,
                    "source": source,
                }
                updates = {k: v for k, v in updates.items() if v is not None}
                
                editor.edit_fact(fact_id, **updates)
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Fato {fact_id} editado.{RESET}")
            elif action == "remove_fact":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Removendo fato existente...{RESET}")
                report = editor.remove_fact(
                    input(f"{AZUL}ID do fato: {RESET}").strip(),
                    force=input(f"{AZUL}Remover regras dependentes? [s/N]: {RESET}").strip().lower() == "s",
                )
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Fato removido: {report.removed_id}{RESET}")
                if report.removed_rules:
                    print_retro(f"{AZUL_BRILHANTE}[AVISO]: Regras dependentes removidas: {', '.join(report.removed_rules)}{RESET}")
            elif action == "add_rule":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Iniciando cadastro de regra...{RESET}")
                rule = editor.add_rule_from_text(
                    input(f"{AZUL}Regra (formato obrigatório: SE F01 E F02 ENTÃO H1=true): {RESET}").strip(),
                    label=input(f"{AZUL}Rótulo: {RESET}").strip() or None,
                    priority=int(prompt_choice("Prioridade da Regra:", ["1", "2", "3", "4", "5"], "1")),
                    explanation_why=input(f"{AZUL}Explicação Por que?: {RESET}").strip(),
                    explanation_how=input(f"{AZUL}Explicação Como?: {RESET}").strip(),
                )
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Regra cadastrada com ID: {rule['id']}{RESET}")
            elif action == "edit_rule":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Editando regra existente...{RESET}")
                rule_id = input(f"{AZUL}ID da regra: {RESET}").strip()
                rule = editor.get_rule(rule_id)
                conditions = input(f"{AZUL}Condições CSV [{','.join(rule['conditions'])}]: {RESET}").strip()
                current_target = rule["conclusion"].get("fact_id") or rule["conclusion"].get(
                    "hypothesis_id"
                )
                
                priority_str = prompt_choice_edit("Nova Prioridade", ["1", "2", "3", "4", "5"], str(rule['priority']))

                updates = {
                    "conditions": _csv(conditions),
                    "conclusion_id": input(f"{AZUL}Conclusão [{current_target}]: {RESET}").strip() or None,
                    "label": input(f"{AZUL}Rótulo [{rule['label']}]: {RESET}").strip() or None,
                    "priority": int(priority_str) if priority_str else None,
                    "explanation_why": input(f"{AZUL}Explicação Por que? [manter]: {RESET}").strip() or None,
                    "explanation_how": input(f"{AZUL}Explicação Como? [manter]: {RESET}").strip() or None,
                }
                
                updates = {k: v for k, v in updates.items() if v is not None}
                
                editor.edit_rule(rule_id, **updates)
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Regra {rule_id} editada.{RESET}")
            elif action == "remove_rule":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Removendo regra existente...{RESET}")
                removed = editor.remove_rule(input(f"{AZUL}ID da regra: {RESET}").strip())
                editor.save(backup=backup)
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Regra {removed['id']} removida.{RESET}")
            elif action == "validate":
                print_retro(f"\n{AZUL_BRILHANTE}[SISTEMA]: Iniciando validação de integridade...{RESET}")
                editor.validate_integrity()
                print_retro(f"{AZUL_BRILHANTE}[SUCESSO]: Integridade válida. Todas as referências estão corretas.{RESET}")
            elif action is None:
                print(f"{AZUL}[ERRO]: Opção inválida.{RESET}")
        except EditorError as error:
            print(f"\n{AZUL_BRILHANTE}[ERRO DE OPERAÇÃO]: {error}{RESET}")
        
        if action:
            input(f"\n{AZUL}Pressione [ENTER] para retornar ao menu principal...{RESET}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    editor = KnowledgeBaseEditor(args.base)
    backup = not args.no_backup

    try:
        if args.command in {None, "interactive"}:
            run_interactive(editor, backup=backup)
            return 0
        if args.command == "list":
            if args.kind == "facts":
                for fact in editor.facts:
                    print(f"{fact['id']} | {fact['attribute']} | {fact['label']}")
            else:
                for rule in editor.rules:
                    print(_format_rule(rule))
            return 0
        if args.command == "validate":
            editor.validate_integrity()
            print("Integridade valida.")
            return 0
        if args.command == "add-fact":
            fact = editor.add_fact(
                fact_id=args.fact_id,
                attribute=args.attribute,
                label=args.label,
                question=args.question,
                fact_type=args.fact_type,
                category=args.category,
                source=args.source,
                value=_parse_scalar(args.value),
            )
            editor.save(backup=backup)
            _print_json(fact)
            return 0
        if args.command == "edit-fact":
            fact = editor.edit_fact(
                args.fact_id,
                attribute=args.attribute,
                label=args.label,
                question=args.question,
                type=args.fact_type,
                category=args.category,
                source=args.source,
                value=_parse_scalar(args.value) if args.value is not None else None,
            )
            editor.save(backup=backup)
            _print_json(fact)
            return 0
        if args.command == "remove-fact":
            report = editor.remove_fact(args.fact_id, force=args.force)
            editor.save(backup=backup)
            _print_json({"removed_id": report.removed_id, "removed_rules": report.removed_rules})
            return 0
        if args.command == "add-rule":
            if args.text:
                rule = editor.add_rule_from_text(
                    args.text,
                    label=args.label,
                    priority=args.priority,
                    explanation_why=args.explanation_why,
                    explanation_how=args.explanation_how,
                    rule_id=args.rule_id,
                )
            else:
                conditions = _csv(args.conditions)
                if not conditions or not args.conclusion_id:
                    raise EditorError("Informe --text ou --conditions junto com --conclusion-id")
                rule = editor.add_rule(
                    rule_id=args.rule_id,
                    conditions=conditions,
                    conclusion_id=args.conclusion_id,
                    value=_parse_scalar(args.value),
                    label=args.label,
                    conclusion_type=args.conclusion_type,
                    priority=args.priority,
                    explanation_why=args.explanation_why,
                    explanation_how=args.explanation_how,
                )
            editor.save(backup=backup)
            _print_json(rule)
            return 0
        if args.command == "edit-rule":
            rule = editor.edit_rule(
                args.rule_id,
                conditions=_csv(args.conditions),
                conclusion_id=args.conclusion_id,
                value=_parse_scalar(args.value) if args.value is not None else None,
                label=args.label,
                conclusion_type=args.conclusion_type,
                priority=args.priority,
                explanation_why=args.explanation_why,
                explanation_how=args.explanation_how,
            )
            editor.save(backup=backup)
            _print_json(rule)
            return 0
        if args.command == "remove-rule":
            removed = editor.remove_rule(args.rule_id)
            editor.save(backup=backup)
            _print_json(removed)
            return 0
    except EditorError as error:
        parser.exit(2, f"Erro: {error}\n")

    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print(f"\n{AZUL}[SISTEMA]: Interrupção forçada pelo operador. Encerrando o Editor.{RESET}")