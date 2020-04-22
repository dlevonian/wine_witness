
import time
import re
import os

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
urls = urls[:100]



tic = time.time()



def retrieve_wine(urls):

    driver = webdriver.Chrome(driver_path)
    
    for url in urls:
        driver.get(url)

        try:
            xpath_price = '//span[@class="purchaseAvailability__currentPrice--3mO4u"]'
            _ = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath_price)))
            # element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath_price)))
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
        wait1 = WebDriverWait(driver, 1)

        
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


    # <a class="anchor__anchor--3DOSm" href="/wine-styles/californian-pinot-noir">Californian Pinot Noir</a>
    # <div class="wineFacts__factHeading--pXg1x">Wine style</div>


        # print(winery, vintage)
        # print(wine_type, region, country)
        # print(avg_rating, n_ratings)
        # print(f'CHARS={len(taste_dimensions)}')
        # print(td_dict)
        # print(f'REVIEWS={len(reviews)}')
        # print(reviews)
        # print('-'*50)
        # print(img_link)
        # print('*'*50)
        # print(wine_style)
        # print('*'*50)


toc = time.time()
print(f'TIME: {toc-tic:.1f}')

