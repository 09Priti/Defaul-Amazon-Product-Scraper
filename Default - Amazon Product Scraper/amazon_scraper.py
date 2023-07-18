import os
import time
from datetime import date
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class AmazonProductScraper:
    def __init__(self):
        self.driver = None
        self.category_name = None
        self.formatted_category_name = None

    def open_browser(self):

        opt = Options()

        opt.add_argument("--disable-infobars")
        opt.add_argument("--disable-extensions")
        opt.add_argument('--log-level=OFF')
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])

        url = "https://www.amazon.in/"
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opt)
       
        self.driver.get(url)

       
        time.sleep(3)

    def get_category_url(self):

        self.category_name = input("\n>> Enter the product/category to be searched: ")

        self.formatted_category_name = self.category_name.replace(" ", "+")

       
        category_url = "https://www.amazon.in/s?k={}&ref=nb_sb_noss"

        category_url = category_url.format(self.formatted_category_name)

        print(">> Category URL: ", category_url)

        
        self.driver.get(category_url)
        
        return category_url

    def extract_webpage_information(self):
       
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        page_results = soup.find_all('div', {'data-component-type': 's-search-result'})

        return page_results

    @staticmethod
    def extract_product_information(page_results):
        temp_record = []
        for i in range(len(page_results)):
            item = page_results[i]

           
            a_tag_item = item.h2.a

           
            description = a_tag_item.text.strip()

           
            category_url = "https://www.amazon.in/" + a_tag_item.get('href')

           
            try:
                product_price_location = item.find('span', 'a-price')
                product_price = product_price_location.find('span', 'a-offscreen').text
            except AttributeError:
                product_price = "N/A"

           
            try:
                product_review = item.i.text.strip()
            except AttributeError:
                product_review = "N/A"

           
            try:
                review_number = item.find('span', {'class': 'a-size-base'}).text
            except AttributeError:
                review_number = "N/A"

           
            product_information = (description, product_price[1:], product_review, review_number, category_url)

           
            temp_record.append(product_information)

        return temp_record

    def navigate_to_other_pages(self, category_url):
       
        records = []

        print("\n>> Page 1 - webpage information extracted")

        try:

            max_number_of_pages = "//span[@class='s-pagination-item s-pagination-disabled']"

            number_of_pages = self.driver.find_element_by_xpath(max_number_of_pages)
            print("Maximum Pages: ", number_of_pages.text)
        except NoSuchElementException:
            max_number_of_pages = "//li[@class='a-normal'][last()]"
            number_of_pages = self.driver.find_element_by_xpath(max_number_of_pages)

        for i in range(2, int(number_of_pages.text) + 1):
           
            next_page_url = category_url + "&page=" + str(i)
            self.driver.get(next_page_url)

          
            page_results = self.extract_webpage_information()
            temp_record = self.extract_product_information(page_results)

            extraction_information = ">> Page {} - webpage information extracted"
            print(extraction_information.format(i))

            for j in temp_record:
                records.append(j)

        self.driver.close()

        print("\n>> Creating an excel sheet and entering the details...")

        return records

    def product_information_spreadsheet(self, records):

        today = date.today().strftime("%d-%m-%Y")

        for _ in records:
            file_name = "{}_{}.csv".format(self.category_name, today)
            f = open(file_name, "w", newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(['Description', 'Price', 'Rating', 'Review Count', 'Product URL'])
            writer.writerows(records)
            f.close()

        message = f">> Information about the product '{self.category_name}' is stored in {file_name}\n"

        print(message)

        os.startfile(file_name)


if __name__ == "__main__":
    my_amazon_bot = AmazonProductScraper()

    my_amazon_bot.open_browser()

    category_details = my_amazon_bot.get_category_url()

    my_amazon_bot.extract_product_information(my_amazon_bot.extract_webpage_information())

    navigation = my_amazon_bot.navigate_to_other_pages(category_details)

    my_amazon_bot.product_information_spreadsheet(navigation)
