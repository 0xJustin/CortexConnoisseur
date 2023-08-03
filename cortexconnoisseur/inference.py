import transformers
import torch

#inference is often run better in a jupyter notebook especially for multiple prompts
#but this basic code can be used as an example of generation

#tokenizer must be same that was used for tokenizer.py
tokenizer = transformers.LlamaTokenizer.from_pretrained('/path/to/llama/tokenizer')
#can run inference on any set of weights
#but they must be in huggingface format
model= transformers.LlamaForCausalLM.from_pretrained('/path/to/output/weights')

#set seed for reproducibility
torch.manual_seed(3)

#sentence to finish OR prompt to answer (if chat version is used as based model)
sentence = 'The fruit fly is ' 

batch = tokenizer(
            sentence,
            return_tensors="pt",
            add_special_tokens=False
        )

with torch.no_grad():
    #generate output tokens
    #max_length refers to max length INCLUDING the prompt sentence
    generated = model.generate(inputs = batch["input_ids"], max_length=200, do_sample=True, top_k=50, temperature=0.5)
    print('model predict: ',tokenizer.decode(generated[0]))