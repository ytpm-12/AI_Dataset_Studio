$ErrorActionPreference = "Stop"

$Swift = if ($env:SWIFT_BIN) {
    $env:SWIFT_BIN
} else {
    Join-Path $env:APPDATA "Python\Python311\Scripts\swift.exe"
}

if (-not (Test-Path -LiteralPath $Swift)) {
    throw "swift.exe introuvable. Lance d'abord: python -m pip install -U ms-swift transformers"
}

$Model = if ($env:MODEL) { $env:MODEL } else { "Qwen/Qwen3-4B-Instruct-2507" }
$TrainData = if ($env:TRAIN_DATA) { $env:TRAIN_DATA } else { "ai_lab/training/qwen3_sft_train.jsonl" }
$ValData = if ($env:VAL_DATA) { $env:VAL_DATA } else { "ai_lab/training/qwen3_sft_validation.jsonl" }
$OutputDir = if ($env:OUTPUT_DIR) { $env:OUTPUT_DIR } else { "ai_lab/fine_tuning/output/qwen3_ai_dataset_studio_lora" }
$DType = if ($env:DTYPE) { $env:DTYPE } else { "float16" }
$Epochs = if ($env:EPOCHS) { $env:EPOCHS } else { "3" }
$TrainBatchSize = if ($env:TRAIN_BATCH_SIZE) { $env:TRAIN_BATCH_SIZE } else { "1" }
$EvalBatchSize = if ($env:EVAL_BATCH_SIZE) { $env:EVAL_BATCH_SIZE } else { "1" }
$LearningRate = if ($env:LEARNING_RATE) { $env:LEARNING_RATE } else { "1e-4" }
$LoraRank = if ($env:LORA_RANK) { $env:LORA_RANK } else { "8" }
$LoraAlpha = if ($env:LORA_ALPHA) { $env:LORA_ALPHA } else { "16" }
$GradAccum = if ($env:GRAD_ACCUM) { $env:GRAD_ACCUM } else { "8" }
$EvalSteps = if ($env:EVAL_STEPS) { $env:EVAL_STEPS } else { "20" }
$SaveSteps = if ($env:SAVE_STEPS) { $env:SAVE_STEPS } else { "20" }
$MaxLength = if ($env:MAX_LENGTH) { $env:MAX_LENGTH } else { "2048" }

& $Swift sft `
    --model $Model `
    --tuner_type lora `
    --dataset $TrainData `
    --val_dataset $ValData `
    --torch_dtype $DType `
    --num_train_epochs $Epochs `
    --per_device_train_batch_size $TrainBatchSize `
    --per_device_eval_batch_size $EvalBatchSize `
    --learning_rate $LearningRate `
    --lora_rank $LoraRank `
    --lora_alpha $LoraAlpha `
    --target_modules all-linear `
    --gradient_accumulation_steps $GradAccum `
    --eval_steps $EvalSteps `
    --save_steps $SaveSteps `
    --save_total_limit 2 `
    --logging_steps 1 `
    --max_length $MaxLength `
    --output_dir $OutputDir `
    --warmup_ratio 0.05 `
    --dataset_num_proc 2 `
    --dataloader_num_workers 2 `
    --use_hf true
