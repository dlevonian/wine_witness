
import time
import numpy as np
import re
import os
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WineWitness():
    """Spider class for scraping vivino.com SKUs
    Scrapes 18 key features of a wine item SKU
    Ignores wine items which are not sold by vivino.com (the price field is empty)
    Approximate scraping speed, optimized for uninterrupted access: 4.5 sec/item, i.e. ~20,000 items per 24 hours
    Validation, type conversion and formatting is performed BEFORE saving to csv
    """

    driver_path = r'C:\Users\Dmitri Levonian\chromedriver.exe'
    PATH = '/Central/NYCDSA/_1_scraping/wine_witness/'

    def __init__(self, start_index, end_index):
        
        self.tic = time.time()
        self.driver = webdriver.Chrome(WineWitness.driver_path)

        with open(os.path.join(WineWitness.PATH, 'ww_in_stock_urls.txt'), 'r') as f:
            urls = list(f.readlines())
        urls = [s.strip() for s in urls]
        self.urls = urls[start_index:end_index]

    def deploy(self):

        with open(os.path.join(WineWitness.PATH, 'ww_main.csv'), 'a', newline='') as f:
            writer = csv.writer(f)

            for count, url in enumerate(self.urls):
                
                time.sleep(1 + np.random.uniform(0,1))
                try:
                    self.driver.get(url)
                except:
                    print(f'Terminated: could not open {url}')
                    break
            
                features = self.retrieve_item(url)

                if features:
                    features = self.process_item(features)
                    try:
                        writer.writerow(features)
                    except:        
                        pass

                print(f'{count+1}  {time.time()-self.tic:.2f} sec  {url}')  
            print(f'COMPLETE: {time.time()-self.tic:.2f} sec')  


    def retrieve_item(self, url):
        try:
            xpath_price = '//span[@class="purchaseAvailability__currentPrice--3mO4u"]'
            _ = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath_price)))
            price = self.driver.find_element_by_xpath(xpath_price).text
            # the only two elements converted and validated right when they are scraped
            price = float(re.sub(r'[^\d.]', '', price))
            wine_id = int(url.split('/')[-1])    
        except:
            # if either price or wine_id cannot be accessed and/or validated,
            # dicard the item and proceed to the next url
            return None
        
        try:
            winery = self.driver.find_element_by_xpath('//a[@class="anchor__anchor--2QZvA winePageHeader__winery--3l9X6"]').text
            vintage = self.driver.find_element_by_xpath('//span[@class="winePageHeader__vintage--2Vux3"]').text
        except:
            winery,vintage = None,None     

        try:
            wine_type = self.driver.find_element_by_xpath('//span[@class="wineLocationHeader__wineType--14nrC"]').text
            region = self.driver.find_element_by_xpath('//a[@class="anchor__anchor--3DOSm wineLocationHeader__region--1cbip"]').text
            country = self.driver.find_element_by_xpath('//a[@class="anchor__anchor--3DOSm wineLocationHeader__country--1RcW2"]').text
        except:
            wine_type, region, country = None, None, None
        
        # Extract wine style from 2 possible (different) locations. Not all wines have this field
        try:
            wine_style_header = self.driver.find_element_by_xpath("//*[contains(text(), 'Wine style')]")
            wine_style = wine_style_header.find_element_by_xpath('..//a[@class="anchor__anchor--3DOSm"]').text
        except:
            wine_style = None

        try:
            avg_rating = self.driver.find_element_by_xpath('//div[@class="vivinoRatingWide__averageValue--1zL_5"]').text
        except:
            avg_rating = None

        try:
            n_ratings = self.driver.find_element_by_xpath('//div[@class="vivinoRatingWide__basedOn--s6y0t"]').text
        except:
            try:
                n_ratings = self.driver.find_element_by_xpath('//span[@class="vivinoRating__ratingCount--NmiVg"]').text
            except: 
                n_ratings = None

        self.driver.execute_script("window.scrollTo(0, 1000);")
        wait1 = WebDriverWait(self.driver, 5)

        # Extract the 4 taste dimensions represented as progress bars on vivino website:
        #  - Light/Bold 
        #  - Smooth/Tannic
        #  - Dry/Sweet
        #  - Soft/Acidic
        # Some wine SKUs have all 4 dimensions, some only a subset (e.g.3) and some others - none
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
        
        # Extract the top 3 helpful reviews
        self.driver.execute_script("window.scrollTo(0, 2000);")
        reviews=[]
        try:
            review_cards = self.driver.find_elements_by_xpath('//p[@class="reviewCard__reviewNote--fbIdd"]')
            for review_card in review_cards:
                    reviews.append(review_card.text)
        except:
            review_cards=[]
        
        # Extract the link to a bottle image (about 40Kb) for possible augmentation of the feature set
        try:
            img_link = self.driver.find_element_by_xpath('//meta[@property="og:image"]').get_attribute("content")
        except:
            img_link = None

        return (wine_id,
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
                img_link)


    @staticmethod
    def process_item(features):

        def extract_td(td_dict, td):
            if td not in td_dict.keys():
                return None
            left = float(re.search('left: (.+?)(%|p)', td_dict[td]).group(1))
            width = float(re.search('width: (.+?)%', td_dict[td]).group(1))
            return left+width/2

        def remove_utf(string):
            return ''.join([char for char in string if ord(char)<128])

        (wine_id,
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
        img_link) = features
    
        # wine_id -- intact
        # url -- intact
        # price -- intact
        # winery -- intact
        # vintage -- intact
        wine_type = wine_type[:-6] if wine_type!=None else None
        # wine_style -- intact
        # region -- intact
        avg_rating = float(avg_rating) if avg_rating!=None else None
        n_ratings = int(re.sub(r'\D', '', n_ratings)) if n_ratings!=None else None

        td_light_bold = extract_td(td_dict, 'Light')
        td_smooth_tannic = extract_td(td_dict, 'Smooth')
        td_dry_sweet = extract_td(td_dict, 'Dry')
        td_soft_acidic = extract_td(td_dict, 'Soft')
        
        review_1 = remove_utf(reviews[0]) if len(reviews)>0 else None
        review_2 = remove_utf(reviews[1]) if len(reviews)>1 else None
        review_3 = remove_utf(reviews[2]) if len(reviews)>2 else None
        # img_link -- intact
        
        return (wine_id,
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


if __name__=="__main__":
    # ww = WineWitness(10_000,19_906)
    # ww.deploy()


