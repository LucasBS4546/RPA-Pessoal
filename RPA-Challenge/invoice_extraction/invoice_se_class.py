from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import cv2
import pandas
import os
import urllib.request
import easyocr
from datetime import datetime
from time import sleep

class Invoice():
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.data = {
            'ID': [],
            'DueDate': [],
            'InvoiceNo': [],
            'InvoiceDate': [],
            'CompanyName': [],
            'TotalDue': []
        }
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.date_format = "%d-%m-%Y"
        
    def run(self):
        self.prepare_page()

        self.main_loop()

        self.submit_results()
        
    def prepare_page(self):
        self.browser.get('https://rpachallengeocr.azurewebsites.net/')
        self.browser.maximize_window()
        self.browser.find_element(By.XPATH, '//button[text()="START"]').click()
        sleep(0.3)

    def main_loop(self):
        while(True):
            rows, next_btn = self.get_page_elements()

            self.iterate_rows(rows)

            if "disabled" in next_btn.get_attribute("class"):
                break

            next_btn.click()

    def iterate_rows(self, rows):
        for row in rows:
            tds = row.find_elements(By.XPATH, ".//*")

            id = tds[1].text
            due_date_str = tds[2].text

            if self.is_today_or_earlier(due_date_str):
                text = self.read_invoice_img(btn=tds[3])

                is_invoice_of_type_1 = 'INVOICE' in text[0].upper()
                if is_invoice_of_type_1:
                    self.fill_data_1(text, id, due_date_str)
                else:
                    self.fill_data_2(text, id, due_date_str)
            
                self.reset_browser_state()
                
    def get_page_elements(self):
        rows = self.browser.find_elements(By.XPATH, '//table[@id="tableSandbox"]/tbody/child::tr')
        next_btn = self.browser.find_element(By.XPATH, '//a[text()="Next"]')
        return rows, next_btn
    
    def is_today_or_earlier(self, date_str):
        due_date = datetime.strptime(date_str, self.date_format)
        today = datetime.today()
        return today >= due_date
    
    def read_invoice_img(self, btn):
        btn.click()
        self.wait.until(EC.number_of_windows_to_be(2))

        new_page = self.browser.window_handles[1]
        self.browser.switch_to.window(new_page)

        img_uri = self.browser.current_url
        urllib.request.urlretrieve(img_uri, os.path.join(f"{os.getcwd()}", "temp_img" + ".jpg"))
        img = cv2.imread("temp_img.jpg")

        return self.reader.readtext(img, detail=0)

    def fill_data_1(self, text, id, due_date):
        date_obj = datetime.strptime(text[4], '%Y-%m-%d')
        uv_date = date_obj.strftime(self.date_format)

        self.data["ID"].append(id)
        self.data["DueDate"].append(due_date)
        self.data["InvoiceNo"].append(text[1])
        self.data["InvoiceDate"].append(uv_date)
        self.data["CompanyName"].append(text[5])
        self.data["TotalDue"].append(text[-2])

    def fill_data_2(self, text, id, due_date):
        date_obj = datetime.strptime(text[3], '%Y-%m-%d')
        uv_date = date_obj.strftime(self.date_format)

        self.data["ID"].append(id)
        self.data["DueDate"].append(due_date)
        self.data["InvoiceNo"].append(text[5][9:])
        self.data["InvoiceDate"].append(uv_date)
        self.data["CompanyName"].append(text[0])
        self.data["TotalDue"].append(text[-5])

    def reset_browser_state(self):
        self.browser.close()
        og_page = self.browser.window_handles[0]
        self.browser.switch_to.window(og_page)

    def submit_results(self):
        df = pandas.DataFrame(self.data)
        df.to_csv('results.csv', index=False)

        submit_input = self.browser.find_element(By.XPATH, '//input[@name="csv"]')
        submit_input.send_keys(os.path.join(f"{os.getcwd()}", "results.csv"))

        sleep(5)
        os.remove("temp_img.jpg")
        os.remove("results.csv")



def main():
    rpa_challenge = Invoice()
    rpa_challenge.run()    


if __name__ == "__main__":
    main()