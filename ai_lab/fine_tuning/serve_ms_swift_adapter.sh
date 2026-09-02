#!/usr/bin/env bash
set -euo pipefail

if [ "${ADAPTER:-}" = "" ]; then
  echo "Usage: ADAPTER=ai_lab/fine_tuning/output/.../checkpoint-xxx bash ai_lab/fine_tuning/serve_ms_swift_adapter.sh"
  exit 1
fi

MODEL_NAME="${MODEL_NAME:-qwen3-ai-dataset-studio}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
BACKEND="${BACKEND:-transformers}"

python -m swift.cli.deploy \
  --host "$HOST" \
  --port "$PORT" \
  --adapters "$ADAPTER" \
  --infer_backend "$BACKEND" \
  --temperature 0 \
  --max_new_tokens 512 \
  --served_model_name "$MODEL_NAME"
