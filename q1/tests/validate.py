"""
validate.py — Valida knowledge_base.json contra knowledge_base.schema.json
e imprime um relatório de sanidade da base de conhecimento.

Uso: python validate.py
"""

import json
import sys

try:
    import jsonschema
except ImportError:
    print("Instalando jsonschema...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema", "--break-system-packages", "-q"])
    import jsonschema

with open("knowledge_base.json", encoding="utf-8") as f:
    kb = json.load(f)

with open("knowledge_base.schema.json", encoding="utf-8") as f:
    schema = json.load(f)

print("=" * 60)
print("  MechApe — Validação da Base de Conhecimento")
print("=" * 60)

# Validação estrutural
try:
    jsonschema.validate(instance=kb, schema=schema)
    print("\n✓  Estrutura JSON válida conforme o schema.\n")
except jsonschema.ValidationError as e:
    print(f"\n✗  Erro de validação: {e.message}")
    print(f"   Caminho: {' > '.join(str(p) for p in e.absolute_path)}")
    sys.exit(1)

# Relatório de sanidade
facts       = kb["facts"]["items"]
rules       = kb["rules"]["items"]
hypotheses  = kb["hypotheses"]["items"]

fact_ids       = {f["id"] for f in facts}
hypothesis_ids = {h["id"] for h in hypotheses}

user_facts     = [f for f in facts if f["source"] == "user_input"]
inferred_facts = [f for f in facts if f["source"] == "inferred"]

print(f"  Domínio        : {kb['_meta']['domain']}")
print(f"   Schema versão  : {kb['_meta']['schema_version']}")
print()
print(f"  Fatos totais       : {len(facts):>3}  (requisito: ≥ 30 → {'✓' if len(user_facts) >= 30 else '✗'})")
print(f"     ├── Usuário       : {len(user_facts):>3}")
print(f"     └── Inferidos     : {len(inferred_facts):>3}")
print(f"  Hipóteses          : {len(hypotheses):>3}  (requisito: ≥  5 → {'✓' if len(hypotheses) >= 5 else '✗'})")
print(f"  Regras             : {len(rules):>3}  (requisito: ≥ 20 → {'✓' if len(rules) >= 20 else '✗'})")
print()

# Integridade referencial das regras
print("  Verificando integridade referencial das regras...")
errors = []
for rule in rules:
    for cond_id in rule["conditions"]:
        if cond_id not in fact_ids:
            errors.append(f"   ✗  Regra {rule['id']}: condição '{cond_id}' não existe nos fatos.")
    conclusion = rule["conclusion"]
    if "fact_id" in conclusion and conclusion["fact_id"] not in fact_ids:
        errors.append(f"   ✗  Regra {rule['id']}: conclusão aponta para fato '{conclusion['fact_id']}' inexistente.")
    if "hypothesis_id" in conclusion and conclusion["hypothesis_id"] not in hypothesis_ids:
        errors.append(f"   ✗  Regra {rule['id']}: conclusão aponta para hipótese '{conclusion['hypothesis_id']}' inexistente.")

if errors:
    for e in errors:
        print(e)
else:
    print("   ✓  Todas as referências de fatos e hipóteses são válidas.")

# Hipóteses cobertas por regras
print()
print("  Cobertura de hipóteses pelas regras:")
covered = set()
for rule in rules:
    c = rule["conclusion"]
    if "hypothesis_id" in c:
        covered.add(c["hypothesis_id"])

for h in hypotheses:
    status = "✓" if h["id"] in covered else "⚠  SEM REGRA"
    print(f"   {status}  {h['id']}: {h['label']}")

# Distribuição de regras por conclusão
print()
print("  Regras por hipótese alvo:")
from collections import Counter
hyp_counter = Counter()
for rule in rules:
    c = rule["conclusion"]
    if "hypothesis_id" in c:
        hyp_counter[c["hypothesis_id"]] += 1
    else:
        hyp_counter["(intermediária)"] += 1

for hyp_id, count in sorted(hyp_counter.items()):
    bar = "█" * count
    print(f"   {hyp_id:<20} {bar} {count}")

print()
print("=" * 60)
print("  Validação concluída.")
print("=" * 60)