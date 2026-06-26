"""
Editor CLI da base de conhecimento do MechApe.

Permite cadastrar fatos, cadastrar regras no formato SE...ENTAO,
editar regras existentes e remover regras sem alterar o codigo-fonte.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_KB_PATH = BASE_DIR / "tests" / "knowledge_base.json"

FACT_CATEGORIES = (
    "desempenho_execucao",
    "launchers",
    "software_so",
    "overlays",
    "hardware",
    "inferred",
)
FACT_TYPES = ("boolean", "numeric", "categorical")
CONCLUSION_TYPES = ("intermediate", "hypothesis")


class KnowledgeBaseError(ValueError):
    """Erro de validacao da base de conhecimento."""


def load_kb(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_kb(kb: dict[str, Any], path: Path, backup: bool = True) -> None:
    if backup and path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_suffix(path.suffix + f".bak_{timestamp}")
        shutil.copy2(path, backup_path)

    with path.open("w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
        f.write("\n")


def facts(kb: dict[str, Any]) -> list[dict[str, Any]]:
    return kb["facts"]["items"]


def rules(kb: dict[str, Any]) -> list[dict[str, Any]]:
    return kb["rules"]["items"]


def hypotheses(kb: dict[str, Any]) -> list[dict[str, Any]]:
    return kb["hypotheses"]["items"]


def ids(items: list[dict[str, Any]]) -> set[str]:
    return {item["id"] for item in items}


def next_numeric_id(existing_ids: set[str], prefix: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    numbers = [int(match.group(1)) for item_id in existing_ids if (match := pattern.match(item_id))]
    return f"{prefix}{max(numbers, default=0) + 1:02d}"


def next_inferred_fact_id(existing_ids: set[str]) -> str:
    pattern = re.compile(r"^F_INF_(\d+)$")
    numbers = [int(match.group(1)) for item_id in existing_ids if (match := pattern.match(item_id))]
    return f"F_INF_{max(numbers, default=0) + 1:02d}"


def ensure_unique(item_id: str, existing_ids: set[str], kind: str) -> None:
    if item_id in existing_ids:
        raise KnowledgeBaseError(f"{kind} '{item_id}' ja existe.")


def ensure_known_facts(kb: dict[str, Any], condition_ids: list[str]) -> None:
    known = ids(facts(kb))
    missing = [condition_id for condition_id in condition_ids if condition_id not in known]
    if missing:
        raise KnowledgeBaseError(f"Fatos inexistentes nas condicoes: {', '.join(missing)}")


def ensure_known_conclusion(kb: dict[str, Any], conclusion_type: str, conclusion_id: str) -> None:
    if conclusion_type == "intermediate" and conclusion_id not in ids(facts(kb)):
        raise KnowledgeBaseError(f"Fato de conclusao '{conclusion_id}' nao existe.")
    if conclusion_type == "hypothesis" and conclusion_id not in ids(hypotheses(kb)):
        raise KnowledgeBaseError(f"Hipotese de conclusao '{conclusion_id}' nao existe.")


def parse_conditions(value: str) -> list[str]:
    conditions = [part.strip() for part in value.split(",") if part.strip()]
    if not conditions:
        raise KnowledgeBaseError("Informe pelo menos uma condicao.")
    return conditions


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "t", "1", "sim", "s", "yes", "y"}:
        return True
    if normalized in {"false", "f", "0", "nao", "não", "n", "no"}:
        return False
    raise argparse.ArgumentTypeError("Use true/false ou sim/nao.")


def add_fact(kb: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    existing_fact_ids = ids(facts(kb))
    source = args.source
    fact_id = args.id

    if not fact_id:
        fact_id = next_inferred_fact_id(existing_fact_ids) if source == "inferred" else next_numeric_id(existing_fact_ids, "F")

    ensure_unique(fact_id, existing_fact_ids, "Fato")
    if args.attribute in {fact["attribute"] for fact in facts(kb)}:
        raise KnowledgeBaseError(f"Atributo '{args.attribute}' ja existe.")
    if source == "inferred" and args.question:
        raise KnowledgeBaseError("Fatos inferidos devem ter pergunta vazia.")
    if source == "user_input" and not args.question:
        raise KnowledgeBaseError("Fatos de entrada do usuario precisam de uma pergunta.")

    fact = {
        "id": fact_id,
        "attribute": args.attribute,
        "label": args.label,
        "question": args.question if source == "user_input" else None,
        "type": args.type,
        "category": args.category,
        "value": None,
        "source": source,
    }
    facts(kb).append(fact)
    return fact


def build_conclusion(conclusion_type: str, conclusion_id: str, value: bool) -> dict[str, Any]:
    key = "fact_id" if conclusion_type == "intermediate" else "hypothesis_id"
    return {key: conclusion_id, "value": value}


def add_rule(kb: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    existing_rule_ids = ids(rules(kb))
    rule_id = args.id or next_numeric_id(existing_rule_ids, "R")

    ensure_unique(rule_id, existing_rule_ids, "Regra")
    conditions = parse_conditions(args.conditions)
    ensure_known_facts(kb, conditions)
    ensure_known_conclusion(kb, args.conclusion_type, args.conclusion_id)

    rule = {
        "id": rule_id,
        "label": args.label,
        "conditions": conditions,
        "conclusion": build_conclusion(args.conclusion_type, args.conclusion_id, args.value),
        "conclusion_type": args.conclusion_type,
        "priority": args.priority,
        "explanation_why": args.explanation_why,
        "explanation_how": args.explanation_how,
        "fired_count": 0,
        "last_fired": None,
    }
    rules(kb).append(rule)
    return rule


def find_rule(kb: dict[str, Any], rule_id: str) -> dict[str, Any]:
    for rule in rules(kb):
        if rule["id"] == rule_id:
            return rule
    raise KnowledgeBaseError(f"Regra '{rule_id}' nao encontrada.")


def edit_rule(kb: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    rule = find_rule(kb, args.id)

    if args.label is not None:
        rule["label"] = args.label
    if args.conditions is not None:
        conditions = parse_conditions(args.conditions)
        ensure_known_facts(kb, conditions)
        rule["conditions"] = conditions
    if args.priority is not None:
        rule["priority"] = args.priority
    if args.explanation_why is not None:
        rule["explanation_why"] = args.explanation_why
    if args.explanation_how is not None:
        rule["explanation_how"] = args.explanation_how

    if args.conclusion_type is not None or args.conclusion_id is not None or args.value is not None:
        conclusion_type = args.conclusion_type or rule["conclusion_type"]
        current_key = "fact_id" if conclusion_type == "intermediate" else "hypothesis_id"
        conclusion_id = args.conclusion_id or rule["conclusion"].get(current_key)
        if not conclusion_id:
            raise KnowledgeBaseError("Informe --conclusion-id ao trocar o tipo da conclusao.")
        conclusion_value = args.value if args.value is not None else rule["conclusion"].get("value", True)
        ensure_known_conclusion(kb, conclusion_type, conclusion_id)
        rule["conclusion_type"] = conclusion_type
        rule["conclusion"] = build_conclusion(conclusion_type, conclusion_id, conclusion_value)

    return rule


def remove_rule(kb: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    rule = find_rule(kb, args.id)
    rules(kb).remove(rule)
    return rule


def validate_references(kb: dict[str, Any]) -> None:
    fact_ids = ids(facts(kb))
    hypothesis_ids = ids(hypotheses(kb))
    rule_ids = ids(rules(kb))

    if len(rule_ids) != len(rules(kb)):
        raise KnowledgeBaseError("Ha regras com IDs duplicados.")
    if len(fact_ids) != len(facts(kb)):
        raise KnowledgeBaseError("Ha fatos com IDs duplicados.")

    for rule in rules(kb):
        missing_conditions = [condition for condition in rule["conditions"] if condition not in fact_ids]
        if missing_conditions:
            raise KnowledgeBaseError(f"Regra {rule['id']} referencia fatos inexistentes: {', '.join(missing_conditions)}")

        conclusion = rule["conclusion"]
        if "fact_id" in conclusion and conclusion["fact_id"] not in fact_ids:
            raise KnowledgeBaseError(f"Regra {rule['id']} conclui fato inexistente: {conclusion['fact_id']}")
        if "hypothesis_id" in conclusion and conclusion["hypothesis_id"] not in hypothesis_ids:
            raise KnowledgeBaseError(f"Regra {rule['id']} conclui hipotese inexistente: {conclusion['hypothesis_id']}")


def print_item(item: dict[str, Any]) -> None:
    print(json.dumps(item, ensure_ascii=False, indent=2))


def list_facts(kb: dict[str, Any]) -> None:
    for fact in facts(kb):
        print(f"{fact['id']:<9} {fact['source']:<10} {fact['category']:<22} {fact['label']}")


def list_rules(kb: dict[str, Any]) -> None:
    for rule in rules(kb):
        conclusion = rule["conclusion"]
        target = conclusion.get("fact_id") or conclusion.get("hypothesis_id")
        se = " E ".join(rule["conditions"])
        print(f"{rule['id']:<5} SE {se} ENTAO {target} ({rule['conclusion_type']}, prioridade {rule['priority']})")


def prompt(required_label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{required_label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Valor obrigatorio.")


def interactive(args: argparse.Namespace) -> None:
    kb_path = args.kb
    kb = load_kb(kb_path)

    while True:
        print("\nEditor MechApe")
        print("1. Listar fatos")
        print("2. Cadastrar fato")
        print("3. Listar regras")
        print("4. Cadastrar regra")
        print("5. Editar regra")
        print("6. Remover regra")
        print("0. Sair")
        choice = input("Opcao: ").strip()

        try:
            if choice == "1":
                list_facts(kb)
            elif choice == "2":
                source = prompt("Fonte (user_input/inferred)", "user_input")
                namespace = argparse.Namespace(
                    id=None,
                    attribute=prompt("Atributo snake_case"),
                    label=prompt("Rotulo"),
                    question=None if source == "inferred" else prompt("Pergunta"),
                    type=prompt("Tipo", "boolean"),
                    category=prompt("Categoria", "inferred" if source == "inferred" else "desempenho_execucao"),
                    source=source,
                )
                item = add_fact(kb, namespace)
                validate_references(kb)
                save_kb(kb, kb_path)
                print_item(item)
            elif choice == "3":
                list_rules(kb)
            elif choice == "4":
                conclusion_type = prompt("Tipo de conclusao (intermediate/hypothesis)", "hypothesis")
                namespace = argparse.Namespace(
                    id=None,
                    label=prompt("Rotulo da regra"),
                    conditions=prompt("Condicoes separadas por virgula (ex: F01,F23)"),
                    conclusion_type=conclusion_type,
                    conclusion_id=prompt("ID da conclusao"),
                    value=True,
                    priority=int(prompt("Prioridade 1-5", "2")),
                    explanation_why=prompt("Explicacao Por que"),
                    explanation_how=prompt("Explicacao Como"),
                )
                item = add_rule(kb, namespace)
                validate_references(kb)
                save_kb(kb, kb_path)
                print_item(item)
            elif choice == "5":
                namespace = argparse.Namespace(
                    id=prompt("ID da regra"),
                    label=input("Novo rotulo (vazio mantem): ").strip() or None,
                    conditions=input("Novas condicoes CSV (vazio mantem): ").strip() or None,
                    conclusion_type=input("Novo tipo de conclusao (vazio mantem): ").strip() or None,
                    conclusion_id=input("Novo ID de conclusao (vazio mantem): ").strip() or None,
                    value=None,
                    priority=None,
                    explanation_why=input("Nova explicacao Por que (vazio mantem): ").strip() or None,
                    explanation_how=input("Nova explicacao Como (vazio mantem): ").strip() or None,
                )
                item = edit_rule(kb, namespace)
                validate_references(kb)
                save_kb(kb, kb_path)
                print_item(item)
            elif choice == "6":
                namespace = argparse.Namespace(id=prompt("ID da regra"))
                item = remove_rule(kb, namespace)
                validate_references(kb)
                save_kb(kb, kb_path)
                print_item(item)
            elif choice == "0":
                return
            else:
                print("Opcao invalida.")
        except (KnowledgeBaseError, ValueError) as exc:
            print(f"Erro: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Editor CLI da base de conhecimento MechApe.")
    parser.add_argument("--kb", type=Path, default=DEFAULT_KB_PATH, help="Caminho do arquivo knowledge_base.json.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("interactive", help="Abre o editor em modo interativo.")
    subparsers.add_parser("list-facts", help="Lista fatos cadastrados.")
    subparsers.add_parser("list-rules", help="Lista regras cadastradas no formato SE...ENTAO.")

    add_fact_parser = subparsers.add_parser("add-fact", help="Cadastra um fato.")
    add_fact_parser.add_argument("--id", help="ID do fato. Se omitido, sera gerado automaticamente.")
    add_fact_parser.add_argument("--attribute", required=True, help="Nome interno em snake_case.")
    add_fact_parser.add_argument("--label", required=True, help="Descricao legivel do fato.")
    add_fact_parser.add_argument("--question", help="Pergunta feita ao usuario. Obrigatoria para user_input.")
    add_fact_parser.add_argument("--type", choices=FACT_TYPES, default="boolean")
    add_fact_parser.add_argument("--category", choices=FACT_CATEGORIES, required=True)
    add_fact_parser.add_argument("--source", choices=("user_input", "inferred"), default="user_input")

    add_rule_parser = subparsers.add_parser("add-rule", help="Cadastra uma regra SE...ENTAO.")
    add_rule_parser.add_argument("--id", help="ID da regra. Se omitido, sera gerado automaticamente.")
    add_rule_parser.add_argument("--label", required=True)
    add_rule_parser.add_argument("--conditions", required=True, help="IDs de fatos separados por virgula: F01,F23.")
    add_rule_parser.add_argument("--conclusion-type", choices=CONCLUSION_TYPES, required=True)
    add_rule_parser.add_argument("--conclusion-id", required=True, help="ID de fato inferido ou hipotese.")
    add_rule_parser.add_argument("--value", type=parse_bool, default=True)
    add_rule_parser.add_argument("--priority", type=int, choices=range(1, 6), default=2)
    add_rule_parser.add_argument("--explanation-why", required=True)
    add_rule_parser.add_argument("--explanation-how", required=True)

    edit_rule_parser = subparsers.add_parser("edit-rule", help="Edita campos de uma regra existente.")
    edit_rule_parser.add_argument("id", help="ID da regra.")
    edit_rule_parser.add_argument("--label")
    edit_rule_parser.add_argument("--conditions", help="IDs de fatos separados por virgula.")
    edit_rule_parser.add_argument("--conclusion-type", choices=CONCLUSION_TYPES)
    edit_rule_parser.add_argument("--conclusion-id")
    edit_rule_parser.add_argument("--value", type=parse_bool)
    edit_rule_parser.add_argument("--priority", type=int, choices=range(1, 6))
    edit_rule_parser.add_argument("--explanation-why")
    edit_rule_parser.add_argument("--explanation-how")

    remove_rule_parser = subparsers.add_parser("remove-rule", help="Remove uma regra existente.")
    remove_rule_parser.add_argument("id", help="ID da regra.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "interactive":
        interactive(args)
        return 0

    try:
        kb = load_kb(args.kb)
        if args.command == "list-facts":
            list_facts(kb)
            return 0
        if args.command == "list-rules":
            list_rules(kb)
            return 0
        if args.command == "add-fact":
            item = add_fact(kb, args)
        elif args.command == "add-rule":
            item = add_rule(kb, args)
        elif args.command == "edit-rule":
            item = edit_rule(kb, args)
        elif args.command == "remove-rule":
            item = remove_rule(kb, args)
        else:
            parser.error("Comando invalido.")

        validate_references(kb)
        save_kb(kb, args.kb)
        print_item(item)
        return 0
    except KnowledgeBaseError as exc:
        parser.exit(2, f"Erro: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
