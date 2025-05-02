from selenium import webdriver
import pandas
from time import sleep

class Challenge:
    def __init__(self, input_file):
        self.df = pandas.read_excel(input_file)
        self.df.columns = self.df.columns.str.strip()
        self.browser = webdriver.Chrome()
        
    def do_challenge(self):
        self.browser.get('https://rpachallenge.com')
        self.browser.find_element('xpath', '//button[text()="Start"]').click()
        self.input_loop()

    def input_loop(self):
        for row in range(0, len(self.df.index)):
            self.select_input_elements()
            self.fill_input_elements(row)
            self.submit_btn.click()

    def select_input_elements(self):
        self.input_divs = self.browser.find_elements('xpath', '//label/parent::div')
        self.submit_btn = self.browser.find_element('xpath', '//input[@type="submit"]')

    def fill_input_elements(self, row):
        for div in self.input_divs:
            label = div.find_element('tag name', 'label').text.strip()
            input = div.find_element('tag name', 'input')
            input.send_keys(str(self.df[label][row]))



if __name__ == "__main__":
    rpac = Challenge("challenge.xlsx")

    rpac.do_challenge()

    sleep(2)