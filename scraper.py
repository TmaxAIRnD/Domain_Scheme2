from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from data_models import Book, Author, Media, Corp

import re
from config import Config
import time

class Scraper:
    def __init__(self):
        chrome_options = Options()
        if Config.HEADLESS:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.books, self.authors, self.media = [], [], []

    def scrape(self):
        self.driver.get(Config.BOOK_BASE_URL)
        books, authors, media = self.books, self.authors, self.media

        time.sleep(3)
        print("-----------------------scraping start--------------------")
        
        page_num = 1
        num = 0
        while page_num <= Config.MAX_PAGE:
            items = self.driver.find_elements(By.CSS_SELECTOR, ".prod_item")[:Config.BOOK_COUNT]
            for item in items:
                info = item.find_element(By.CSS_SELECTOR, ".prod_info")

                title = info.text.strip()
                detail_link = info.get_attribute('href')

                try:
                    summary = item.find_element(By.CSS_SELECTOR, ".prod_introduction").text
                except NoSuchElementException:
                    summary = '정보 없음'
                                
                self.driver.execute_script("window.open(arguments[0]);", detail_link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(5)

                category_list_item = self.driver.find_element(By.CSS_SELECTOR, ".category_list_item")

                # 작가
                author_element = self.driver.find_element(By.CSS_SELECTOR, ".author a")
                author = author_element.text

                # 출판사 이름 추출
                publisher_element = self.driver.find_element(By.CSS_SELECTOR, ".publish_date a")
                publisher = publisher_element.text

                # 출판일 추출
                publish_date_element = self.driver.find_element(By.CSS_SELECTOR, ".publish_date")
                publish_date_text = publish_date_element.text
                published_date = publish_date_text.replace(publisher, '').strip(' ·')

                # 평점
                rating_element = self.driver.find_element(By.CSS_SELECTOR, 'input.form_rating.rating-input')
                rating_value = rating_element.get_attribute('value')

                # 찾고자 하는 항목들 리스트로 준비
                values = {}

                for content in ('ISBN', '발행(출시)일자', '쪽수', '크기', '언어'):
                    try:
                        element = self.driver.find_element(By.XPATH, f"//th[contains(text(), '{content}')]/following-sibling::td")
                        values[content] = element.text
                        if values[content] == "준비중":
                            values[content] = "정보 없음"
                    except NoSuchElementException:
                        if content != "언어":
                          values[content] = "정보 없음"
                        else:
                          values[content] = "한국어"  

                category_links = category_list_item.find_elements(By.CSS_SELECTOR, ".intro_category_link")

                if len(category_links) > 1 :  
                    cate = category_links[1].text
                else:
                    cate = "정보 없음"

                try:
                  tab_texts_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product_keyword_pick .tab_text")
                  if tab_texts_elements:
                      tab_texts = [element.text for element in tab_texts_elements]
                  else:
                      tab_texts = ["정보 없음"]
                except Exception as e:
                  print(f"오류 발생: {e}")
                  tab_texts = ["정보 없음"]

                last_genre_text, last_birth_text = '정보 없음', '정보 없음'

                prod_type_items = self.driver.find_elements(By.CSS_SELECTOR, ".prod_type_list .prod_type_item")
                product = []
                
                for item in prod_type_items:
                    prod_type = item.find_element(By.CSS_SELECTOR, ".prod_type").text
                    product.append(prod_type)
                    print(f"prod_type {prod_type}")
                
                ebook = "O" if "ebook" in product or "sam" in product else "X"

                first_author_link = self.driver.find_element(By.CSS_SELECTOR, ".author a")

                href = first_author_link.get_attribute('href')
                match = re.search(r'chrcCode=(\w+)', href)

                chrcCode = match.group(1)
                new_url = f"{Config.AUTHOR_PROFILE}{chrcCode}"
                
                self.driver.execute_script(f"window.open('{new_url}');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(2)

                person_genre_divs = self.driver.find_elements(By.CSS_SELECTOR, '#infoPerson .person_genre')
                person_bitrh_divs = self.driver.find_elements(By.CSS_SELECTOR, '#infoPerson .person_detail_info_box')

                if person_genre_divs:
                    genre_elements = person_genre_divs[0].find_elements(By.CLASS_NAME, 'genre')
                    if genre_elements:
                        last_genre_text = genre_elements[-1].text.split("＞")[-1]
                        print(last_genre_text)
                
                birth_element = False
                if person_bitrh_divs:
                    try:
                      birth_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '출생지')]/following-sibling::span[@class='desc']")
                      last_birth_text = birth_element.text
                    except NoSuchElementException:
                        pass

                # -------------------------------------------------------------
                book = Book(id=num, title=title, author=author, publisher=publisher, published_date=published_date,
                            category=cate, rating_value=rating_value, isbn=values['ISBN'], page_num=values['쪽수'], size=values['크기'].split(" mm")[0],
                            language=values['언어'], keywords=tab_texts, summary=summary)
                books.append(book)

                author = Author(author=author, country=last_birth_text, job=last_genre_text)
                authors.append(author)

                media_item = Media(title=title, paper_book="O", ebook=ebook)
                media.append(media_item)

                num = num + 1
                print(num, title)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            page_num += 1
            next_page = self.driver.find_element(By.CSS_SELECTOR, f'a[data-index="{page_num}"]')
            self.driver.execute_script("arguments[0].click();", next_page)
    
            time.sleep(3)

        return books, authors, media 

    def search_and_crawl(self, query):

        self.driver.get(Config.SEARCH_CORP) # Naver
        search_box = self.driver.find_element(By.NAME, 'query')
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)

        time.sleep(2) 

        try:
            industry = self.driver.find_element(By.XPATH, "//dt[contains(text(), '업종')]/following-sibling::dd").text
        except Exception as e:
            industry = "출판업"
            print(f"Error finding industry: {e}")
        try:
            products = self.driver.find_element(By.XPATH, "//dt[contains(text(), 기업구분')]/following-sibling::dd").text
        except Exception as e:
            products = "중소기업"
            print(f"Error finding products: {e}")

        return Corp(publisher=query, sector=industry, company_size=products)
    
    def scrape_corps_from_books(self):
        corps = []
        
        for book in self.books:
            corp_data = self.search_and_crawl(book.publisher)
            corps.append(corp_data)
        
        return corps

    def close(self):
        self.driver.quit()