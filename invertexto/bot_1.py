from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pandas
from time import sleep


class Bot_1:
    def __init__(self, file_path):
        self.movies = pandas.read_csv(file_path)
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.uri = "No URI"

    def get_uri(self):
        return self.uri

    def run(self):
        self._prepare()        
        self._fill_textarea()
        return self.uri

    def _prepare(self):
        self._prepare_browser()
        self._prepare_page()
        self._prepare_dict()

    def _prepare_browser(self):
        self.browser.get('https://www.invertexto.com/notepad')
        self.browser.maximize_window()

    def _prepare_page(self):
        input_div = self.browser.find_element(By.CLASS_NAME, 'input-group').find_elements(By.XPATH, ".//*")
        self.uri = input_div[0].text + input_div[1].get_attribute("value")
        self.uri = f'https://{self.uri}'
        input_div[2].click()
        sleep(0.5)

    def _prepare_dict(self):
        self.movies = self.movies.to_dict(orient='records')

    def _fill_textarea(self):
        textarea = self.browser.find_element(By.TAG_NAME, "textarea")
        for movie in self.movies:
            duration = int(movie['Duration'] / 60)
            dur_str = f'{duration}h {movie["Duration"] - 60 * duration}m'
            
            str = f'Filme {movie["Id"]}: {movie["Name"]}\n' + \
                    f'    - Avaliação: {movie["Rating"]}\n' + \
                    f'    - Duração: {dur_str}\n' + \
                    f'    - Diretor: {movie["Director"]}\n\n'
            
            textarea.send_keys(str)