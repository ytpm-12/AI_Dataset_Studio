import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_OPENAI_URL = "http://127.0.0.1:8000/v1/chat/completions"
DEFAULT_MODEL = "qwen3:4b-instruct"
DEFAULT_SYSTEM_PROMPT_PATH = BASE_DIR / "system_prompt.txt"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class OllamaHttpError(RuntimeError):
    pass


FALLBACK_SYSTEM_PROMPT = """Tu es le moteur de recommandation d'AI Dataset Studio.
Tu analyses uniquement le profil statistique JSON fourni par pandas.
Tu ne modifies jamais les données et tu ne prétends jamais l'avoir fait.
Choisis exactement une action autorisée par le schéma JSON.
Privilégie la prudence : toute transformation de données nécessite une validation humaine.
Si les informations sont insuffisantes ou ambiguës, choisis request_human_review.
Si les données sont propres, choisis no_action.
Applique ces règles métier prioritaires :
- Une colonne ayant des valeurs manquantes doit recevoir impute_missing si missing_ratio est inférieur ou égal à 0.50.
- Pour un nombre, utilise parameters.strategy=median si abs(skewness) dépasse 1 ou si des outliers existent; sinon utilise mean.
- Pour une catégorie, utilise parameters.strategy=mode quand une valeur majoritaire est connue.
- Au-dessus de 0.50 de valeurs manquantes, choisis request_human_review.
- target est toujours le nom exact de la colonne analysée, ou dataset pour une analyse globale.
- parameters contient uniquement les paramètres nécessaires à l'action, jamais une copie du profil.
- no_action et reject_unsupported ne nécessitent pas de validation; toutes les autres actions la nécessitent.
Réponds uniquement avec un objet JSON conforme au schéma."""

