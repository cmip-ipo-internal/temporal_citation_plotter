from scholarly import scholarly
import pandas as pd
# !conda install -c conda-forge scholarly
import time

from scholarly import ProxyGenerator
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)
# Must use a proxy to avoid getting your ip blocked 

def get_citations(doi):

    time.sleep(1)
    match = scholarly.search_single_pub('doi:'+doi)
    return  match.get('num_citations',0)


papers = pd.read_csv('list.csv')
total = {}


for paper in papers.iterrows():

    paper = paper[1]
    print(paper.NAME)
    # name = f"{paper.NAME}__{paper.YEAR}__{paper.LEAD}__{paper.DOI}".replace(' ','+').replace('.','(dot)').replace(';','\;').replace('/','(slash)')
    # filename = f'citation_data/{name}.csv'
    total[paper.NAME] = get_citations(paper.DOI)


print(total)


pd.DataFrame(total).to_csv('scholar_total.csv')