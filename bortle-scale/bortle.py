from playwright.sync_api import sync_playwright
import pandas
import os
from time import sleep
from datetime import datetime
import glob

def main():
    places = []
    data = []

    read_input_file(places)

    get_data(data, places)

    save_output_file(data)

def read_input_file(places):
    with open('places.txt', 'r') as file:
        for line in file:
            contents = line.split("/")
            coords = contents[0].strip().split(",")
            place_info = contents[1].strip().rsplit(" ", maxsplit=1)

            lat, lon = coords[0].strip(), coords[1].strip()        
            place = place_info[0]

            places.append({
                'lat': float(lat),
                'lon': float(lon),
                'name': place
            })

def get_data(data, places):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://www.lightpollutionmap.info/')

        for place in places:
            searchBox = page.locator('xpath=.//input[@id="searchBox"]')

            coordenates = f'{place["lat"]}, {place["lon"]}'
            searchBox.fill(coordenates)
            page.keyboard.press("Enter")

            sleep(2)

            popup = page.locator('xpath=.//*[@id="ol-popup-content"]')
            rows = popup.locator('xpath=.//*[@class="tableRow"]').all()

            data_item = {
                'nome': place['name']
            }
            for row in rows:
                cell = row.locator('xpath=.//*[@class="tableCell"]').text_content()
                cellValue = row.locator('xpath=.//*[@class="tableCellValues"]').text_content()

                data_item[cell.strip()] = cellValue.strip()

            data.append(data_item)

def save_output_file(data):
    basedir = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join(basedir, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    old_results = glob.glob(os.path.join(basedir, "output_") + "*.csv")
    for old_result in old_results:
        try:
            os.remove(old_result)
        except FileNotFoundError:
            print(f"File not found: {old_result}")
        except Exception as e:
             print(f"Error deleting {old_result}: {e}")

    df = pandas.DataFrame(data)
    df.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()