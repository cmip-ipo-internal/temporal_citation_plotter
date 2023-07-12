import os
import pdb
import json 
import pandas as pd 
import time
import urllib.parse
import requests
import xmltodict
import json

from datetime import datetime
session = requests.Session()
import http.client
http.client.HTTPConnection.debuglevel = 1

debug = True

if debug:
    # keep this off as it displays your credentials as plain text in the output. 
    import logging
    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")

    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True





headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

# Read a specific environment variable
user = os.environ.get('CMIP')
pwd = os.environ.get('CROSSPWD')
role = 'heso'

def get_info(doi):


    
    # Encode the username and password
    encoded_username = urllib.parse.quote(user, safe='')
    encoded_password = urllib.parse.quote(pwd, safe='')

    # Construct the combined URL with encoded username and password
    url = f'https://doi.crossref.org/servlet/getForwardLinks?doi={doi}&usr={encoded_username}/{role}&pwd={encoded_password}'

    if debug: 
        print(url)

    # Make the HTTP request and retrieve the XML data
    print(datetime.now())
    try:
        # each of these seem to take a minute. 
        response = session.get(url,headers=headers)
    except ConnectionError:
        assert False, 'You must be connected to the internet for this to work.'

    print('--done-- ',datetime.now())
    xml_data = response.text

    # Convert XML to JSON
    # json_data = json.dumps(xmltodict.parse(xml_data), indent=4)
    
    return xmltodict.parse(xml_data)['crossref_result']['query_result']['body']['forward_link']

fail = []

def parse_result(data):
    
    for k in data.keys():
        if '_cite' in k:
            data = data[k]
            title = k.replace('cite','title').replace('book','chapter').replace('conf','paper')
            medium = k.replace('cite','title').replace('book','volume').replace('conf','volume').replace('report','volume')
            break

    # ignore condition for places where the year is missing does not exist e.g. 'Forest Service Research Data Archive'
    if 'year' not in data: 
        return 
    try:
        # Extracting the journal title
        journal_title = data.get(title,k.split('_')[0])
        # Extracting the article title
        article_title = data.get(medium) or data.get('series_title') or data['title']
        # Extracting the contributors
        contributors = []

        if 'contributors' in data:
            for _,contributor in data['contributors'].items():
                if isinstance(contributor,list): 
                    for author in contributor:
                        # print(author)

                        name = f"{author.get('given_name','')} {author['surname']}"
                        contributors.append(name)
                else:
                    name = f"{contributor.get('given_name','')} {contributor['surname']}"
                    # print(contributor,name)
                    contributors.append(name)
        else:
            contributors = ['various']





        # contributors = [ f"{contributor['given_name']} {contributor['surname']}" for _,contributor in data['contributors'].items()]
        # Extracting the year
        year = int(data['year'])

        # Extracting the DOI text
        doi = data['doi']['#text']

        # Returning a dictionary with the extracted values
        return {
            'journal_title': journal_title,
            'article_title': article_title,
            'contributors': contributors,
            'year': year,
            'doi': doi
        }
    
    except KeyError as e :
        print()
        print(e)
        print('keyerror',data)
        assert False
        

    # except TypeError as e:
    #     print()
    #     print(e)
    #     print([
    #         fail.append(f"{contributor['given_name']} {contributor['surname']}") for _,contributor in data['contributors'].items()])
    #     print('fail' , data[title])
    #     return None
    except AssertionError:
        ...


# doi = '10.5194/gmd-9-2853-2016'


# # test = pd.DataFrame(filter(bool,map(parse_result, get_info(doi))))




papers = pd.read_csv('list.csv')


total = {}


for paper in papers.iterrows():
    paper = paper[1]
    name = f"{paper.NAME}__{paper.YEAR}__{paper.LEAD}__{paper.DOI}".replace(' ','+').replace('.','(dot)').replace(';','\;').replace('/','(slash)')
    filename = f'citation_data/{name}.csv'

    
    if os.path.exists(filename):
        data =pd.read_csv(filename)
        print('read existing file:',filename)
    else:
        result = get_info(paper.DOI)
        data = pd.DataFrame(filter(bool,map(parse_result,result )))
        data.to_csv(filename)

    total[paper.NAME] = len(data)
    time.sleep(1)

pd.Series(total).to_csv('total_summary.csv')





# groupby year count

