
import time
import numpy as np
import re
import os
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver_path = r'C:\Users\Dmitri Levonian\chromedriver.exe'
PATH = '/Central/NYCDSA/_1_scraping/wine_witness/'

text_file = os.path.join(PATH, 'ww_in_stock_urls.txt')
with open(text_file, 'r') as f:
    urls = list(f.readlines())
urls = [s.strip() for s in urls]
# urls = urls[:100]



tic = time.time()


def retrieve_batch(urls):

    driver = webdriver.Chrome(driver_path)

    # batch (list) variables start with underscore 
    _wine_id, _url, _price,  _winery, _vintage, _wine_type, _wine_style,\
    _region, _country, _avg_rating, _n_ratings, _td_dict, _reviews, _img_link = ([] for _ in range(14))
    
    for count, url in enumerate(urls):
        
        time.sleep(2 + np.random.uniform(0,2))
        try:
            driver.get(url)
        except:
            if count>0:
                pipeline_save_batch(_wine_id,
                                    _url,
                                    _price,
                                    _winery,
                                    _vintage,
                                    _wine_type,
                                    _wine_style,
                                    _region,
                                    _country,
                                    _avg_rating,
                                    _n_ratings,
                                    _td_dict,
                                    _reviews,
                                    _img_link,
                                    )

        try:
            xpath_price = '//span[@class="purchaseAvailability__currentPrice--3mO4u"]'
            _ = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath_price)))
            price = driver.find_element_by_xpath(xpath_price).text
            # print(f'Found price: {price}    {url}')
        except:
            continue
        
        wine_id = int(url.split('/')[-1])
        winery = driver.find_element_by_xpath('//a[@class="anchor__anchor--2QZvA winePageHeader__winery--3l9X6"]').text
        vintage = driver.find_element_by_xpath('//span[@class="winePageHeader__vintage--2Vux3"]').text

        wine_type = driver.find_element_by_xpath('//span[@class="wineLocationHeader__wineType--14nrC"]').text
        region = driver.find_element_by_xpath('//a[@class="anchor__anchor--3DOSm wineLocationHeader__region--1cbip"]').text
        country = driver.find_element_by_xpath('//a[@class="anchor__anchor--3DOSm wineLocationHeader__country--1RcW2"]').text

        try:
            wine_style_header = driver.find_element_by_xpath("//*[contains(text(), 'Wine style')]")
            wine_style = wine_style_header.find_element_by_xpath('..//a[@class="anchor__anchor--3DOSm"]').text
        except:
            wine_style = None

        avg_rating  = driver.find_element_by_xpath('//div[@class="vivinoRatingWide__averageValue--1zL_5"]').text

        try:
        	n_ratings=driver.find_element_by_xpath('//div[@class="vivinoRatingWide__basedOn--s6y0t"]').text
        except:
            try:
            	n_ratings=driver.find_element_by_xpath('//span[@class="vivinoRating__ratingCount--NmiVg"]').text
            except:	
                n_ratings=0

        driver.execute_script("window.scrollTo(0, 1000);")
        wait1 = WebDriverWait(driver, 5)

        
        td_dict={}
        try:
            taste_dimensions = wait1.until(EC.presence_of_all_elements_located((By.XPATH,
    									'//div[@class="tasteStructure__tasteCharacteristic--1rMFl"]')))
            for taste_dimension in taste_dimensions:
                    
                    td_key = taste_dimension.\
                    find_element_by_xpath('./div[@class="tasteStructure__property--loYWN"]').text 

                    td_value = taste_dimension.\
                    find_element_by_xpath('.//span[@class="indicatorBar__progress--3aXLX"]').get_attribute("style")
                    
                    td_dict[td_key]=td_value  #to be later processed as value=left+width/2 (invariant to scale)
        except:
            taste_dimensions=[]
        

        reviews=[]
        try:
            review_cards = driver.find_elements_by_xpath('//p[@class="reviewCard__reviewNote--fbIdd"]')
            for review_card in review_cards:
                    reviews.append(review_card.text)
        except:
            review_cards=[]
        
        img_link = driver.find_element_by_xpath('//meta[@property="og:image"]').get_attribute("content")
         
        # accumulate the batch
        _wine_id.append(wine_id)
        _url.append(url)
        _price.append(price)
        _winery.append(winery)
        _vintage.append(vintage)
        _wine_type.append(wine_type)
        _wine_style.append(wine_style)
        _region.append(region)
        _country.append(country)
        _avg_rating.append(avg_rating)
        _n_ratings.append(n_ratings)
        _td_dict.append(td_dict)
        _reviews.append(reviews)
        _img_link.append(img_link)

        print(f'{count}  {time.time()-tic:.2f} sec  {url}')  

    pipeline_save_batch(_wine_id,
                        _url,
                        _price,
                        _winery,
                        _vintage,
                        _wine_type,
                        _wine_style,
                        _region,
                        _country,
                        _avg_rating,
                        _n_ratings,
                        _td_dict,
                        _reviews,
                        _img_link,
                        )
    


def pipeline_save_batch(wine_id,
                        url,
                        price,
                        winery,
                        vintage,
                        wine_type,
                        wine_style,
                        region,
                        country,
                        avg_rating,
                        n_ratings,
                        td_dict,
                        reviews,
                        img_link,
                        ):
    
    # wine_id -- intact
    # url -- intact
    price = [float(re.sub(r'[^\d.]', '', x)) for x in price]
    # winery -- intact
    # vintage -- intact
    wine_type = [x[:-6] for x in wine_type]
    # wine_style -- intact
    # region -- intact
    avg_rating = [float(x) for x in avg_rating]
    n_ratings = [int(re.sub(r'\D', '', x)) for x  in n_ratings]
    td_light_bold = list(map(lambda s: extract_td(s, 'Light'), td_dict))
    td_smooth_tannic = list(map(lambda s: extract_td(s, 'Smooth'), td_dict))
    td_dry_sweet = list(map(lambda s: extract_td(s, 'Dry'), td_dict))
    td_soft_acidic = list(map(lambda s: extract_td(s, 'Soft'), td_dict))
    review_1 = remove_utf(list(zip(*reviews))[0])
    review_2 = remove_utf(list(zip(*reviews))[1])
    review_3 = remove_utf(list(zip(*reviews))[2])
    # img_link -- intact
    
    zipped_features = zip(wine_id,
                            url,
                            price,
                            winery,
                            vintage,
                            wine_type,
                            wine_style,
                            region,
                            country,
                            avg_rating,
                            n_ratings,
                            td_light_bold,
                            td_smooth_tannic,
                            td_dry_sweet,
                            td_soft_acidic,
                            review_1,
                            review_2,
                            review_3,
                            img_link)
    # print(list(zipped_features))  # DEBUG

    PATH = '/Central/NYCDSA/_1_scraping/wine_witness/'
    csv_file = os.path.join(PATH, 'ww_main.csv')

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(zipped_features)


def extract_td(td_dict, td):
    if td not in td_dict.keys():
        return None
    left = float(re.search('left: (.+?)(%|p)', td_dict[td]).group(1))
    width = float(re.search('width: (.+?)%', td_dict[td]).group(1))
    return left+width/2


def remove_utf(arr):
    return [''.join([char for char in string if ord(char)<128]) for string in arr]


test_urls = urls[105:110]
retrieve_batch(test_urls)

toc = time.time()
print(f'TIME: {toc-tic:.1f}')

