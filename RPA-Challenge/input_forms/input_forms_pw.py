from playwright.sync_api import sync_playwright
import pandas
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto('https://rpachallenge.com')

    page.locator('//button[text()="Start"]').click()

    df = pandas.read_excel('challenge.xlsx')
    df.columns = df.columns.str.strip()

    for row in range(0, len(df.index)):
        input_divs = page.locator('//label/parent::div').all()
        submit_btn = page.locator('//input[@type="submit"]')

        for div in input_divs:
            label = div.locator("label").text_content().strip()
            input = div.locator("input")
            input.fill(str(df[label][row]))

        submit_btn.click()

    sleep(2)

    browser.close()