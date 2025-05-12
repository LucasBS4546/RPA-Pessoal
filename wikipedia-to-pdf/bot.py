from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from time import sleep
import os

class WikiToMdBot:
    def __init__(self, urls: list):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.resultsdir = os.path.join(self.basedir, 'results')
        self.urls = urls

        self.__setup_pw()

    def __setup_pw(self):
        p = sync_playwright().start()
        self.browser: Browser = p.chromium.launch(headless=False)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page = self.context.new_page()

    def run(self):
        for url in urls:
            self.__prepare_page(url)
            self.__download_pdf(url)

    def __prepare_page(self, url: str):
        self.page.goto(url)

        main = self.page.locator('#content')

        toolbar = main.locator('.vector-page-toolbar').first
        appearance = main.locator('.vector-column-end').first
        toolbar.evaluate('el => el.remove()')
        appearance.evaluate('el => el.remove()')

        main.evaluate('el => {' \
            'const main = el;' \
            'document.body.innerHTML = "";' \
            'document.body.appendChild(main.cloneNode(true))' \
          '}'
        )

    def __download_pdf(self, url: str):
        fname = f'{url.rsplit("/").pop()}.pdf'
        path = os.path.join(self.resultsdir, fname)

        self.page.pdf(path=path)


if __name__ == '__main__':
    urls = [
        'https://en.wikipedia.org/wiki/Anomalocaris',
        'https://en.wikipedia.org/wiki/Peytoia',
        'https://en.wikipedia.org/wiki/Hurdia'
    ]
    bot = WikiToMdBot(urls)

    bot.run()
