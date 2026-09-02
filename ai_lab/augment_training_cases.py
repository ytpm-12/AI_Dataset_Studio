import argparse
import copy
import json
import random
from pathlib import Path

from benchmark_ollama import deterministic_recommendation, load_json, score_case


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "evaluation_cases.jsonl"
DEFAULT_OUTPUT_DIR = BASE_DIR / "training"
DEFAULT_SCHEMA = BASE_DIR / "recommendation.schema.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Génère des variantes supervisées pour le laboratoire IA.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--variants-per-case", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--validation-ratio", type=float, default=0.15)
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--no-validate-rules", action="store_true")
    return parser.parse_args()


def load_cases(path):
    with Path(path).open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def write_jsonl(path, records):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False) + "\n")


def jitter_int(value, rng, min_value=1, spread=0.25):
    if not isinstance(value, int) or isinstance(value, bool):
        return value
    delta = max(1, int(value * spread))
    return max(min_value, value + rng.randint(-delta, delta))


def jitter_float(value, rng, spread=0.20, min_value=None, max_value=None):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return value
    new_value = float(value) * rng.uniform(1 - spread, 1 + spread)
    if min_value is not None:
        new_value = max(min_value, new_value)
    if max_value is not None:
        new_value = min(max_value, new_value)
    return round(new_value, 4)


def set_distribution(case, rng):
    target = case["profile"].get("target")
    if not target or not target.get("distribution"):
        return
    if case["expected_actions"][0] == "flag_class_imbalance":
        minority = round(rng.uniform(0.003, 0.04), 4)
        target["distribution"] = {"false": round(1 - minority, 4), "true": minority}
    elif case["expected_actions"][0] == "no_action":
        false_ratio = round(rng.uniform(0.42, 0.58), 4)
        target["distribution"] = {"false": false_ratio, "true": round(1 - false_ratio, 4)}


def mutate_column(case, rng):
    column = case["profile"].get("column")
    if not column:
        return
    action = case["expected_actions"][0]
    expected_params = case["expected_parameters"]

    if "missing_ratio" in column:
        if action == "request_human_review" and case["category"] == "missing_values":
            column["missing_ratio"] = round(rng.uniform(0.55, 0.90), 4)
        elif action == "impute_missing":
            column["missing_ratio"] = round(rng.uniform(0.01, 0.45), 4)
        elif action == "no_action":
            column["missing_ratio"] = 0.0

    if "skewness" in column:
        if expected_params.get("strategy") == "median":
            column["skewness"] = round(rng.choice([-1, 1]) * rng.uniform(1.2, 3.2), 4)
        elif expected_params.get("strategy") == "mean":
            column["skewness"] = round(rng.uniform(-0.8, 0.8), 4)

    if "outlier_ratio" in column:
        if expected_params.get("strategy") == "median":
            column["outlier_ratio"] = round(rng.uniform(0.01, 0.12), 4)
        elif action == "review_outliers":
            column["outlier_ratio"] = round(rng.uniform(0.001, 0.03), 4)
        else:
            column["outlier_ratio"] = 0.0

    if "iqr_outlier_ratio" in column:
        column["iqr_outlier_ratio"] = round(rng.uniform(0.001, 0.02), 4)

    if "parseable_as_decimal_comma_ratio" in column:
        column["parseable_as_decimal_comma_ratio"] = round(rng.uniform(0.95, 1.0), 4)

    if "leading_or_trailing_whitespace_ratio" in column:
        column["leading_or_trailing_whitespace_ratio"] = round(rng.uniform(0.03, 0.25), 4)

    if "uppercase_ratio" in column:
        column["uppercase_ratio"] = round(rng.uniform(0.02, 0.20), 4)

    if "format_variants" in column:
        column["format_variants"] = rng.randint(2, 10)

    if "ambiguous_date_ratio" in column:
        column["ambiguous_date_ratio"] = round(rng.uniform(0.51, 0.85), 4)

    if "outside_expected_range_ratio" in column:
        column["outside_expected_range_ratio"] = round(rng.uniform(0.005, 0.08), 4)

    if "negative_ratio" in column:
        column["negative_ratio"] = round(rng.uniform(0.002, 0.05), 4)

    if "values" in column and len(column["values"]) >= 4:
        column["values"] = [round(rng.uniform(0.5, 5.0), 2) for _ in column["values"][:-1]] + [
            round(rng.uniform(60.0, 150.0), 2)
        ]

    if case["id"].startswith("missing_business_context") and "unique_count" in column:
        rows = case["profile"].get("dataset", {}).get("rows", 4000)
        column["unique_count"] = max(1, rows - rng.randint(1, max(2, int(rows * 0.02))))

    for key in ["mean", "median", "q1", "q3", "min", "max"]:
        if key in column and not column.get("expected_range"):
            column[key] = jitter_float(column[key], rng, spread=0.25)


