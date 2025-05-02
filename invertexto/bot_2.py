from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pandas
from datetime import datetime

class Bot_2:
    def __init__(self, uri, path):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.uri = uri
        self.path = path
        self.data = {
            'Id': [],
            'Name': [],
            'Rating': [],
            'Duration': [],
            'Director': []
        }

    def run(self):
        self._prepare_browser()        
        self._read_textarea()
        self._save_csv()

    def _prepare_browser(self):
        self.browser.get(self.uri)
        self.browser.maximize_window()

    def _read_textarea(self):
        textarea = self.browser.find_element(By.TAG_NAME, "textarea").get_attribute("value")
        movies = textarea.split("\n\n")
        for movie in movies:
            lines = movie.split("\n")

            f_line = lines[0].split(":", maxsplit=1)
            if len(f_line) == 2:
                dur_str = lines[2][15:].split(" ")
                hours = int(dur_str[0][:-1])
                min = int(dur_str[1][:-1])
                duration = hours * 60 + min

                self.data["Id"].append(f_line[0][6:])
                self.data["Name"].append(f_line[1][1:])
                self.data["Rating"].append(lines[1][17:])
                self.data["Duration"].append(duration)
                self.data["Director"].append(lines[3][15:])
            
    
    def _save_csv(self):
        df = pandas.DataFrame(self.data)
        df.to_csv(self.path, index=False)
        with open(self.path, 'a') as file:
            file.write(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                

