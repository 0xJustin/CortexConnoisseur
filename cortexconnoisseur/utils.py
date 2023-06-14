import requests
from bs4 import BeautifulSoup
import backoff
import io
import PyPDF2

"""
example code to scape doi's from a webpage
code generated with help from phind.com
"""
import json
keys = json.load(open('./api_keys.json', 'rb'))

def get_page_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def extract_dois_from_page(soup):
    dois = []
    for link in soup.find_all("a"):
        if "doi.org" in link.get("href", ""):
            dois.append(link["href"])
    return dois

def get_text_from_response(pdf_response, paper_id, publisher, save):
    pdf_file = io.BytesIO(pdf_response.content)

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    if save:
        # save the text to file
        with open(f'./paper_text/{publisher}/{paper_id}.txt', 'wb') as f:
            f.write(text)
    return text
# @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_text_from_arxiv(arxiv_id, save=True):
# {
#   "arxiv_uri": "https://arxiv.org/pdf/2104.02308.pdf"
# }
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    pdf_response = requests.get(pdf_url)
    text = get_text_from_response(pdf_response, arxiv_id, 'arxiv', save)
    return text

def get_text_from_elsevier(doi, save=True):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    }
    pdf_url = f"https://api.elsevier.com/content/article/doi/{doi}"
    pdf_response = requests.get(pdf_url)
    text = get_text_from_response(pdf_response, doi, 'elsevier', save)
    return text

def get_text_from_springer(doi, save=True, api_key='a287f446500eaf7e1620969d0f098d3a'):

    url = f'https://api.springer.com/metadata/json?q=doi:{doi}&api_key={api_key}'

    pdf_response = requests.get(pdf_url)
    text = get_text_from_response(pdf_response, doi, 'springer', save)
    return text

def get_text_from_pubmed(pmc_id, save=True):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmc_id}/unicode"
    pdf_response = requests.get(pdf_url)
    text = get_text_from_response(pdf_response, pmc_id, 'pubmed', save)
    return text

def save_text_from_publisher_batch(id_list, publisher):
    from concurrent.futures import ThreadPoolExecutor
    
    """
    Using threadpoolexecutor, process many papers in parallel
    Uses arxiv_ids, formatted like this: 
    Arxiv_id: 1705.04281 -> https://arxiv.org/pdf/1705.04281.pdf

    """
    if publisher == 'arxiv':
        func = get_text_from_arxiv
    elif publisher == 'elsevier':
        func =  get_text_from_elsevier
    

    with ThreadPoolExecutor() as executor:
        results = executor.map(func, id_list)
    print('done!')



def main(url):
    soup = get_page_content(url)
    dois = extract_dois_from_page(soup)
    return dois

if __name__ == "__main__":
    main("https://www.fpbase.org/references/")
