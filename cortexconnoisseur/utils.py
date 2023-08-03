import requests
from bs4 import BeautifulSoup
import backoff
import io
import PyPDF2
import xml.etree.ElementTree as ET
import re

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

#extract text from pdf
def get_text_from_response(pdf_response, paper_id, publisher, save):
    pdf_file = io.BytesIO(pdf_response.content)

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    if save:
        # save the text to file
        with open(f'/path/to/papers/{publisher}/{paper_id}.txt', 'w') as f:
            f.write(text)
    return text

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=2)
def get_text_from_arxiv(arxiv_id, doi, paper_id, save=True):
    #get text from pdf url
    pdf_url = f"https://export.arxiv.org/pdf/{arxiv_id}"
    pdf_response = requests.get(pdf_url)
    try:
        get_text_from_response(pdf_response, paper_id, 'arxiv', save)
        skip_doi = '0'
    except:
        skip_doi = (doi,'PDFError')
    
    return skip_doi

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_text_from_elsevier(doi, paper_id, save=True, api_key = 'APIKey'):
    txt = requests.get(f'https://api.elsevier.com/content/article/doi/{doi}?APIKey={api_key}&httpAccept=text/plain')
    txt = txt.text 
    
    if(txt.find("service-error") != -1):
        txt = ''
        skip_doi = (doi, 'ElsevierError')
    else:
        if save:
        # save the text to file
            with open(f'/path/to/papers/elsevier/{paper_id}.txt', 'w') as f:
                f.write(txt)
            skip_doi = '0'

    
    return skip_doi

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_text_from_springer(doi, paper_id, save=True, api_key='APIKey'):

    doi_temp = doi.replace("/", f"%2F")
    xml_url = f'https://api.springernature.com/openaccess/jats?api_key={api_key}&q=doi%3A{doi_temp}&s=1&p=10'
    xml_response = requests.get(xml_url)
    xml_string = xml_response.text
    if(xml_string.find("<body>") == -1):
        txt = ""
        skip_doi = (doi, 'SpringerError')
    else:
        start = xml_string.find("<body>")
        end = xml_string.find('</body>')
        xml_string = xml_string[start+6: end+7]
        txt = re.sub('<[^<]+?>', ' ', xml_string)

        if save:
        # save the text to file
            with open(f'/path/to/papers/springer/{paper_id}.txt', 'w') as f:
                f.write(txt)
            skip_doi = '0'

    return skip_doi

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_text_from_pmc(pmc_id, doi, save=True):
    try:
        xml_url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC{pmc_id}/ascii'
        xml_response = requests.get(xml_url)
        xml_string = xml_response.text
        xml_string = re.sub('<[^<]+?>', ' ', xml_string)
        xml_string = re.sub('surname:', ' ', xml_string)
        xml_string = re.sub(';given-names:', ', ', xml_string)
        if save:
            # save the text to file
            with open(f'/path/to/papers/pmc/{pmc_id}.txt', 'w') as f:
                f.write(xml_string)
            skip_doi = '0'
    except:
        skip_doi = (doi, 'PMCError')
    
    return skip_doi


def main(url):
    soup = get_page_content(url)
    dois = extract_dois_from_page(soup)
    return dois

if __name__ == "__main__":
    main("https://www.fpbase.org/references/")
