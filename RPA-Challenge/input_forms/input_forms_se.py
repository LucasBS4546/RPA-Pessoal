from selenium import webdriver
import pandas
from time import sleep

navegador = webdriver.Chrome()

navegador.get('https://rpachallenge.com')

navegador.find_element('xpath', '//button[text()="Start"]').click()

df = pandas.read_excel('challenge.xlsx')
df.columns = df.columns.str.strip()

for row in range(0, len(df.index)):
    input_divs = navegador.find_elements('xpath', '//label/parent::div')
    submit_btn = navegador.find_element('xpath', '//input[@type="submit"]')

    for div in input_divs:
        label = div.find_element('tag name', 'label').text.strip()
        input = div.find_element('tag name', 'input')
        input.send_keys(str(df[label][row]))

    submit_btn.click()

sleep(2)