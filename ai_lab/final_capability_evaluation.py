import argparse
import json
import time
import urllib.error
from collections import Counter
from pathlib import Path

from benchmark_ollama import (
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_URL,
    deterministic_recommendation,
    load_json,
    load_system_prompt,
    percentage,
    request_recommendation,
    score_case,
    validate_contract,
)
from profile_real_datasets import build_column_profile, build_dataset_profile, json_ready, read_dataset


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DOWNLOAD_DIR = Path(r"D:\Downloads\jeu de donnee")
DEFAULT_OUTPUT_DIR = BASE_DIR / "results" / "final_capability_evaluation"


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluation finale non arrangee du moteur IA/hybride.")
    parser.add_argument("--download-dir", default=str(DEFAULT_DOWNLOAD_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--max-rows", type=int, default=0, help="0 = lire tous les lignes disponibles.")
    parser.add_argument("--with-llm", action="store_true", help="Interroge aussi Qwen via Ollama sur les profils reels.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--num-ctx", type=int, default=2048)
    parser.add_argument("--system-prompt", default=str(BASE_DIR / "system_prompt.txt"))
    return parser.parse_args()


def load_cases(path):
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as target:
        for record in records:
            target.write(json.dumps(json_ready(record), ensure_ascii=False) + "\n")


def evaluate_supervised_split(split_name, cases_path, schema):
    cases = load_cases(cases_path)
    records = []
    totals = Counter()
    exact = 0
    started_at = time.perf_counter()

    for case in cases:
        result = deterministic_recommendation(case["profile"])
        scores = score_case(case, result, schema)
        exact += int(all(scores.values()))
        for name, passed in scores.items():
            totals[name] += int(passed)
        records.append(
            {
                "split": split_name,
                "case_id": case["id"],
                "source_case_id": case.get("source_case_id"),
                "synthetic": case.get("synthetic"),
                "scores": scores,
                "result": result,
            }
        )

    duration = time.perf_counter() - started_at
    completed = len(cases)
    summary = {
        "split": split_name,
        "cases": completed,
        "duration_seconds": round(duration, 3),
        "contract_rate": percentage(totals["contract"], completed),
        "action_rate": percentage(totals["action"], completed),
        "target_rate": percentage(totals["target"], completed),
        "parameters_rate": percentage(totals["parameters"], completed),
        "validation_rate": percentage(totals["validation"], completed),
        "exact_rate": percentage(exact, completed),
        "exact": exact,
    }
    return summary, records


def discover_csv_files(download_dir):
    candidates = []
    project_data = BASE_DIR / "data"
    if project_data.exists():
        candidates.extend(sorted(project_data.glob("*.csv")))
    external = Path(download_dir)
    if external.exists():
        candidates.extend(sorted(external.glob("*.csv")))

    seen = set()
    unique = []
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def profile_csv_files(csv_files, max_rows, system_prompt, schema, args):
    records = []
    summaries = []
    nrows = None if max_rows == 0 else max_rows

    for path in csv_files:
        started_at = time.perf_counter()
        print(f"\nCSV: {path}")
        try:
            frame, read_info = read_dataset(path, nrows)
        except Exception as error:
            print(f"  ERREUR lecture: {error}")
            records.append({"file": str(path), "error": str(error)})
            summaries.append({"file": str(path), "error": str(error)})
            continue

        file_records = []
        profiles = [("dataset", build_dataset_profile(frame, None))]
        profiles.extend((f"column:{column_name}", build_column_profile(frame, column_name, None)) for column_name in frame.columns)

        action_counts = Counter()
        llm_contract_failures = 0
        llm_rule_disagreements = 0
        critical_disagreements = []

        for scope, profile in profiles:
            rule_result = deterministic_recommendation(profile)
            llm_result = None
            llm_error = None
            llm_contract_ok = None

            if args.with_llm:
                try:
                    llm_result = request_recommendation(
                        "ollama",
                        args.url,
                        args.model,
                        schema,
                        system_prompt,
                        profile,
                        args.timeout,
                        False,
                        0,
                        args.num_ctx,
                        "",
                        512,
                    )
                    llm_contract_ok = validate_contract(llm_result, schema)
                    llm_contract_failures += int(not llm_contract_ok)
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, RuntimeError) as error:
                    llm_error = str(error)
                    llm_contract_failures += 1

                if llm_result and llm_result.get("action") != rule_result.get("action"):
                    llm_rule_disagreements += 1
                    column = profile.get("column", {})
                    if column.get("missing_ratio", 0) > 0 and llm_result.get("action") == "no_action":
                        critical_disagreements.append(
                            {
                                "scope": scope,
                                "reason": "missing_ratio>0 mais LLM propose no_action",
                                "rule_action": rule_result.get("action"),
                                "llm_action": llm_result.get("action"),
                                "missing_ratio": column.get("missing_ratio"),
                            }
                        )
                    if rule_result.get("action") in {"validate_integrity", "request_human_review"}:
                        critical_disagreements.append(
                            {
                                "scope": scope,
                                "reason": "désaccord sur une règle prudente",
                                "rule_action": rule_result.get("action"),
                                "llm_action": llm_result.get("action"),
                            }
                        )

            action_counts[rule_result["action"]] += 1
            record = {
                "file": str(path),
                "scope": scope,
                "rows_read": int(len(frame)),
                "columns_read": int(len(frame.columns)),
                "read_info": read_info,
                "profile": profile,
                "rule_recommendation": rule_result,
                "llm_recommendation": llm_result,
                "llm_error": llm_error,
                "llm_contract_ok": llm_contract_ok,
            }
            file_records.append(record)
            records.append(record)

        duration = time.perf_counter() - started_at
        summary = {
            "file": str(path),
            "rows_read": int(len(frame)),
            "columns_read": int(len(frame.columns)),
            "read_info": read_info,
            "profiles_evaluated": len(profiles),
            "rule_action_counts": dict(action_counts),
            "llm_enabled": args.with_llm,
            "llm_contract_failures": llm_contract_failures if args.with_llm else None,
            "llm_rule_disagreements": llm_rule_disagreements if args.with_llm else None,
            "critical_disagreements": critical_disagreements,
            "duration_seconds": round(duration, 3),
        }
        summaries.append(summary)

        print(f"  Lignes lues: {len(frame)} | Colonnes: {len(frame.columns)} | Profils: {len(profiles)}")
        print(f"  Actions règles: {dict(action_counts)}")
        if args.with_llm:
            print(f"  Désaccords Qwen/règles: {llm_rule_disagreements} | contrats LLM échoués: {llm_contract_failures}")
            if critical_disagreements:
                print(f"  Désaccords critiques: {len(critical_disagreements)}")

    return summaries, records


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def write_report(path, supervised_summaries, csv_summaries, args):
    rows = []
    for summary in supervised_summaries:
        rows.append(
            [
                summary["split"],
                summary["cases"],
                f'{summary["exact_rate"]:.1f} %',
                f'{summary["action_rate"]:.1f} %',
                f'{summary["validation_rate"]:.1f} %',
                f'{summary["duration_seconds"]:.2f}s',
            ]
        )

    csv_rows = []
    for summary in csv_summaries:
        if "error" in summary:
            csv_rows.append([Path(summary["file"]).name, "ERREUR", "-", "-", summary["error"]])
            continue
        csv_rows.append(
            [
                Path(summary["file"]).name,
                summary["rows_read"],
                summary["columns_read"],
                summary["profiles_evaluated"],
                summary["rule_action_counts"],
            ]
        )

    llm_note = (
        "Le test Qwen/Ollama a été exécuté sur les profils réels en zéro-shot, sans few-shot."
        if args.with_llm
        else "Le test Qwen/Ollama sur profils réels n'a pas été exécuté dans cette passe; seules les règles déterministes ont été appliquées aux CSV."
    )

    content = f"""# Evaluation finale non arrangee - AI Dataset Studio

Date : 2026-08-29

## Protocole

- Données supervisées : `cases_train.jsonl`, `cases_validation.jsonl`, `cases_test.jsonl`.
- Données réelles : CSV du projet + CSV téléchargés dans `{args.download_dir}`.
- Mode few-shot désactivé.
- Règles déterministes appliquées sans correction manuelle.
- Prompt système utilisé pour les appels Qwen : `{args.system_prompt}`.
- Lignes CSV lues : {"toutes les lignes" if args.max_rows == 0 else args.max_rows}.

Attention méthodologique : le split `train` est connu du fine-tuning, donc il sert seulement de contrôle de cohérence. Le split `test` et les CSV publics sont les parties les plus utiles pour juger la capacité réelle.

## Résultats supervisés avec règles déterministes

{markdown_table(["Split", "Cas", "Exact", "Action", "Validation", "Durée"], rows)}

## Résultats sur CSV réels

{markdown_table(["Fichier", "Lignes", "Colonnes", "Profils", "Actions règles"], csv_rows)}

## Qwen / LoRA

{llm_note}

Le checkpoint LoRA `checkpoint-48` reste un artefact expérimental. Il n'est pas encore fusionné dans Ollama localement. Pour un test produit non biaisé aujourd'hui, la décision fiable est donc celle du moteur hybride : règles d'abord, Qwen ensuite uniquement si le service LoRA est disponible et validé.

## Lecture des résultats

- Un score parfait sur `train` n'est pas une preuve suffisante, car ces cas sont proches de l'entraînement.
- Un score parfait sur `test` montre que les règles couvrent correctement le périmètre actuellement défini.
- Les CSV réels vérifient la robustesse du profilage : encodage, séparateur, volume, dates, valeurs manquantes et nombres français.
- L'absence de vérité terrain sur CSV réels interdit de parler de pourcentage de précision; on parle plutôt de cohérence des recommandations produites.

## Décision

Le moteur recommandé pour l'intégration reste :

```text
profilage pandas -> règles déterministes -> Qwen/LoRA si nécessaire -> validation JSON -> validation humaine
```
"""
    path.write_text(content, encoding="utf-8")


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = load_json(BASE_DIR / "recommendation.schema.json")
    system_prompt = load_system_prompt(args.system_prompt)

    supervised_summaries = []
    for split_name in ["train", "validation", "test"]:
        cases_path = BASE_DIR / "training" / f"cases_{split_name}.jsonl"
        summary, records = evaluate_supervised_split(split_name, cases_path, schema)
        supervised_summaries.append(summary)
        write_jsonl(output_dir / f"supervised_{split_name}_rules.jsonl", records)
        print(
            f"{split_name}: exact={summary['exact']}/{summary['cases']} "
            f"({summary['exact_rate']:.1f} %) | durée={summary['duration_seconds']:.2f}s"
        )

    csv_files = discover_csv_files(args.download_dir)
    print(f"\nCSV découverts: {len(csv_files)}")
    for csv_file in csv_files:
        print(f"- {csv_file}")

    csv_summaries, csv_records = profile_csv_files(csv_files, args.max_rows, system_prompt, schema, args)
    write_jsonl(output_dir / "real_csv_profiles_and_recommendations.jsonl", csv_records)
    write_jsonl(output_dir / "summary.jsonl", [{"supervised": supervised_summaries, "csv": csv_summaries}])
    write_report(output_dir / "RAPPORT_EVALUATION_FINALE.md", supervised_summaries, csv_summaries, args)

    print(f"\nDossier résultats: {output_dir}")
    print(f"Rapport: {output_dir / 'RAPPORT_EVALUATION_FINALE.md'}")


if __name__ == "__main__":
    main()