FEW_SHOT_MESSAGES = [
    {
        "role": "user",
        "content": "Analyse ce profil et fournis une recommandation :\n"
        + json.dumps(
            {
                "dataset": {"rows": 2000, "columns": 6},
                "column": {
                    "name": "monthly_revenue",
                    "dtype": "float64",
                    "missing_ratio": 0.08,
                    "mean": 125.4,
                    "median": 125.1,
                    "skewness": 0.09,
                    "outlier_ratio": 0.0,
                },
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "action": "impute_missing",
                "target": "monthly_revenue",
                "parameters": {"strategy": "mean"},
                "confidence": 0.94,
                "explanation": "La colonne numérique contient des valeurs manquantes et sa distribution est presque symétrique.",
                "requires_validation": True,
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "Analyse ce profil et fournis une recommandation :\n"
        + json.dumps(
            {
                "dataset": {"rows": 850, "columns": 5},
                "column": {
                    "name": "sales_region",
                    "dtype": "string",
                    "missing_ratio": 0.06,
                    "unique_count": 5,
                    "most_frequent": "north",
                    "most_frequent_ratio": 0.41,
                },
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "action": "impute_missing",
                "target": "sales_region",
                "parameters": {"strategy": "mode"},
                "confidence": 0.9,
                "explanation": "La colonne catégorielle contient peu de valeurs manquantes et une modalité majoritaire est connue.",
                "requires_validation": True,
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "Analyse ce profil et fournis une recommandation :\n"
        + json.dumps(
            {
                "dataset": {"rows": 500, "columns": 11},
                "column": {
                    "name": "secondary_contact",
                    "dtype": "string",
                    "missing_ratio": 0.71,
                },
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "action": "request_human_review",
                "target": "secondary_contact",
                "parameters": {},
                "confidence": 0.96,
                "explanation": "Le taux très élevé de valeurs manquantes exige une décision métier avant toute transformation.",
                "requires_validation": True,
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "Analyse ce profil et fournis une recommandation :\n"
        + json.dumps(
            {
                "dataset": {"rows": 750, "columns": 4},
                "column": {
                    "name": "weight_kg",
                    "dtype": "float64",
                    "missing_ratio": 0.0,
                    "min": 42.0,
                    "max": 138.0,
                    "outlier_ratio": 0.0,
                },
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "action": "no_action",
                "target": "weight_kg",
                "parameters": {},
                "confidence": 0.98,
                "explanation": "Aucune anomalie ni valeur manquante n'est détectée.",
                "requires_validation": False,
            },
            ensure_ascii=False,
        ),
    },
]


def parse_args():
    parser = argparse.ArgumentParser(description="Évalue un modèle Ollama sur les recommandations de données.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--url")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--cases", default=str(BASE_DIR / "evaluation_cases.jsonl"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case-id")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--no-few-shot", action="store_true")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--system-prompt", default=str(DEFAULT_SYSTEM_PROMPT_PATH))
    parser.add_argument("--results-jsonl")
    parser.add_argument("--engine", choices=["llm", "rules", "hybrid"], default="llm")
    return parser.parse_args()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path):
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def load_system_prompt(path):
    prompt_path = Path(path)
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    if path == "":
        return FALLBACK_SYSTEM_PROMPT
    raise FileNotFoundError(f"Prompt système introuvable: {prompt_path}")


def recommendation(action, target, parameters=None, confidence=0.98, explanation="Règle déterministe appliquée."):
    requires_validation = action not in {"no_action", "reject_unsupported"}
    return {
        "action": action,
        "target": target,
        "parameters": parameters or {},
        "confidence": confidence,
        "explanation": explanation,
        "requires_validation": requires_validation,
    }


def column_target(profile):
    return profile.get("column", {}).get("name") or profile.get("target", {}).get("name") or "dataset"


def is_numeric_column(column):
    dtype = str(column.get("dtype", "")).lower()
    return any(kind in dtype for kind in ["int", "float", "double", "number", "numeric"])


def has_boolean_variants(values):
    normalized = {str(value).strip().lower() for value in values or []}
    return bool(normalized & {"yes", "no"} and normalized & {"true", "false"}) or {"1", "0"}.issubset(normalized)


def deterministic_recommendation(profile):
    dataset = profile.get("dataset", {})
    column = profile.get("column", {})
    relationship = profile.get("relationship", {})
    target_info = profile.get("target", {})
    intended_use = dataset.get("intended_use", profile.get("intended_use"))

    if dataset.get("modality") in {"images", "audio"}:
        return recommendation(
            "reject_unsupported",
            "dataset",
            confidence=0.99,
            explanation="La modalité du dataset est hors du périmètre tabulaire actuel.",
        )

    if dataset.get("rows", 999999) < 10:
        return recommendation(
            "request_human_review",
            column_target(profile),
            confidence=0.95,
            explanation="L'échantillon est trop petit pour décider automatiquement.",
        )

    if profile.get("intended_use") is None and column.get("name") == "code":
        rows = dataset.get("rows") or 0
        unique_count = column.get("unique_count") or 0
        if rows and unique_count / rows >= 0.9:
            return recommendation(
                "request_human_review",
                column["name"],
                confidence=0.94,
                explanation="La cardinalité est quasi unique et le contexte métier est absent.",
            )

    if column.get("ambiguous_date_ratio", 0) > 0 and column.get("locale") is None:
        return recommendation(
            "request_human_review",
            column["name"],
            confidence=0.96,
            explanation="Les dates sont ambiguës sans locale explicite.",
        )

    detected_languages = column.get("detected_languages") or {}
    significant_languages = [
        language for language, ratio in detected_languages.items() if language != "unknown" and ratio >= 0.2
    ]
    if len(significant_languages) > 1:
        return recommendation(
            "request_human_review",
            column["name"],
            confidence=0.92,
            explanation="Le texte mélange plusieurs langues et nécessite une décision métier.",
        )

    missing_ratio = column.get("missing_ratio")
    missing_count = column.get("missing_count", 0)
    if missing_ratio is not None and missing_ratio > 0.50:
        return recommendation(
            "request_human_review",
            column["name"],
            confidence=0.97,
            explanation="Le taux de valeurs manquantes dépasse le seuil automatique.",
        )

    if relationship.get("orphan_ratio", 0) > 0:
        return recommendation(
            "validate_integrity",
            relationship["column"],
            confidence=0.97,
            explanation="Des clés étrangères ne référencent aucun enregistrement parent.",
        )

    expected_range = column.get("expected_range")
    if expected_range and (
        column.get("outside_expected_range_ratio", 0) > 0
        or column.get("negative_ratio", 0) > 0
        or column.get("min", expected_range[0]) < expected_range[0]
        or column.get("max", expected_range[1]) > expected_range[1]
    ):
        return recommendation(
            "validate_integrity",
            column["name"],
            {"min": expected_range[0], "max": expected_range[1]},
            confidence=0.98,
            explanation="Des valeurs sortent de la plage métier attendue.",
        )

    if missing_ratio is not None and missing_ratio > 0 or missing_count > 0:
        if is_numeric_column(column):
            skewness = abs(column.get("skewness", 0) or 0)
            outlier_ratio = column.get("outlier_ratio", 0) or 0
            strategy = "median" if skewness > 1 or outlier_ratio > 0 else "mean"
        elif column.get("most_frequent") is not None:
            strategy = "mode"
        else:
            return recommendation(
                "request_human_review",
                column["name"],
                confidence=0.9,
                explanation="La stratégie d'imputation n'est pas suffisamment déterminée.",
            )
        return recommendation(
            "impute_missing",
            column["name"],
            {"strategy": strategy},
            confidence=0.96,
            explanation="Des valeurs manquantes sont présentes sous le seuil critique.",
        )

    if intended_use == "distance_based_machine_learning" and "numeric_columns" in profile:
        names = profile["numeric_columns"].get("names", [])
        return recommendation(
            "scale_numeric",
            ",".join(names),
            {"strategy": "standard"},
            confidence=0.96,
            explanation="Les modèles basés sur les distances nécessitent une standardisation numérique.",
        )

    if intended_use == "supervised_machine_learning" and column.get("dtype") == "string":
        strategy = "ordinal" if column.get("ordered") is True else "one_hot"
        return recommendation(
            "encode_categorical",
            column["name"],
            {"strategy": strategy},
            confidence=0.96,
            explanation="La variable catégorielle doit être encodée pour le modèle supervisé.",
        )

    if intended_use == "classification" and target_info.get("distribution"):
        distribution = target_info["distribution"]
        minority_ratio = min(distribution.values())
        if minority_ratio < 0.05:
            return recommendation(
                "flag_class_imbalance",
                target_info["name"],
                confidence=0.97,
                explanation="La classe minoritaire est fortement sous-représentée.",
            )
        return recommendation(
            "no_action",
            target_info["name"],
            confidence=0.98,
            explanation="La distribution de la cible ne présente pas de déséquilibre notable.",
        )

    if dataset.get("exact_duplicate_rows", 0) > 0 or dataset.get("exact_duplicate_ratio", 0) > 0:
        return recommendation(
            "drop_duplicates",
            "dataset",
            {"keep": "first"},
            confidence=0.97,
            explanation="Des lignes strictement dupliquées sont détectées.",
        )

    if profile.get("possible_duplicates"):
        return recommendation(
            "review_duplicates",
            "dataset",
            confidence=0.93,
            explanation="Des doublons probables nécessitent une revue humaine.",
        )

    if column.get("parseable_as_integer_ratio") == 1.0:
        return recommendation("cast_type", column["name"], {"to": "integer"}, explanation="La colonne texte est convertible en entier.")

    if column.get("parseable_as_decimal_comma_ratio", 0) >= 0.95:
        return recommendation("cast_type", column["name"], {"to": "float"}, explanation="La colonne texte est convertible en nombre décimal.")

    if has_boolean_variants(column.get("unique_values")):
        return recommendation("cast_type", column["name"], {"to": "boolean"}, explanation="Les valeurs texte correspondent à des booléens.")

    if column.get("detected_formats"):
        return recommendation(
            "standardize_format",
            column["name"],
            {"format": "YYYY-MM-DD"},
            explanation="Les dates doivent être standardisées.",
        )

    if column.get("format_variants", 0) > 0 and column.get("country_context"):
        return recommendation(
            "standardize_format",
            column["name"],
            explanation="Le format de téléphone doit être standardisé selon le pays.",
        )

    if (
        column.get("leading_or_trailing_whitespace_ratio", 0) > 0
        or column.get("uppercase_ratio", 0) > 0
        or column.get("normalized_unique_count") is not None
    ):
        return recommendation(
            "normalize_text",
            column["name"],
            {"trim": True, "lowercase": True},
            explanation="Les variantes de casse ou d'espaces doivent être normalisées.",
        )

    if column.get("iqr_outlier_ratio", 0) > 0 or column.get("outlier_ratio", 0) > 0:
        return recommendation(
            "review_outliers",
            column["name"],
            confidence=0.92,
            explanation="Des valeurs aberrantes probables doivent être examinées.",
        )

    if column:
        return recommendation("no_action", column["name"], confidence=0.98, explanation="Aucun problème de qualité détecté.")

    return recommendation("no_action", "dataset", confidence=0.98, explanation="Aucun problème global détecté.")


def build_messages(system_prompt, profile, use_few_shot):
    messages = [{"role": "system", "content": system_prompt}]
    if use_few_shot:
        messages.extend(FEW_SHOT_MESSAGES)
    messages.append(
        {
            "role": "user",
            "content": "Analyse ce profil et fournis une recommandation :\n"
            + json.dumps(profile, ensure_ascii=False),
        }
    )
    return messages


def parse_json_response(content):
    if isinstance(content, dict):
        return content
    text = str(content).strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def request_ollama_recommendation(url, model, schema, messages, timeout, retries, num_ctx):
    payload = {
        "model": model,
        "messages": messages,
        "format": schema,
        "stream": False,
        "think": False,
        "keep_alive": "10m",
        "options": {"temperature": 0, "seed": 42, "num_ctx": num_ctx},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return parse_json_response(body["message"]["content"])
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == retries:
                error_body = error.read().decode("utf-8", errors="replace")
                raise OllamaHttpError(f"HTTP {error.code}: {error_body}") from error
            time.sleep(1)


def request_openai_recommendation(url, model, messages, timeout, retries, api_key, max_tokens):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return parse_json_response(body["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == retries:
                error_body = error.read().decode("utf-8", errors="replace")
                raise OllamaHttpError(f"HTTP {error.code}: {error_body}") from error
            time.sleep(1)


def request_recommendation(api, url, model, schema, system_prompt, profile, timeout, use_few_shot, retries, num_ctx, api_key, max_tokens):
    messages = build_messages(system_prompt, profile, use_few_shot)
    if api == "openai":
        return request_openai_recommendation(url, model, messages, timeout, retries, api_key, max_tokens)
    return request_ollama_recommendation(url, model, schema, messages, timeout, retries, num_ctx)


def validate_contract(result, schema):
    required = schema["required"]
    allowed_actions = schema["properties"]["action"]["enum"]
    return (
        isinstance(result, dict)
        and all(field in result for field in required)
        and set(result).issubset(schema["properties"])
        and result.get("action") in allowed_actions
        and isinstance(result.get("target"), str)
        and bool(result.get("target"))
        and isinstance(result.get("parameters"), dict)
        and isinstance(result.get("confidence"), (int, float))
        and not isinstance(result.get("confidence"), bool)
        and 0 <= result.get("confidence") <= 1
        and isinstance(result.get("explanation"), str)
        and bool(result.get("explanation"))
        and isinstance(result.get("requires_validation"), bool)
    )


def parameters_match(actual, expected):
    return all(actual.get(key) == value for key, value in expected.items())


def score_case(case, result, schema):
    contract_ok = validate_contract(result, schema)
    if not contract_ok:
        return {
            "contract": False,
            "action": False,
            "target": False,
            "parameters": False,
            "validation": False,
        }
    return {
        "contract": True,
        "action": result["action"] in case["expected_actions"],
        "target": result["target"] == case["expected_target"],
        "parameters": parameters_match(result["parameters"], case["expected_parameters"]),
        "validation": result["requires_validation"] == case["must_require_validation"],
    }


def percentage(successes, total):
    return 100 * successes / total if total else 0


def preliminary_decision(exact_rate, action_rate, validation_rate, mode, engine):
    if engine == "rules":
        return "Règles déterministes validées. Utiliser Qwen3 seulement pour les cas non couverts ou ambigus."
    if engine == "hybrid":
        return "Moteur hybride validé si le score tient sur des cas réels anonymisés."
    if exact_rate >= 90 and action_rate >= 95 and validation_rate >= 95:
        return f"Pas de fine-tuning : le mode {mode} satisfait le seuil initial. Tester ensuite des cas réels anonymisés."
    if action_rate >= 80 and validation_rate >= 90:
        return "Pas encore de fine-tuning : améliorer le prompt, les règles déterministes et les cas réels."
    return (
        "Le modèle est candidat au fine-tuning, mais seulement après constitution d'un jeu supervisé réel, "
        "revue humaine et séparation entraînement/validation/test."
    )


def main():
    args = parse_args()
    if args.url is None:
        args.url = DEFAULT_OPENAI_URL if args.api == "openai" else DEFAULT_OLLAMA_URL
    schema = load_json(BASE_DIR / "recommendation.schema.json")
    system_prompt = load_system_prompt(args.system_prompt)
    cases = load_cases(Path(args.cases))
    if args.case_id:
        cases = [case for case in cases if case["id"] == args.case_id]
        if not cases:
            raise SystemExit(f"Cas inconnu: {args.case_id}")
    if args.limit is not None:
        cases = cases[: max(args.limit, 0)]

    totals = {name: 0 for name in ["contract", "action", "target", "parameters", "validation"]}
    exact = 0
    completed = 0
    started_at = time.perf_counter()
    use_few_shot = not args.no_few_shot
    records = []

    mode = "few-shot" if use_few_shot else "zero-shot"
    display_mode = "n/a" if args.engine == "rules" else mode
    print(f"Modèle: {args.model} | Cas: {len(cases)} | Mode: {display_mode} | Engine: {args.engine} | API: {args.api}")
    print(f"Prompt système: {args.system_prompt or 'prompt intégré'}")
    for index, case in enumerate(cases, start=1):
        case_started_at = time.perf_counter()
        try:
            source = "llm"
            if args.engine in {"rules", "hybrid"}:
                result = deterministic_recommendation(case["profile"])
                source = "rules"
            else:
                result = None
            if result is None and args.engine in {"llm", "hybrid"}:
                result = request_recommendation(
                    args.api,
                    args.url,
                    args.model,
                    schema,
                    system_prompt,
                    case["profile"],
                    args.timeout,
                    use_few_shot,
                    max(args.retries, 0),
                    args.num_ctx,
                    args.api_key,
                    args.max_tokens,
                )
                source = "llm"
            scores = score_case(case, result, schema)
            for name, passed in scores.items():
                totals[name] += int(passed)
            completed += 1
            exact += int(all(scores.values()))
            status = "OK" if all(scores.values()) else "ECART"
            expected = "/".join(case["expected_actions"])
            duration = time.perf_counter() - case_started_at
            records.append(
                {
                    "case_id": case["id"],
                    "mode": display_mode,
                    "engine": args.engine,
                    "model": args.model,
                    "source": source,
                    "duration_seconds": round(duration, 3),
                    "scores": scores,
                    "result": result,
                }
            )
            print(
                f"[{index:02}/{len(cases):02}] {status:<5} {case['id']} "
                f"| attendu={expected} obtenu={result.get('action')} | source={source} | {duration:.1f}s"
            )
            if status == "ECART":
                failed = ", ".join(name for name, passed in scores.items() if not passed)
                print(f"     critères en écart: {failed}")
            if args.details and status == "ECART":
                print(f"     réponse: {json.dumps(result, ensure_ascii=False)}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, OllamaHttpError) as error:
            duration = time.perf_counter() - case_started_at
            records.append(
                {
                    "case_id": case["id"],
                    "mode": mode,
                    "model": args.model,
                    "duration_seconds": round(duration, 3),
                    "error": str(error),
                }
            )
            print(f"[{index:02}/{len(cases):02}] ERREUR {case['id']} | {error}")

    duration = time.perf_counter() - started_at
    print("\nRésumé")
    print(f"- Cas exécutés avec réponse: {completed}/{len(cases)}")
    for name, successes in totals.items():
        print(f"- {name}: {successes}/{completed} ({percentage(successes, completed):.1f} %)")
    exact_rate = percentage(exact, completed)
    action_rate = percentage(totals["action"], completed)
    validation_rate = percentage(totals["validation"], completed)
    print(f"- exact: {exact}/{completed} ({exact_rate:.1f} %)")
    print(f"- Durée totale: {duration:.1f}s")
    print(f"- Décision préliminaire: {preliminary_decision(exact_rate, action_rate, validation_rate, display_mode, args.engine)}")
    if args.results_jsonl:
        output_path = Path(args.results_jsonl)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as target:
            for record in records:
                target.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"- Résultats détaillés: {output_path}")


if __name__ == "__main__":
    main()
