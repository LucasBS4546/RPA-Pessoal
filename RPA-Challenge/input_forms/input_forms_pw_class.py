from playwright.sync_api import sync_playwright
import pandas
from time import sleep

class Challenge:
    def __init__(self, p, input_file):
        self.df = pandas.read_excel(input_file)
        self.df.columns = self.df.columns.str.strip()
        self.browser = p.chromium.launch(headless=False)
        self.main_page = self.browser.new_page()
        
    def do_challenge(self):
        self.main_page.goto('https://rpachallenge.com')
        self.main_page.locator('//button[text()="Start"]').click()
        self.input_loop()

    def input_loop(self):
        for row in range(0, len(self.df.index)):
            self.select_input_elements()
            self.fill_input_elements(row)
            self.submit_btn.click()

    def select_input_elements(self):
        self.input_divs = self.main_page.locator('//label/parent::div').all()
        self.submit_btn = self.main_page.locator('//input[@type="submit"]')

    def fill_input_elements(self, row):
        for div in self.input_divs:
            label = div.locator("label").text_content().strip()
            input = div.locator("input")
            input.fill(str(self.df[label][row]))

    def end_challenge(self):
        self.browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        rpac = Challenge(p, "challenge.xlsx")
        
        rpac.do_challenge()

        sleep(2)

        rpac.end_challenge()