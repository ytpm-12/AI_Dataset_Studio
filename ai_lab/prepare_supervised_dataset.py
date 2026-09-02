import argparse
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES_PATH = BASE_DIR / "evaluation_cases.jsonl"
DEFAULT_PROMPT_PATH = BASE_DIR / "system_prompt.txt"
DEFAULT_OUTPUT_PATH = BASE_DIR / "training" / "qwen3_recommendations_sft.jsonl"


def parse_args():
    parser = argparse.ArgumentParser(description="Prépare un JSONL supervisé pour Qwen3.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES_PATH))
    parser.add_argument("--system-prompt", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    return parser.parse_args()


def load_cases(path):
    with Path(path).open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def build_expected_response(case):
    action = case["expected_actions"][0]
    requires_validation = case["must_require_validation"]
    return {
        "action": action,
        "target": case["expected_target"],
        "parameters": case["expected_parameters"],
        "confidence": 0.95 if requires_validation else 0.98,
        "explanation": case.get("notes", "Recommandation conforme au profil fourni."),
        "requires_validation": requires_validation,
    }


def build_record(case, system_prompt):
    profile_json = json.dumps(case["profile"], ensure_ascii=False, separators=(",", ":"))
    expected_json = json.dumps(build_expected_response(case), ensure_ascii=False, separators=(",", ":"))
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Analyse ce profil et fournis une recommandation :\n{profile_json}",
            },
            {"role": "assistant", "content": expected_json},
        ]
    }


def main():
    args = parse_args()
    system_prompt = Path(args.system_prompt).read_text(encoding="utf-8").strip()
    cases = load_cases(args.cases)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as target:
        for case in cases:
            target.write(json.dumps(build_record(case, system_prompt), ensure_ascii=False) + "\n")
    print(f"Exemples écrits: {len(cases)}")
    print(f"Fichier: {output_path}")


if __name__ == "__main__":
    main()
