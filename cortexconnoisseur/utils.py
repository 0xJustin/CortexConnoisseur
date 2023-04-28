import requests
from bs4 import BeautifulSoup

"""
example code to scape doi's from a webpage
code generated with help from phind.com
"""

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

def main(url):
    soup = get_page_content(url)
    dois = extract_dois_from_page(soup)
    return dois

if __name__ == "__main__":
    main("https://www.fpbase.org/references/")
