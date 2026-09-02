import argparse
import csv
import json
import math
from pathlib import Path

import pandas as pd

from benchmark_ollama import deterministic_recommendation


CSV_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin1")


def parse_args():
    parser = argparse.ArgumentParser(description="Profile des datasets reels et applique les recommandations deterministes.")
    parser.add_argument("inputs", nargs="+", help="Fichiers CSV/XLS/XLSX a profiler.")
    parser.add_argument("--output-jsonl", default="ai_lab/results/real_world_recommendations.jsonl")
    parser.add_argument("--max-rows", type=int, default=100_000)
    parser.add_argument("--intended-use", choices=["classification", "supervised_machine_learning", "distance_based_machine_learning"])
    return parser.parse_args()


def safe_number(value):
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, 6)
    return value


def json_ready(value):
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if hasattr(value, "item"):
        return json_ready(value.item())
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def detect_delimiter(path, encoding):
    sample = path.read_text(encoding=encoding, errors="replace")[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,|\t,").delimiter
    except csv.Error:
        if sample.count(";") >= sample.count(","):
            return ";"
        return ","


def read_csv(path, max_rows):
    last_error = None
    for encoding in CSV_ENCODINGS:
        try:
            delimiter = detect_delimiter(path, encoding)
            frame = pd.read_csv(path, sep=delimiter, encoding=encoding, nrows=max_rows)
            return frame, {"encoding": encoding, "delimiter": delimiter}
        except UnicodeDecodeError as error:
            last_error = error
        except pd.errors.ParserError as error:
            last_error = error
    raise RuntimeError(f"Impossible de lire le CSV {path}: {last_error}")


def read_dataset(path, max_rows):
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return read_csv(path, max_rows)
    if suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(path, nrows=max_rows)
        return frame, {"encoding": None, "delimiter": None}
    raise ValueError(f"Format non supporte pour ce profiler: {suffix}")


def dtype_label(series):
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "float64"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "string"


def ratio(mask, total):
    if total == 0:
        return 0.0
    return round(float(mask.sum()) / float(total), 6)


def parseable_integer_ratio(values):
    non_null = values.dropna().astype(str).str.strip()
    if len(non_null) == 0:
        return 0.0
    parsed = non_null.str.fullmatch(r"[+-]?\d+")
    return round(float(parsed.sum()) / float(len(non_null)), 6)


def parseable_decimal_comma_ratio(values):
    non_null = values.dropna().astype(str).str.strip()
    if len(non_null) == 0:
        return 0.0
    parsed = non_null.str.fullmatch(r"[+-]?\d+(,\d+)?")
    return round(float(parsed.sum()) / float(len(non_null)), 6)


def detected_date_formats(values):
    non_null = values.dropna().astype(str).str.strip()
    if len(non_null) == 0:
        return {}
    formats = {
        "YYYY-MM-DD": non_null.str.match(r"^\d{4}-\d{2}-\d{2}").sum(),
        "DD/MM/YYYY": non_null.str.match(r"^\d{2}/\d{2}/\d{4}$").sum(),
        "ISO_DATETIME": non_null.str.match(r"^\d{4}-\d{2}-\d{2}T").sum(),
    }
    result = {}
    for name, count in formats.items():
        if count:
            result[name] = round(float(count) / float(len(non_null)), 6)
    return result


def string_profile(series, column):
    values = series.dropna().astype(str)
    total = len(series)
    non_null = len(values)
    column["unique_count"] = int(values.nunique(dropna=True))
    if non_null:
        modes = values.mode(dropna=True)
        if not modes.empty:
            most_frequent = modes.iloc[0]
            column["most_frequent"] = most_frequent
            column["most_frequent_ratio"] = round(float((values == most_frequent).sum()) / float(non_null), 6)
        column["examples"] = values.drop_duplicates().head(5).tolist()
        stripped = values.str.strip()
        column["leading_or_trailing_whitespace_ratio"] = ratio(values != stripped, non_null)
        has_letters = values.str.contains(r"[A-Za-zÀ-ÖØ-öø-ÿ]", regex=True, na=False)
        uppercase = values.str.fullmatch(r"[A-ZÀ-Ö0-9 _./:+-]+", na=False)
        column["uppercase_ratio"] = ratio(has_letters & uppercase, non_null)
        normalized_unique_count = stripped.str.lower().nunique(dropna=True)
        if normalized_unique_count < column["unique_count"]:
            column["normalized_unique_count"] = int(normalized_unique_count)

    int_ratio = parseable_integer_ratio(series)
    decimal_ratio = parseable_decimal_comma_ratio(series)
    if int_ratio >= 0.95:
        column["parseable_as_integer_ratio"] = int_ratio
    has_decimal_comma = series.dropna().astype(str).str.contains(",", regex=False).any()
    if has_decimal_comma and decimal_ratio >= 0.95:
        column["parseable_as_decimal_comma_ratio"] = decimal_ratio

    date_formats = detected_date_formats(series)
    if date_formats:
        column["detected_formats"] = date_formats

    bool_values = {item.lower() for item in values.str.strip().drop_duplicates().head(20)}
    if bool_values and bool_values.issubset({"yes", "no", "true", "false", "1", "0"}):
        column["unique_values"] = sorted(bool_values)


def numeric_profile(series, column):
    numeric = pd.to_numeric(series, errors="coerce")
    non_null = numeric.dropna()
    if non_null.empty:
        return
    column["min"] = safe_number(non_null.min())
    column["max"] = safe_number(non_null.max())
    column["mean"] = safe_number(non_null.mean())
    column["median"] = safe_number(non_null.median())
    column["skewness"] = safe_number(non_null.skew()) if len(non_null) > 2 else 0.0
    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)
    iqr = q3 - q1
    column["q1"] = safe_number(q1)
    column["q3"] = safe_number(q3)
    if iqr > 0:
        outliers = (non_null < q1 - 1.5 * iqr) | (non_null > q3 + 1.5 * iqr)
        column["iqr_outlier_ratio"] = round(float(outliers.sum()) / float(len(series)), 6)
        column["outlier_ratio"] = column["iqr_outlier_ratio"]


