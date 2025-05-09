from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from tenacity import retry, stop_after_attempt
from pathlib import Path
from time import sleep
import os

class FrogBot:
    def __init__(self, inpath: str, outpath: str):
        self.inpath = inpath
        self.outpath = outpath

        self.__setup_pw()

    def __setup_pw(self):
        p = sync_playwright().start()
        self.browser: Browser = p.chromium.launch(headless=False)
        self.context: BrowserContext = self.browser.new_context()

    @retry(stop=stop_after_attempt(3))
    def open_page(self):
        self.page = self.context.new_page()
        self.page.goto('https://pt.wikipedia.org/wiki/Categoria:G%C3%AAneros_de_anf%C3%ADbios')

    def run(self):
        self.__get_page_elements()
        self.cur_frog = self.__get_current_frog()

        try:
            self.__get_to_frog_element()
        except Exception as e:
            print(f"Error: Informed frog could not be found\n\n{e}")
            return

        self.__get_frog_data()


    def __get_page_elements(self):
        self.main_div = self.page.locator('xpath=//*[@id="mw-pages"]')
        self.frogs = self.main_div.locator('xpath=./div/div')

    def __get_current_frog(self):
        if os.path.isfile(self.inpath):
            first_frog = self.__read_file()
        else:
            first_frog = self.__first_frog()

        return first_frog

    def __read_file(self):
        with open(self.inpath, 'r', encoding='utf-8') as file:
            return file.read().strip()

    def __first_frog(self):
        return self.frogs.locator('.//li').first.text_content()

    def __get_to_frog_element(self):
        last_frog = self.frogs.locator('.//li').last.text_content()
        page_btn = self.main_div.locator('./a').last

        while self.cur_frog > last_frog:
            if page_btn.text_content() == 'página seguinte':
                page_btn.click()
                self.__get_current_frog()
            else:
                raise Exception("Frog not found")

    def __get_frog_data(self):
            self.__open_frog_page()

    def __open_frog_page(self):
        btn = self.frogs.locator(f'.//li[text()="{self.cur_frog}"]')

        with self.context.expect_page() as new_page_info:
            btn.click()
        self.page = new_page_info.value


if __name__ == "__name__":
    outpath = os.path.join(Path(__file__), 'results')
    inpath = os.path.join(Path(__file__), 'input.txt')
    bot = FrogBot(inpath=inpath, outpath=outpath)

    bot.run()