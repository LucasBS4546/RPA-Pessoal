from playwright.sync_api import sync_playwright
import cv2
import pandas
import os
import urllib.request
import easyocr
from datetime import datetime
from time import sleep

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://rpachallengeocr.azurewebsites.net/')

        data = {
                'ID': [],
                'DueDate': [],
                'InvoiceNo': [],
                'InvoiceDate': [],
                'CompanyName': [],
                'TotalDue': []
            }

        page.locator('xpath=//button[text()="START"]').click()
        sleep(0.5)
        reader = easyocr.Reader(['en'], gpu=False)
        try:
            while(True):
                rows = page.locator('xpath=//table[@id="tableSandbox"]/tbody/child::tr').all()
                next_btn = page.locator('xpath=//a[text()="Next"]')

                for row in rows:
                    tds = row.locator("xpath=.//*", ).all()

                    id = tds[1].text_content()
                    due_date_str = tds[2].text_content()
                    date_format = "%d-%m-%Y"

                    due_date = datetime.strptime(due_date_str, date_format)
                    today = datetime.today()

                    if today >= due_date:  
                        with context.expect_page() as new_page_info:
                            tds[3].click()
                        new_page = new_page_info.value

                        img_uri = new_page.url
                        urllib.request.urlretrieve(img_uri, os.path.join(f"{os.getcwd()}", "temp_img" + ".jpg"))
                        img = cv2.imread("temp_img.jpg")

                        data["ID"].append(id)
                        data["DueDate"].append(due_date_str)

                        text = reader.readtext(img, detail=0)

                        if 'INVOICE' in text[0].upper():
                            data["InvoiceNo"].append(text[1])
                            date_obj = datetime.strptime(text[4], '%Y-%m-%d')
                            uv_date = date_obj.strftime(date_format)
                            data["InvoiceDate"].append(uv_date)
                            data["CompanyName"].append(text[5])
                            data["TotalDue"].append(text[-2])
                        else:
                            data["InvoiceNo"].append(text[5][9:])
                            date_obj = datetime.strptime(text[3], '%Y-%m-%d')
                            uv_date = date_obj.strftime(date_format)
                            data["InvoiceDate"].append(uv_date)
                            data["CompanyName"].append(text[0])
                            data["TotalDue"].append(text[-5])
                        

                        new_page.close()

                if "disabled" in next_btn.get_attribute("class"):
                    break

                next_btn.click()
        except:
            print("Algo deu errado")
        
        df = pandas.DataFrame(data)
        df.to_csv('results.csv', index=False)

        submit_input = page.locator('xpath=//input[@name="csv"]')
        submit_input.set_input_files(os.path.join(f"{os.getcwd()}", "results.csv"))
    sleep(5)
    os.remove("temp_img.jpg")
    os.remove("results.csv")


if __name__ == "__main__":
    main()