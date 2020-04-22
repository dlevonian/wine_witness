import numpy as np
import time

import os
import re
import csv

from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

PATH = '/Central/NYCDSA/_1_scraping/wine_witness/'

def extract_urls_from_xml():
    """A one-time function to extract URLs from the 8 raw XML files downloaded from vivino.com 
    8 XML files are named sitemap_wines_0.xml etc.
    Each wine item in the XML comes in the following format:
      <url>
        <loc>https://www.vivino.com/it-scacciadiavoli-brut-rose-metodo-classico/w/10</loc>
        <lastmod>2020-04-15T10:00:00Z</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
      </url>
    Returns:
        a .txt file with 380,090 URLs to individual wine items
    """

    urls=[]
    tic = time.time()

    for i in range(8):
        xml_file = PATH + 'Vivino_raw_xml/' + f'sitemap_wines_{i}.xml'
        
        with open(xml_file, 'r') as f:
            soup = BeautifulSoup(f.read(),'lxml')

        for url in soup.find_all('loc'):
            urls.append(url.text)
        
        toc = time.time()
        print(f'XML: {i}    urls: {len(urls):,}     {toc-tic:.1f} sec') 

    print(f'Total urls: {len(urls):,}')
    print(np.random.choice(urls, 10))
    
    text_file = PATH + 'ww_all_links_20200415.txt'
    with open(text_file, 'w') as f:
        f.writelines(url+'\n' for url in urls[1:])  # 1st line is not an wine item URL 


def load_all_urls(file_name='ww_all_links_20200415.txt'):
    # loads all urls into a list
    with open(os.path.join(PATH,file_name), 'r') as f:
        urls = list(f.readlines())
    return [s.strip() for s in urls] #to remove \n
    

def identify_in_stock(index_start = 0,
                    index_end   = 380_090
                   ):
    """Identify if wine items are in stock (i.e. are SKUs with a price tag) on vivino.com
    Only about 5.3% of all items are in stock, the rest are reviewed but not sold
    This function performs the initial fast crawl (~0.5 sec/item) to filter out ~95% 'empty' URLs
    Arguments:
        index_start
        index_end
    Returns:
        a saved csv file of (wine_id, in_stock) for URLs within the [index_start:index_end]
    """
    
    def price_numeric(text):
        # checks if HTML contains a price tag followed by a digit
        return bool(re.findall('price":"\d', text))

    def instock_string(text):
        # checks if HTML contains 'InStock'
        return bool(re.findall('InStock', text))

    http = urllib3.PoolManager()
    urls = load_all_urls()

    wine_id  = []
    in_stock = []
    tic = time.time()

    for i, url in enumerate(urls[index_start:index_end]):

        r = http.request('GET', url)
        
        if r.status==404: # ignore 404
            continue

        if r.status!=200: # interrupt if anything except 200 and 404, e.g. 529
            index_end = index_start+i
            print(f'\nHTTP {r.status}')
            print(f'Scan terminated at {index_end:-,}')
            break    

        # wine_id is a unique number present in the URL
        wine_id.append(int(url.split('/')[-1]))  

        # if any of the 2 patterns appear in HTML body, identify as candidate SKU (in_stock)
        text = str(r._body)
        in_stock.append(price_numeric(text) or instock_string(text))

        print(f'\r{100*(i+1)/(index_end-index_start):.2f}%  {i+1:,}     '+\
              f'{np.sum(in_stock):,} SKUs     {time.time()-tic:.1f} sec',end='')
        
        # empirical sleep time to avoid HTTP status code 529 
        time.sleep(np.random.uniform(0,0.5))

    csv_file = PATH + f'in_stock/in_stock_{index_start}_{index_end}.csv'  

    with open(csv_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(zip(wine_id, in_stock))


def produce_final_url_list():
    """Produce a final URL list of candidate in stock items to be processed by Selenium
    Returns:
        a saved csv file of URLs
    """

    urls = load_all_urls()
    url_dict = {int(url.split('/')[-1]):url for url in urls}

    in_stock_path = os.path.join(PATH, 'in_stock')
    in_stock_files = [f for f in os.listdir(in_stock_path)]
    
    master_list=[]
    for file_name in in_stock_files:
        with open(os.path.join(in_stock_path, file_name), 'r') as f:
            reader = csv.reader(f)
            master_list.extend(list(reader))
        print(f'Appended {file_name}')

    # convert ['10', 'True'] loaded from csv into {10: True}
    master_dict = {int(k):v=='True' for k,v in master_list}
    
    # filter only those url_dict items for which master_dict[id]==True
    final_dict = {k:v for (k,v) in url_dict.items() if k in master_dict.keys() if master_dict[k]}
    final_list = list(final_dict.values())
    print(f'Total candidate URLs: {len(final_list):,}')

    text_file = os.path.join(PATH, 'ww_in_stock_urls.txt')
    with open(text_file, 'w') as f:
        f.writelines(url+'\n' for url in final_list)
