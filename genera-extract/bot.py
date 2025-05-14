from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Locator
from time import sleep
import pandas
import os

class GenusExcelBot:
    def __init__(self, outpath: str, urls: dict):
        self.outpath: str  = outpath
        self.urls: dict    = urls
        self.data: dict    = {}

        self.__startup_data()
        self.__setup_pw()

    def __startup_data(self):
        for key in self.urls:
            self.data[key] = self.__create_dict()


    def __get_columns(self):
        return ["Reino", "Filo", "Classe", "Ordem", "Subordem", "Família", "Subfamília", "Gênero"]

    def __create_dict(self):
        return {col: [] for col in self.__get_columns()}
    
    def __setup_pw(self):
        p = sync_playwright().start()
        self.browser: Browser        = p.chromium.launch(headless=False)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page              = self.context.new_page()

    def run(self):
        for key in self.data:
            self.__open_page(url=self.urls[key])
            self.__run_extract_loop(datakey=key)
        self.__save_excel()

    def __open_page(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state()
    
    def __run_extract_loop(self, datakey: str):
        while True:
            main = self.page.locator('#mw-pages')
            atags_text: list = main.locator('xpath=./a').all_text_contents()
            is_last_page: bool = 'página seguinte' not in atags_text

            for genus in main.locator('li').all():
                print(genus.text_content(), '\n')
                self.__save_genus_data(genus, datakey)

            if is_last_page:
                break
            else:
                main.locator('xpath=./a[text()="página seguinte"]').first.click()
                continue

    def __save_genus_data(self, genus: Locator, datakey: str):
        with self.context.expect_page() as new_page_info:
            genus.locator('a').click(modifiers=['Control'])
        genus_page = new_page_info.value
        genus_page.wait_for_load_state()

        content_table = genus_page.locator('xpath=//a[@title="Classificação científica"]/../../following-sibling::tr[1]/td/table[1]/tbody')
        
        trs = content_table.locator('tr').all()
        temp_data = {col: "-" for col in self.__get_columns()}
        is_valid_tr = False
        for tr in trs:
            key = tr.locator('xpath=./td[1]')
            value = tr.locator('xpath=./td[2]')

            key = self.__format_key(key.text_content())
            value = self.__format_value(value.text_content(), key)

            temp_data[key] = value
            is_valid_tr = True

        if is_valid_tr:
            for key in self.__get_columns():
                self.data[datakey][key].append(temp_data[key])

        genus_page.close()
    
    def __format_key(self, key: str):
        key = key.strip()[:-1]
        if key.lower() == 'género':
            key = "Gênero"
        return key

    def __format_value(self, value: str, key: str):
        value = value.strip()
        if key == 'Gênero':
            return self.__format_genus_name(value)
        return value
    
    def __format_genus_name(self, s: str):
        for i, c in enumerate(s):
            if i+1 == len(s):
                break
            if c.islower() and s[i+1].isupper():
                return s[:i+1]
        return s
                

    def __save_excel(self, index: bool=False):
        with pandas.ExcelWriter(self.outpath, engine='xlsxwriter') as writer:
            for datakey in self.data:
                df = pandas.DataFrame(self.data[datakey])
                df.to_excel(writer, index=index, sheet_name=datakey)



if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))
    outpath = os.path.join(basedir, 'output.xlsx')
    urls = {
        'amphibian genera':'https://pt.wikipedia.org/wiki/Categoria:G%C3%AAneros_de_anf%C3%ADbios',
        'reptilian genera':'https://pt.wikipedia.org/wiki/Categoria:G%C3%AAneros_de_r%C3%A9pteis'
    }
    bot =  GenusExcelBot(outpath=outpath, urls=urls)

    bot.run()