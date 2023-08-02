from transformers import LlamaTokenizer
import os
from tqdm import tqdm
import pickle

#path to tokenizer; used llama 7b weights for cortex connoisseur
tokenizer = LlamaTokenizer.from_pretrained("/path/to/llama/tokenizer")

tokenizer.pad_token_id = (0)
tokenizer.padding_side = "left"  # Allow batched inference

#prompt is input to tokenizer
def tokenize(prompt, add_eos_token=True):
        result = tokenizer(
            prompt,
            truncation=True,
            padding=False,
            return_tensors=None,
        )
        if (
            result["input_ids"][-1] != tokenizer.eos_token_id
            and add_eos_token
        ):
            result["input_ids"].append(tokenizer.eos_token_id)
            result["attention_mask"].append(1)

        result["labels"] = result["input_ids"].copy()

        return result

#list of directories that contain input text files (cleaned) 
directory_list = ['/path/to/papers/springer','/path/to/cleaned/papers/pmc', '/path/to/cleaned/papers/arxiv', '/path/to/cleaned/papers/elsevier']

#loops through each file in each directory
#tokenizes text and pickles file into tokenized-text directory
#output is BatchEncoding type
for directory in tqdm(directory_list):
    for filename in tqdm(os.listdir(directory)):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            with open(f, 'r') as file:
                sample = file.read()
            pickle.dump(tokenize(sample), open(f'/path/to/tokenized/directory/{filename}', 'wb'))
   