def mutate_dataset(case, rng):
    dataset = case["profile"].get("dataset", {})
    if "rows" in dataset:
        dataset["rows"] = jitter_int(dataset["rows"], rng, min_value=1, spread=0.30)
    if "columns" in dataset:
        dataset["columns"] = jitter_int(dataset["columns"], rng, min_value=1, spread=0.20)
    if "exact_duplicate_ratio" in dataset and case["expected_actions"][0] == "drop_duplicates":
        dataset["exact_duplicate_ratio"] = round(rng.uniform(0.005, 0.12), 4)
        dataset["exact_duplicate_rows"] = max(1, int(dataset.get("rows", 100) * dataset["exact_duplicate_ratio"]))
    elif "exact_duplicate_ratio" in dataset:
        dataset["exact_duplicate_ratio"] = 0.0
        dataset["exact_duplicate_rows"] = 0


def mutate_profile(case, rng):
    mutate_dataset(case, rng)
    mutate_column(case, rng)
    set_distribution(case, rng)

    relationship = case["profile"].get("relationship")
    if relationship and "orphan_ratio" in relationship:
        relationship["orphan_ratio"] = round(rng.uniform(0.003, 0.08), 4)

    possible_duplicates = case["profile"].get("possible_duplicates")
    if possible_duplicates and "pairs" in possible_duplicates:
        possible_duplicates["pairs"] = jitter_int(possible_duplicates["pairs"], rng, min_value=1, spread=0.50)


def augment_case(case, variant_index, rng):
    augmented = copy.deepcopy(case)
    augmented["id"] = f"{case['id']}_aug_{variant_index:03d}"
    augmented["source_case_id"] = case["id"]
    augmented["synthetic"] = True
    augmented["notes"] = f"{case.get('notes', '').rstrip()} Cas augmenté synthétique."
    mutate_profile(augmented, rng)
    return augmented


def split_records(records, rng, train_ratio, validation_ratio):
    shuffled = records[:]
    rng.shuffle(shuffled)
    train_end = int(len(shuffled) * train_ratio)
    validation_end = train_end + int(len(shuffled) * validation_ratio)
    return shuffled[:train_end], shuffled[train_end:validation_end], shuffled[validation_end:]


def validate_with_rules(records, schema):
    failures = []
    for record in records:
        result = deterministic_recommendation(record["profile"])
        scores = score_case(record, result, schema)
        if not all(scores.values()):
            failures.append((record["id"], scores, result))
    return failures


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    base_cases = load_cases(args.input)
    records = []
    for case in base_cases:
        original = copy.deepcopy(case)
        original["source_case_id"] = case["id"]
        original["synthetic"] = False
        records.append(original)
        for variant_index in range(1, max(args.variants_per_case, 0) + 1):
            records.append(augment_case(case, variant_index, rng))

    if not args.no_validate_rules:
        schema = load_json(Path(args.schema))
        failures = validate_with_rules(records, schema)
        if failures:
            for case_id, scores, result in failures[:10]:
                print(f"ECART {case_id} scores={scores} result={json.dumps(result, ensure_ascii=False)}")
            raise SystemExit(f"{len(failures)} cas augmentés ne passent pas les règles.")

    train, validation, test = split_records(records, rng, args.train_ratio, args.validation_ratio)
    output_dir = Path(args.output_dir)
    write_jsonl(output_dir / "cases_augmented.jsonl", records)
    write_jsonl(output_dir / "cases_train.jsonl", train)
    write_jsonl(output_dir / "cases_validation.jsonl", validation)
    write_jsonl(output_dir / "cases_test.jsonl", test)
    print(f"Cas totaux: {len(records)}")
    print(f"Train: {len(train)} | Validation: {len(validation)} | Test: {len(test)}")
    print(f"Dossier: {output_dir}")


if __name__ == "__main__":
    main()
