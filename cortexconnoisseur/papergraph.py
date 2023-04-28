from concurrent.futures import ThreadPoolExecutor
import requests
import backoff

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_papers_authors_batch(batch):
    """
    Given a batch of papers, get all the authors of those papers.
    batch: tuple of (paper_ids, fields)
    This function is meant to be called by get_papers_authors
    """
    batch, fields = batch
    response = requests.post(
        'https://api.semanticscholar.org/graph/v1/paper/batch',
        params={'fields': [fields]},
        json={"ids": batch}
    )
    return response.json()

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_authors_papers_batch(batch):
    """
    Given a batch of authors, get all the papers of those authors.
    batch: list of author_ids
    """
    response = requests.post(
        'https://api.semanticscholar.org/graph/v1/author/batch',
        params={'fields': 'papers'},
        json={"ids": batch}
    )
    return response.json()

def get_papers_authors(paper_ids, fields='authors,externalIds,citationCount', batchsize=100):
    """
    Using threadpoolexecutor, process many papers in parallel
    This uses the semanticscholar API- refer to their documentation info on the fields
    https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/get_graph_get_paper_autocomplete

    """
    n_batch = (len(paper_ids) // batchsize) + 1
    batches = [(paper_ids[i*batchsize:(i+1)*batchsize], fields) for i in range(n_batch)]

    papers_authors_request = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(get_papers_authors_batch, batches)
        for result in results:
            papers_authors_request.extend(result)

    return papers_authors_request

def get_authors_papers(author_ids, batchsize=100):
    """
    Using threadpoolexecutor, process many authors in parallel
    This uses the semanticscholar API- refer to their documentation info on the fields
   https://api.semanticscholar.org/api-docs/#tag/Author-Data
    """
    n_batch = (len(author_ids) // batchsize) + 1
    batches = [author_ids[i*batchsize:(i+1)*batchsize] for i in range(n_batch)]
    authors_papers_request = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(get_authors_papers_batch, batches)
        for result in results:
            authors_papers_request.extend(result)

    return authors_papers_request


def get_paper_ids(authors_papers_request):
    """
    Takes a list of authors and retrives the semantic scholar paper ids from each author
    """
    new_papers = []
    for i in range(len(authors_papers_request)):
        if authors_papers_request[i] is None or type(authors_papers_request[i]) == str:
            continue

        paper_ids = [paper['paperId'] for paper in authors_papers_request[i]['papers']]
        new_papers.extend(paper_ids)
    return new_papers
    
def get_author_ids(papers_authors_request, doi_dict=None):
    """
    Takes a list of paper and retrives the semantic scholar author ids from each author
    If a dictionary is provided, doi_dict will update as doi: citation count
    """
    new_author_names = set()
    new_author_ids = set()

    for i in range(len(papers_authors_request)):
        if papers_authors_request[i] is None or type(papers_authors_request[i]) == str:
            continue
        authors = papers_authors_request[i]['authors']
        new_names = set([authors[k]['name'] for k in range(len(authors))])
        new_ids = set([authors[k]['authorId'] for k in range(len(authors))])
        new_author_names.update(new_names)
        new_author_ids.update(new_ids)

        if not doi_dict is None:
            doi = papers_authors_request[i]['externalIds'].get('DOI', None)
            if doi is None:
                continue
            doi_dict[doi] = papers_authors_request[i]['citationCount']

    return new_author_names, new_author_ids, doi_dict