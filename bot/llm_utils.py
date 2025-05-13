import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel, PeftConfig
import os

def get_llm_coeff(ticker, messages):
    model_path = os.path.join(f"../models", ticker)


    config = PeftConfig.from_pretrained(model_path)
        
    base_model = AutoModelForSequenceClassification.from_pretrained(
        config.base_model_name_or_path,
        num_labels=2,
        attn_implementation="eager",
        ignore_mismatched_sizes=True
    )
    
    model = PeftModel.from_pretrained(base_model, model_path, is_trainable=False, config=config)
    
    model = model.merge_and_unload()
    
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)    

    diffs = []
    for msg in messages:
        text = msg.get('text', '')
        
        inputs = tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        class_0_prob = probabilities[0][0].item()
        class_1_prob = probabilities[0][1].item()
    
        diff = class_1_prob - class_0_prob
        
        diffs.append(diff)
    
    return sum(diffs) / len(diffs) if diffs else 0.0
