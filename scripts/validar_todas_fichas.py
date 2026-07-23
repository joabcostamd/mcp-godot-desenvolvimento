#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sota_1.1 — Validador de fichas de behavior.

Valida todos os behavior.json contra o behavior.schema.json
e verifica a presença dos 4 novos campos obrigatórios.

Uso: python scripts/validar_todas_fichas.py [--schema PATH]
"""

import json
import os
import sys


def load_schema(schema_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json_schema(instance, schema):
    """Validação básica contra JSON Schema (sem dependência externa).
    
    Verifica: required fields, type matching, enum values, pattern matching.
    Não implementa o JSON Schema completo — usa jsonschema se disponível.
    """
    errors = []

    try:
        import jsonschema
        validator = jsonschema.Draft202012Validator(schema)
        for err in validator.iter_errors(instance):
            errors.append(f"  - {err.json_path}: {err.message}")
    except ImportError:
        # Fallback: validação manual básica
        errors.extend(_manual_validate(instance, schema))

    return errors


def _manual_validate(instance, schema):
    """Validação manual mínima quando jsonschema não está disponível."""
    errors = []

    if not isinstance(instance, dict):
        return ["  - raiz: esperado object"]

    # Required
    for req in schema.get("required", []):
        if req not in instance:
            errors.append(f"  - {req}: campo obrigatório ausente")

    # Properties
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_name not in instance:
            continue

        value = instance[prop_name]

        # Type check
        expected_type = prop_schema.get("type")
        if expected_type:
            if expected_type == "array" and not isinstance(value, list):
                errors.append(f"  - {prop_name}: esperado array, recebido {type(value).__name__}")
            elif expected_type == "string" and not isinstance(value, str):
                errors.append(f"  - {prop_name}: esperado string, recebido {type(value).__name__}")
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(f"  - {prop_name}: esperado object, recebido {type(value).__name__}")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"  - {prop_name}: esperado integer, recebido {type(value).__name__}")

        # Enum check
        if "enum" in prop_schema and isinstance(value, str):
            if value not in prop_schema["enum"]:
                errors.append(f"  - {prop_name}: '{value}' não está em {prop_schema['enum']}")

        # Pattern check
        if "pattern" in prop_schema and isinstance(value, str):
            import re
            if not re.match(prop_schema["pattern"], value):
                errors.append(f"  - {prop_name}: '{value}' não casa com padrão {prop_schema['pattern']}")

        # MinLength/MaxLength
        if "minLength" in prop_schema and isinstance(value, str):
            if len(value) < prop_schema["minLength"]:
                errors.append(f"  - {prop_name}: comprimento {len(value)} < mínimo {prop_schema['minLength']}")
        if "maxLength" in prop_schema and isinstance(value, str):
            if len(value) > prop_schema["maxLength"]:
                errors.append(f"  - {prop_name}: comprimento {len(value)} > máximo {prop_schema['maxLength']}")

        # Array uniqueItems
        if prop_schema.get("uniqueItems") and isinstance(value, list):
            if len(value) != len(set(value)):
                errors.append(f"  - {prop_name}: contém itens duplicados")

        # Array items pattern
        if expected_type == "array" and isinstance(value, list):
            item_schema = prop_schema.get("items", {})
            item_pattern = item_schema.get("pattern")
            if item_pattern:
                import re
                for i, item in enumerate(value):
                    if isinstance(item, str) and not re.match(item_pattern, item):
                        errors.append(f"  - {prop_name}[{i}]: '{item}' não casa com padrão")

    return errors


def validate_new_fields(instance, valid_behavior_names):
    """Verifica os 4 novos campos obrigatórios."""
    errors = []

    # combina_bem
    if "combina_bem" not in instance:
        errors.append("  - combina_bem: campo ausente")
    elif not isinstance(instance["combina_bem"], list):
        errors.append("  - combina_bem: deve ser array")
    else:
        for i, cb in enumerate(instance["combina_bem"]):
            if not isinstance(cb, str):
                errors.append(f"  - combina_bem[{i}]: deve ser string")
            elif cb not in valid_behavior_names:
                errors.append(f"  - combina_bem[{i}]: '{cb}' não é um behavior existente")

    # custo
    if "custo" not in instance:
        errors.append("  - custo: campo ausente")
    elif instance["custo"] not in ("leve", "medio", "pesado"):
        errors.append(f"  - custo: '{instance.get('custo')}' inválido (esperado: leve|medio|pesado)")

    # verbo_pt
    if "verbo_pt" not in instance:
        errors.append("  - verbo_pt: campo ausente")
    elif not isinstance(instance["verbo_pt"], str) or len(instance["verbo_pt"].strip()) < 2:
        errors.append(f"  - verbo_pt: string muito curta ou inválida")

    # verbo_en
    if "verbo_en" not in instance:
        errors.append("  - verbo_en: campo ausente")
    elif not isinstance(instance["verbo_en"], str) or len(instance["verbo_en"].strip()) < 2:
        errors.append(f"  - verbo_en: string muito curta ou inválida")

    # nivel
    if "nivel" not in instance:
        errors.append("  - nivel: campo ausente")
    elif instance["nivel"] not in ("basico", "intermediario", "avancado"):
        errors.append(f"  - nivel: '{instance.get('nivel')}' inválido (esperado: basico|intermediario|avancado)")

    return errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Valida todas as fichas de behavior")
    parser.add_argument("--schema", default=None,
                        help="Caminho para behavior.schema.json (default: behaviors/behavior.schema.json)")
    parser.add_argument("--only-new-fields", action="store_true",
                        help="Verificar apenas os 4 novos campos (sem validação completa do schema)")
    args = parser.parse_args()

    behaviors_root = os.path.join(os.path.dirname(__file__), "..", "behaviors")
    schema_path = args.schema or os.path.join(behaviors_root, "behavior.schema.json")

    if not os.path.isfile(schema_path):
        print(f"ERRO: Schema não encontrado em {schema_path}")
        sys.exit(1)

    schema = load_schema(schema_path)
    print(f"Schema carregado: {schema_path}")
    print(f"Schema $id: {schema.get('$id', 'N/A')}")
    print()

    # Coleta nomes válidos de behavior (para validação de combina_bem)
    valid_names = set()
    for entry in sorted(os.listdir(behaviors_root)):
        path = os.path.join(behaviors_root, entry)
        if os.path.isdir(path) and os.path.isfile(os.path.join(path, "behavior.json")):
            valid_names.add(entry)

    # Varredura
    total = 0
    passed = 0
    failed = 0
    faltantes = []
    resultados = {}

    for entry in sorted(os.listdir(behaviors_root)):
        path = os.path.join(behaviors_root, entry)
        if not os.path.isdir(path):
            continue
        bjson = os.path.join(path, "behavior.json")
        if not os.path.isfile(bjson):
            continue

        total += 1
        try:
            with open(bjson, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"FAIL [{entry}] JSON inválido: {e}")
            failed += 1
            continue

        errors = []

        # Validação JSON Schema
        if not args.only_new_fields:
            errors.extend(validate_json_schema(data, schema))

        # Validação dos novos campos
        errors.extend(validate_new_fields(data, valid_names))

        if errors:
            print(f"FAIL [{entry}] ({len(errors)} erro(s))")
            for e in errors:
                print(e)
            failed += 1
        else:
            passed += 1

        resultados[entry] = errors

    # Resumo
    print()
    print("=" * 60)
    print(f"RESUMO: {total} behaviors verificados")
    print(f"  PASS: {passed}")
    print(f"  FAIL: {failed}")
    print(f"  Faltantes (sem os 4 novos campos): {len(faltantes)}")
    if faltantes:
        for f in faltantes:
            print(f"    - {f}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ Todos os behaviors passaram na validação.")
        sys.exit(0)


if __name__ == "__main__":
    main()
