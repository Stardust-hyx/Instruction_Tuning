# Instruction Tuning 
Tuning ChatGLM with Lora to follow instructions and solve downstream tasks.

## Quick links

* [Preparation](#preparation)
  * [Environment](#environment)
  * [Data](#data)
* [Run the model](#run)

## Preparation

### Environment
To run our code, first make sure your Python>=3.7, then install all the dependency packages by using the following command:

```
pip install -r requirements.txt
```

### Data
Please make sure your data folder structure look like below.
```bash
Instruction_tuning
  └── datasets
      └── Your_dataset
          ├── train.json
          ├── dev.json
          └── test.json

```

## Run

Run the following command to train.
```bash
cd ft_chatglm_lora
bash train.sh
```

After training, you can run the following command to infer.
```bash
bash eval.sh
```
