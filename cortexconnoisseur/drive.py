import papergraph
import utils

def get_papers_and_authors(author_ids, deg=2):
    """
    Author ids: list[str] of author ids from semanticscholar
    deg: int, number of degrees of separation to search. 1 gives thousands, 2 gives millions
    """
    author_names = set([])
    last_ids = set(author_ids)
    all_papers = set()
    paper_level = {}
    author_level = {0: list(author_ids)}
    doi_dict = {}

    for c in range(deg):
        print("Starting iteration {} of {}".format(c+1, deg))
        # turn the set of author ids into a list
        to_query = list(last_ids)
        # get all the papers of all of the authors
        authors_papers_request = papergraph.get_authors_papers(to_query)
        # get all the papers of all the new authors
        new_papers = papergraph.get_paper_ids(authors_papers_request)
        # remove duplicates (papers we've already seen) from the new papers
        new_papers = list(set(new_papers) - all_papers)
        # setting the level of the dict to reflect at what degree of separation we found the paper
        print("Found {} new papers".format(len(new_papers)))
        paper_level[c] = new_papers
        # add the new papers to the set of all papers
        all_papers.update(set(new_papers))
        # get the all authors of the new papers
        papers_authors_request = papergraph.get_papers_authors(new_papers)
        # get all the papers from the new authors and those papers' dois and citations
        new_author_names, new_author_ids, doi_dict = papergraph.get_author_ids(papers_authors_request)
        print("Found {} new authors".format(len(new_author_ids)))

        # remove authors we've already seen
        last_ids = set(new_author_ids) - set(author_ids) 
        author_level[c+1] = list(new_author_names)
        # add the new authors to the set of all authors
        author_names.update(new_author_names)
        author_ids.update(new_author_ids)

    # Desired output is papers, so taking the last set of authors and doing a final iteration over papers
    print("Fetching final papers")
    # turn the set of author ids into a list
    to_query = list(last_ids)
    # get all the papers of all of the authors
    authors_papers_request = papergraph.get_authors_papers(to_query)
    # get all the papers of all the new authors
    new_papers = papergraph.get_paper_ids(authors_papers_request)
    # remove duplicates (papers we've already seen) from the new papers
    new_papers = list(set(new_papers) - all_papers)
    # setting the level of the dict to reflect at what degree of separation we found the paper
    print("Found {} new papers".format(len(new_papers)))
    paper_level[deg] = new_papers
    # add the new papers to the set of all papers
    all_papers.update(set(new_papers))
    return author_ids, all_papers, author_level, paper_level, doi_dict



if __name__ == "__main__":
    import pickle
    # To get these search each author on semanticsholar.com 
    # [Srini Turaga, Arnold Bakker, Ashish Vaswani, William Gray Roncal, Wolfgang Maass, Ernst Niebur, 
    # Konrad Kording, Laura Waller, Loren Looger, Eric Schreiter, Alison Tebom, Li-Huei Tsai, Daphne Koller] 
    author_ids = set([3178417, 38037133, 40348417, 1744493, 145247053, 3271571, 
                      3282030, 144203599, 3595515, 4487712, 11460587, 2342352, 1736370])
    
    author_ids, all_papers, author_level, paper_level, doi_dict = get_papers_and_authors(author_ids)
    extra_dois = utils.main("https://www.fpbase.org/references/")
    pickle.dump(paper_level, open('papers_dict.pkl', 'wb'))
    pickle.dump(doi_dict, open('doi_dict.pkl', 'wb'))
    pickle.dump([author_ids, all_papers, author_level, paper_level, doi_dict, extra_dois], open("data.p", "wb"))