import io
import requests
import re
from utils import get_text_from_arxiv, get_text_from_elsevier, get_text_from_pmc, get_text_from_springer, get_text_from_response
import pickle
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

if __name__ == '__main__':
    
    #unpickling the doi dictionary
    doidict = pickle.load(open('./doi_dict.pkl','rb'))
    skip_list = []
    
    def extract_text_from_paper(doi, values):
    #retrieve full text OR save to skip list
    #replace api keys with appropriate values
    #each function returns either 0 or an error tuple that is added to skip list
        if 'ArXiv' in values['externalIds']:
            arxiv_return = get_text_from_arxiv(values['externalIds']['ArXiv'], doi, values['paperId'], True)
            if (arxiv_return != '0'):
                skip_list.append(arxiv_return)
        elif 'PubMedCentral' in values['externalIds']:
            pmc_return = get_text_from_pmc(values['externalIds']['PubMedCentral'], doi,  True)
            if (pmc_return != '0'):
                skip_list.append(pmc_return)        
        elif values['publicationVenue'] is not None and 'alternate_urls' in values['publicationVenue']:
            if(len([val for val in values['publicationVenue']['alternate_urls'] if 'sciencedirect' in val]) != 0):
                elsevier_return = get_text_from_elsevier(doi, values['paperId'], True, 'insertApiKey')
                if (elsevier_return != '0'):
                    skip_list.append(elsevier_return)
        else:   
            springer_return = get_text_from_springer(doi, values['paperId'], True, 'insertApiKey')
            if (springer_return != '0'):
                skip_list.append(springer_return)
        print(doi)

    #concurrent processing of papers
    with ThreadPool() as executor:
        results = executor.starmap(extract_text_from_paper, tqdm(doidict.items()))
    print('done!')


    #save skipped papers doi
    with open(f'./skip_list.p', 'wb') as f:
            pickle.dump(skip_list, f)

