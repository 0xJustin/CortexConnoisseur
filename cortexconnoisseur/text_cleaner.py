import re
import os
from tqdm import tqdm

#clean arxiv text
def clean_arxiv(sample):
    #strip bibliography
    ref_index = sample.rfind("References")
    if (ref_index == -1):
        ref_index = sample.rfind("REFERENCES")
    if (ref_index == -1):
        ref_index = sample.rfind("references")
    if (ref_index != -1):
        sample = sample[0:int(ref_index)]
    
    #correct words split over line breaks
    sample = re.sub('-&&&', '', sample)
    sample = re.sub('&&&', ' ', sample)

    return sample

#clean pub med central text
def clean_pmc(sample):
    #strip beginning metadata and bibliography
    title_index = sample.find('TITLE')
    ref_index = sample.find('REF')
    sample = sample[title_index:ref_index]

    #correct words split over line breaks
    sample = re.sub('-&&&', '', sample)
    sample = re.sub('&&&', ' ', sample)

    return sample

#clean elsevier text    
def clean_elsevier(sample):
    #remove extraneous links
    sample = re.sub(r'https?:\/\/.\S+', "", sample)
    sample = re.sub(r'http?:\/\/.\S+', "", sample)

    #remove file types
    sample = re.sub(r'^\w+\.(gif|png|jpg|jpeg|sml|pdf|flv)$', " ", sample)
    sample = re.sub(r'sml|jpg|png|gif', "", sample)
    sample = re.sub(r'IMAGE\S+', "", sample)
    sample = re.sub(r'\s+figs\S+', "", sample )
    sample = re.sub(r'\s+mmc\S+', "", sample )
    sample = re.sub(r'\s+gr\S+', "", sample )
    sample = re.sub(r'\s+fr\S+', "", sample )
    sample = re.sub(r'^\w+\-(figs|lrg|gr|mmc|si|fx)\S+$', " ", sample)

    #remove bibliography
    ref_index = sample.find("References")
    if (ref_index == -1):
        ref_index = sample.rfind("REFERENCES")
    if (ref_index == -1):
        ref_index = sample.rfind("references")
    if (ref_index != -1):
        sample = sample[0:int(ref_index)]

    #correct words split over line breaks
    sample = re.sub('-&&&', '', sample)
    sample = re.sub('&&&', ' ', sample)

    return sample


#list of directories that contain elsevier, pmc, and arxiv papers
directory_list = ['/path/to/papers/pmc', '/path/to/papers/arxiv', '/path/to/papers/elsevier']



publisher = 0

#iterates through each file in each directory and saves cleaned text into a txt file in a clean text directory
for directory in tqdm(directory_list):
    publisher = publisher + 1
    for filename in tqdm(os.listdir(directory)):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            with open(f, 'r') as file:
                sample = file.read().replace('\n', '&&&')   
            if (publisher == 1):
                with open(f'/path/to/cleaned/papers/{filename}', 'w') as m:
                    m.write(clean_pmc(sample))
            elif (publisher == 2):
                with open(f'/path/to/cleaned/papers/{filename}', 'w') as m:
                    m.write(clean_arxiv(sample))
            elif (publisher == 3):
                with open(f'/path/to/cleaned/papers/{filename}', 'w') as m:
                    m.write(clean_elsevier(sample))
