lora_rank=8
lora_trainable="query_key_value,dense,dense_h_to_4h,dense_4h_to_h"
modules_to_save="null"
lora_dropout=0.2
LR=2e-4
model_name_or_path="/home/u21s051047/huggingface/chatglm-6b"   # LLM底座模型路径，或者是huggingface hub上的模型名称
your_data_path="../datasets/Text2DT"  # 填入数据集所在的文件夹路径
your_checkpopint_path="../outputs"
CHECKPOINT=lora-aux_RE_TreeS-aug-2e-4-2022
STEP=1000

CUDA_VISIBLE_DEVICES=1 python main.py \
    --do_predict \
    --validation_file $your_data_path/test_dt.json \
    --test_file $your_data_path/test_dt.json \
    --overwrite_cache \
    --prompt_column input \
    --response_column target \
    --model_name_or_path $model_name_or_path \
    --peft_path $your_checkpopint_path/$CHECKPOINT/checkpoint-$STEP \
    --output_dir $your_checkpopint_path/$CHECKPOINT/checkpoint-$STEP \
    --overwrite_output_dir \
    --max_source_length 225 \
    --max_target_length 300 \
    --per_device_eval_batch_size 1 \
    --predict_with_generate