def build_column_profile(frame, column_name, intended_use):
    series = frame[column_name]
    profile = {
        "dataset": {
            "rows": int(len(frame)),
            "columns": int(len(frame.columns)),
        },
        "column": {
            "name": str(column_name),
            "dtype": dtype_label(series),
            "missing_ratio": round(float(series.isna().sum()) / float(len(series)), 6) if len(series) else 0.0,
        },
    }
    if intended_use:
        profile["dataset"]["intended_use"] = intended_use

    column = profile["column"]
    if pd.api.types.is_numeric_dtype(series):
        numeric_profile(series, column)
    else:
        string_profile(series, column)
    return profile


def build_dataset_profile(frame, intended_use):
    profile = {
        "dataset": {
            "rows": int(len(frame)),
            "columns": int(len(frame.columns)),
            "missing_ratio": round(float(frame.isna().sum().sum()) / float(frame.size), 6) if frame.size else 0.0,
            "exact_duplicate_rows": int(frame.duplicated().sum()),
        }
    }
    rows = len(frame)
    profile["dataset"]["exact_duplicate_ratio"] = round(float(profile["dataset"]["exact_duplicate_rows"]) / float(rows), 6) if rows else 0.0
    if intended_use:
        profile["dataset"]["intended_use"] = intended_use
    return profile


def recommendation_record(file_path, scope, profile, read_info):
    return {
        "file": str(file_path),
        "scope": scope,
        "read_info": read_info,
        "profile": profile,
        "recommendation": deterministic_recommendation(profile),
    }


def main():
    args = parse_args()
    output_path = Path(args.output_jsonl)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for raw_path in args.inputs:
        path = Path(raw_path)
        print(f"\nFichier: {path}")
        try:
            frame, read_info = read_dataset(path, args.max_rows)
        except Exception as error:
            print(f"  ERREUR lecture: {error}")
            records.append({"file": str(path), "error": str(error)})
            continue

        print(f"  Lignes profilees: {len(frame)} | Colonnes: {len(frame.columns)} | Lecture: {read_info}")
        dataset_record = recommendation_record(path, "dataset", build_dataset_profile(frame, args.intended_use), read_info)
        records.append(dataset_record)
        print(f"  Dataset -> {dataset_record['recommendation']['action']} ({dataset_record['recommendation']['target']})")

        for column_name in frame.columns:
            profile = build_column_profile(frame, column_name, args.intended_use)
            record = recommendation_record(path, f"column:{column_name}", profile, read_info)
            records.append(record)
            recommendation = record["recommendation"]
            if recommendation["action"] != "no_action":
                print(f"  Colonne {column_name} -> {recommendation['action']} {recommendation['parameters']}")

    with output_path.open("w", encoding="utf-8") as target:
        for record in records:
            target.write(json.dumps(json_ready(record), ensure_ascii=False) + "\n")

    print(f"\nResultats ecrits: {output_path}")
    print(f"Enregistrements: {len(records)}")


if __name__ == "__main__":
    main()
