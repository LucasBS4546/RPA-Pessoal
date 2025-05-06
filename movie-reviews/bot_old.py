from playwright.sync_api import sync_playwright
from textblob import TextBlob
from time import sleep
import os
import textwrap
import glob
from tenacity import retry, stop_after_delay

def main():
        basedir = os.path.abspath(os.path.dirname(__file__))
        movie_urls = []
        movies = {}

        clear_results_dir(basedir)
        read_input_file(movie_urls, basedir)

        with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                
                for movie_url in movie_urls:
                        movie_title = load_page(movie_url, page)
                        sleep(0.3)
                        review_list = get_page_reviews(page)
                
                        reviews = []
                        for review in review_list:
                                handle_spoiler_btn(review)

                                review_elements = review.locator('xpath=./div').all()

                                review_title, review_desc = get_review_data(review_elements)
                                polarity = get_review_polarity(review_desc)

                                reviews.append({
                                        'title':review_title,
                                        'desc':review_desc,
                                        'polarity':polarity
                                })
                        movies[movie_title] = reviews
        save_results(movies, basedir)


def clear_results_dir(basedir):
        old_results = glob.glob(os.path.join(basedir, "results", "*.txt"))
        for old_result in old_results:
                try:
                        os.remove(old_result)
                except FileNotFoundError:
                        print(f"File not found: {old_result}")
                except Exception as e:
                        print(f"Error deleting {old_result}: {e}")

def read_input_file(movie_urls, basedir):
        input_path = os.path.join(basedir, 'movies.txt')
        with open(input_path, 'r') as file:
                for line in file:
                        movie_urls.append(line)

def load_page(movie_url, page):
        page.goto(movie_url)
                        
        movie_title = page.locator('xpath=.//span[@data-testid="hero__primary-text"]').text_content()
        
        userReviewsDiv = page.locator('xpath=.//section[@data-testid="UserReviews"]/div')
        userReviewsDiv.locator("a").click()

        return movie_title

def get_page_reviews(page):
        reviewsSection = page.locator('xpath=//*[@id="__next"]/main/div/section/div/section/div/div[1]/section[1]')
        return reviewsSection.locator('xpath=.//article/div[1]/div[1]').all()[0:10]

def insert_newlines(s, every=64):
        return '\n'.join(textwrap.wrap(s, every))

@retry(stop=stop_after_delay(1))
def handle_spoiler_btn(review):
        has_btn = review.evaluate('el => el.getElementsByTagName("button").length > 0')
        if has_btn and review.locator('button').text_content() == 'Spoiler':
                review.locator('button').click()
                spoiler_div = review.locator('xpath=.//*[@data-testid="review-spoiler-content"]/div[1]')
                spoiler_div.evaluate('el => el.remove()')

def get_review_data(review_elements):
        if len(review_elements) == 3:
                review_title = review_elements[1].text_content()
                review_desc = review_elements[2].text_content()
                return review_title, review_desc
        elif len(review_elements) == 2:
                review_title = review_elements[0].text_content()
                review_desc = review_elements[1].text_content()
                return review_title, review_desc
        else:
                raise Exception("Error collecting review elements: Couldn't find separate title and description alements.")

def get_review_polarity(review_desc):
        polarity = TextBlob(review_desc).sentiment.polarity
        if polarity > 0:
                return "Positive"
        elif polarity == 0:
                return "Neutral"
        else:
                return "Negative"

def save_results(movies, basedir):
        results_path = os.path.join(basedir, "results")
        for movie in movies:
                out_path = os.path.join(results_path, f'{movie}.txt')
                with open(out_path, 'w', encoding='utf-8') as file:
                        for review in movies[movie]:
                                title = insert_newlines(review['title'])
                                pol = f"[{review['polarity']} review]"
                                desc = insert_newlines(review['desc'])
                                content = f"{title}\n\n{pol}\n\n{desc}\n{'-'*64}\n\n"
                                file.write(content)

if __name__ == '__main__':
        main()