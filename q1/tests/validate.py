"""
Valida knowledge_base.json e imprime um relatorio de sanidade.

Uso:
    python validate.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from q1.editor import KnowledgeBaseError, validate_references

try:
    import jsonschema
except ImportError:
    jsonschema = None


BASE_DIR = Path(__file__).resolve().parent


def main() -> int:
    with (BASE_DIR / "knowledge_base.json").open(encoding="utf-8") as f:
        kb = json.load(f)

    with (BASE_DIR / "knowledge_base.schema.json").open(encoding="utf-8") as f:
        schema = json.load(f)

    print("=" * 60)
    print("  MechApe - Validacao da Base de Conhecimento")
    print("=" * 60)

    if jsonschema is None:
        print("\n!  Pacote jsonschema nao instalado; validacao completa do schema foi pulada.")
        print("   As checagens de integridade referencial serao executadas.\n")
    else:
        try:
            jsonschema.validate(instance=kb, schema=schema)
            print("\nOK Estrutura JSON valida conforme o schema.\n")
        except jsonschema.ValidationError as exc:
            print(f"\nERRO de validacao: {exc.message}")
            print(f"Campo: {' > '.join(str(p) for p in exc.absolute_path)}")
            return 1

    facts = kb["facts"]["items"]
    rules = kb["rules"]["items"]
    hypotheses = kb["hypotheses"]["items"]

    user_facts = [fact for fact in facts if fact["source"] == "user_input"]
    inferred_facts = [fact for fact in facts if fact["source"] == "inferred"]

    print(f"  Dominio        : {kb['_meta']['domain']}")
    print(f"  Schema versao  : {kb['_meta']['schema_version']}")
    print()
    print(f"  Fatos totais   : {len(facts):>3}")
    print(f"    Usuario      : {len(user_facts):>3}  (requisito: >= 30 -> {'OK' if len(user_facts) >= 30 else 'FALHA'})")
    print(f"    Inferidos    : {len(inferred_facts):>3}")
    print(f"  Hipoteses      : {len(hypotheses):>3}  (requisito: >=  5 -> {'OK' if len(hypotheses) >= 5 else 'FALHA'})")
    print(f"  Regras         : {len(rules):>3}  (requisito: >= 20 -> {'OK' if len(rules) >= 20 else 'FALHA'})")
    print()

    print("  Verificando integridade referencial das regras...")
    try:
        validate_references(kb)
        print("  OK Todas as referencias de fatos e hipoteses sao validas.")
    except KnowledgeBaseError as exc:
        print(f"  ERRO {exc}")
        return 1

    print()
    print("  Cobertura de hipoteses pelas regras:")
    covered = {
        rule["conclusion"]["hypothesis_id"]
        for rule in rules
        if "hypothesis_id" in rule["conclusion"]
    }

    for hypothesis in hypotheses:
        status = "OK" if hypothesis["id"] in covered else "SEM REGRA"
        print(f"  {status:<9} {hypothesis['id']}: {hypothesis['label']}")

    print()
    print("  Regras por hipotese alvo:")
    hyp_counter: Counter[str] = Counter()
    for rule in rules:
        conclusion = rule["conclusion"]
        if "hypothesis_id" in conclusion:
            hyp_counter[conclusion["hypothesis_id"]] += 1
        else:
            hyp_counter["(intermediaria)"] += 1

    for hyp_id, count in sorted(hyp_counter.items()):
        bar = "#" * count
        print(f"  {hyp_id:<20} {bar} {count}")

    print()
    print("=" * 60)
    print("  Validacao concluida.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
