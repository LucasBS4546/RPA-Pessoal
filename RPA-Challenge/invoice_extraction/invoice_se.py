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

def main():

    navegador = webdriver.Chrome()
    navegador.get('https://rpachallengeocr.azurewebsites.net/')
    navegador.maximize_window()

    wait = WebDriverWait(navegador, 10)
    data = {
            'ID': [],
            'DueDate': [],
            'InvoiceNo': [],
            'InvoiceDate': [],
            'CompanyName': [],
            'TotalDue': []
        }
    
    navegador.find_element(By.XPATH, '//button[text()="START"]').click()
    sleep(0.3)

    reader = easyocr.Reader(['en'], gpu=False)

    while(True):
        try:
            rows = navegador.find_elements(By.XPATH, '//table[@id="tableSandbox"]/tbody/child::tr')
            next_btn = navegador.find_element(By.XPATH, '//a[text()="Next"]')
            
            for row in rows:
                tds = row.find_elements(By.XPATH, ".//*")

                id = tds[1].text
                due_date_str = tds[2].text
                date_format = "%d-%m-%Y"

                due_date = datetime.strptime(due_date_str, date_format)
                today = datetime.today()

                if today >= due_date:                        
                    tds[3].click()
                    wait.until(EC.number_of_windows_to_be(2))
                    
                    navegador.switch_to.window(navegador.window_handles[1])

                    img_uri = navegador.current_url
                    urllib.request.urlretrieve(img_uri, os.path.join(f"{os.getcwd()}", "temp_img" + ".jpg"))
                    img = cv2.imread("temp_img.jpg")

                    text = reader.readtext(img, detail=0)

                    data["ID"].append(id)
                    data["DueDate"].append(due_date_str)

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
                
                    
                    navegador.close()
                    navegador.switch_to.window(navegador.window_handles[0])

            if "disabled" in next_btn.get_attribute("class"):
                break

            next_btn.click()
        except:
            print("Algo deu errado")
    
    df = pandas.DataFrame(data)
    df.to_csv('results.csv', index=False)

    submit_input = navegador.find_element(By.XPATH, '//input[@name="csv"]')
    submit_input.send_keys(os.path.join(f"{os.getcwd()}", "results.csv"))
    sleep(5)
    os.remove("temp_img.jpg")
    os.remove("results.csv")


if __name__ == "__main__":
    main()