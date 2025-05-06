from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from textblob import TextBlob
from time import sleep
import os
import textwrap
import glob
from tenacity import retry, stop_after_delay
from urllib.parse import urlparse, urlunparse


class MovieReviewsBot:
    def __init__(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.movie_urls = []
        self.movies = {} 

    def run(self):
        self.__clear_results_dir()

        with sync_playwright() as p:
            self.__pw_setup(p)

            self.__read_input_file()

            self.__collect_pages_data()

        self.__save_results()

    def __clear_results_dir(self):
        old_results = glob.glob(os.path.join(self.basedir, "results", "*.txt"))
        for old_result in old_results:
            try:
                os.remove(old_result)
            except FileNotFoundError:
                print(f"File not found: {old_result}")
            except Exception as e:
                print(f"Error deleting {old_result}: {e}")

    def __read_input_file(self):
        input_path = os.path.join(self.basedir, 'movies.txt')
        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = self.__assert_url(line)
                self.movie_urls.append(line)

    def __assert_url(self, line: str):
        line = line.strip()
        if line.startswith("http://") or line.startswith("https://"):
            return line
        
        return self.__get_movie_url(line)
    
    def __get_movie_url(self, line: str):
        self.page.goto('https://www.imdb.com/?ref_=nv_home')
        self.page.wait_for_load_state("networkidle")

        search = self.page.locator('xpath=.//form[@id="nav-search-form"]')

        sdropdown = search.locator('xpath=./div[1]')
        sdropdown.click()
        sleep(0.3)
        sdropdown.locator('xpath=.//*[text()="Títulos"]').click()


        search = self.page.locator('xpath=.//input[@id="suggestion-search"]')
        search.fill(line)
        self.page.keyboard.press('Enter')

        results = self.page.locator('xpath=.//section[@data-testid="find-results-section-title"]/div[2]')
        if "No results found" in results.text_content():
            raise Exception(f"Movie title error: No movie with title '{line}' found")
        movie_url = urlparse(results.locator('xpath=//a').first.get_attribute('href'))            
        movie_url = urlunparse(movie_url._replace(query="", fragment=""))
        return 'https://www.imdb.com' + movie_url

    def __collect_pages_data(self):
        for movie_url in self.movie_urls:
            movie_title = self.__load_page(movie_url)
            sleep(0.3)
            review_list = self.__get_page_reviews()
    
            reviews = []
            for review in review_list:
                self.__handle_spoiler_btn(review)
                
                review_elements = review.locator('xpath=./div').all()
                
                self.__remove_extra_element(review_elements)

                # Recoleta elementos após tratamento
                review_elements = review.locator('xpath=./div').all()

                review_title, review_desc, review_polarity = self.__get_review_data(review_elements)

                reviews.append({
                    'title':review_title,
                    'desc':review_desc,
                    'polarity':review_polarity
                })
            self.movies[movie_title] = reviews
    
    def __pw_setup(self, p):
        self.browser: Browser = p.chromium.launch(headless=False)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page = self.context.new_page()

    def __load_page(self, movie_url: str):
        self.page.goto(movie_url)
                        
        movie_title = self.page.locator('xpath=.//span[@data-testid="hero__primary-text"]').text_content()
        
        userReviewsDiv = self.page.locator('xpath=.//section[@data-testid="UserReviews"]/div')
        userReviewsDiv.locator("a").click()

        return movie_title
        
    def __get_page_reviews(self):
        reviewsSection = self.page.locator('xpath=//*[@id="__next"]/main/div/section/div/section/div/div[1]/section[1]')
        return reviewsSection.locator('xpath=.//article/div[1]/div[1]').all()[0:10]

    def __remove_extra_element(self, review_elements: list):
        if len(review_elements) == 3:
            review_elements[0].evaluate('el => el.remove()')
            del review_elements[0]

    @retry(stop=stop_after_delay(1))
    def __handle_spoiler_btn(self, review):
        has_btn = review.evaluate('el => el.getElementsByTagName("button").length > 0')
        if has_btn and review.locator('button').text_content() == 'Spoiler':
                review.locator('button').click()
                spoiler_div = review.locator('xpath=.//*[@data-testid="review-spoiler-content"]/div[1]')
                spoiler_div.evaluate('el => el.remove()')
         
    @retry(stop=stop_after_delay(1))
    def __get_review_data(self, review_elements):
        if len(review_elements) == 2:
            title = review_elements[0].text_content()
            desc = review_elements[1].text_content()
        else:
            raise Exception("Error collecting review elements: Couldn't find separate title and description alements.")
        
        polarity = self.__get_review_polarity(desc)
        return title, desc, polarity
         
    def __get_review_polarity(self, desc: str):
        polarity = TextBlob(desc).sentiment.polarity
        if polarity > 0:
            return "Positive"
        elif polarity == 0:
            return "Neutral"
        else:
            return "Negative"

    def __save_results(self):
        results_path = os.path.join(self.basedir, "results")
        for movie in self.movies:
            out_path = os.path.join(results_path, f'{movie}.txt')
            with open(out_path, 'w', encoding='utf-8') as file:
                for review in self.movies[movie]:
                    title = self.__insert_newlines(review['title'])
                    pol = f"[{review['polarity']} review]"
                    desc = self.__insert_newlines(review['desc'])
                    content = f"{title}\n\n{pol}\n\n{desc}\n{'-'*64}\n\n"
                    file.write(content)  

    def __insert_newlines(self, s: str, every=64):
        return '\n'.join(textwrap.wrap(s, every))           


if __name__ == '__main__':
    MovieReviewsBot().run()