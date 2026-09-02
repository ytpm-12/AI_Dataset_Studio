#!/usr/bin/env bash
set -euo pipefail

MODEL="${MODEL:-Qwen/Qwen3-4B-Instruct-2507}"
TRAIN_DATA="${TRAIN_DATA:-ai_lab/training/qwen3_sft_train.jsonl}"
VAL_DATA="${VAL_DATA:-ai_lab/training/qwen3_sft_validation.jsonl}"
OUTPUT_DIR="${OUTPUT_DIR:-ai_lab/fine_tuning/output/qwen3_ai_dataset_studio_lora}"
DTYPE="${DTYPE:-bfloat16}"
EPOCHS="${EPOCHS:-3}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-1}"
EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-1}"
LEARNING_RATE="${LEARNING_RATE:-1e-4}"
LORA_RANK="${LORA_RANK:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"
GRAD_ACCUM="${GRAD_ACCUM:-8}"
EVAL_STEPS="${EVAL_STEPS:-20}"
SAVE_STEPS="${SAVE_STEPS:-20}"
MAX_LENGTH="${MAX_LENGTH:-2048}"

python -m swift.cli.sft \
  --model "$MODEL" \
  --tuner_type lora \
  --dataset "$TRAIN_DATA" \
  --val_dataset "$VAL_DATA" \
  --torch_dtype "$DTYPE" \
  --num_train_epochs "$EPOCHS" \
  --per_device_train_batch_size "$TRAIN_BATCH_SIZE" \
  --per_device_eval_batch_size "$EVAL_BATCH_SIZE" \
  --learning_rate "$LEARNING_RATE" \
  --lora_rank "$LORA_RANK" \
  --lora_alpha "$LORA_ALPHA" \
  --target_modules all-linear \
  --gradient_accumulation_steps "$GRAD_ACCUM" \
  --eval_steps "$EVAL_STEPS" \
  --save_steps "$SAVE_STEPS" \
  --save_total_limit 2 \
  --logging_steps 1 \
  --max_length "$MAX_LENGTH" \
  --output_dir "$OUTPUT_DIR" \
  --warmup_ratio 0.05 \
  --dataset_num_proc 2 \
  --dataloader_num_workers 2 \
  --use_hf true
