import undetected_chromedriver as uc
import time
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#GOOGLE SHEETS IMPORTS
import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class Product:
    def __init__(self):
        self.product_name = None
        self.package_id = None
        self.available = None
        self.inventory_date = None
        self.unit_price = None
        self.batch = None
        self.thc = None
        self.room = None
        self.rowId = None

    def __repr__(self):
        return f"Product # {self.rowId} ({self.product_name}, {self.package_id}, {self.available}, {self.inventory_date}, {self.unit_price}, {self.batch}, {self.thc})"

# SETUP: Enter your username and password for the Dutchie Backoffice
username = "victorv1798"
passW = "BIGSMOKE98"
spreadSheetID = "1szv26MB-HIGeezQ_N1s9K7Cglww3VYC-QUe9GEwrO-8"


# The following code is used to suppress the ResourceWarning that is thrown by the undetected_chromedriver package
warnings.filterwarnings("ignore", category=ResourceWarning)

# The following code is used to create a headless browser using the undetected_chromedriver package
chromeOptions = uc.ChromeOptions()
# chromeOptions.headless = True
driver = uc.Chrome(use_subprocess=True, options=chromeOptions)

all_products = []
seen_rows = set()

# The following code is used to login to the Dutchie Backoffice
try:
    driver.get("https://cove.backoffice.dutchie.com/home")
    time.sleep(10)

    # The following code is used to enter the username and password into the login form
    userName = driver.find_element(By.ID, "input-input_login-email")
    userName.send_keys(username)
    time.sleep(5)

    # The following code is used to enter the password into the login form
    password = driver.find_element(By.ID, "input-input_login-password")
    password.send_keys(passW)

    # The following code is used to click the login button
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='auth_button_go-green']"))
    )
    login_button.click()
    time.sleep(5)

    try:
        # The following code checks if the page is ready by looking for the main navigation menu
        presElement = EC.presence_of_element_located((By.ID, 'main-navigation-menu'))
        WebDriverWait(driver, 10).until(presElement)
        print("Page is ready!")

        driver.get("https://cove.backoffice.dutchie.com/products/inventory?categories=Everyday+14g+Pre-Packed+Flower%2CEveryday+14g+Pre-Packed+Shake+Flower%2CEveryday+28g+Pre-Packed+Flower%2CEveryday+3.5g+Pre-Packed+%28Promo%29+Flower%2CEveryday+3.5g+Pre-Packed+Flower%2CEveryday+7g+Shake+Pre-Packed+Flower%2CLoud+Pax+14g+Pre-Packed+Flower%2CLoud+Pax+28g+Pre-Packed+Flower%2CLoud+Pax+3.5g+Pre-Packed+Flower%2CLoud+Pax+3.5g+Flower+%28MED%29%2CLiquid+Gold+Concentrates%2CLiquid+Gold+CR+Concentrates%2CLiquid+Gold+Infused+Pre-Rolls%2CLiquid+Gold+Kief+Concentrates%2CLiquid+Gold+Kief+Hash+Concentrates%2CLiquid+Gold+Live+Disposable+1g%2CLiquid+Gold+Loaded+1g+Pre-Rolls%2CLiquid+Gold+NANO+Infused+Pre-Rolls%2CCookies+3.5g+Vendor+Pre-Packed+Flower%2CCookies+7g+Vendor+Pre-Packed+Flower%2CCookies+Bulk+Concentrates%2CCookies+1g+LR+Concentrates%2CCookies+1g+Concentrates%2CMAC+Pharms+3.5g+Vendor+Pre-Packed+Flower&sortFields=product.whseProductsDescription&sortDirections=asc&pageSize=1000")
        time.sleep(5)

        scroll_container = driver.find_element(By.CSS_SELECTOR, "div.MuiDataGrid-virtualScroller")

        def scroll_table(element, scroll_pause_time=1):
            last_scroll_position = driver.execute_script("return arguments[0].scrollTop", element)
            driver.execute_script("arguments[0].scrollTop += arguments[0].offsetHeight", element)
            time.sleep(scroll_pause_time)
            new_scroll_position = driver.execute_script("return arguments[0].scrollTop", element)
            print(f"Scrolled from {last_scroll_position} to {new_scroll_position}")
            return new_scroll_position > last_scroll_position

        print("Attempting to scan rows...")

        def fetch_and_process_rows():
            rows = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")  # Find all rows in the table
            processed_products = []
            
            for row in rows[1:]:  # Skip the first row as it is the header
                row_id = row.get_attribute("data-rowindex")
                print(f"Processing row_id: {row_id}")
                if row_id in seen_rows:
                    print(f"Row {row_id} already processed, skipping.")
                    continue

                seen_rows.add(row_id)
                print("Scanning row " + str(rows.index(row)) + "...")
                product = Product()
                try:
                    product.rowId = row_id
                except:
                    product.rowId = "N/A"
                try:
                    product.product_name = row.find_element(By.CSS_SELECTOR, "div[data-colindex='1'] .MuiDataGrid-cellContent").text
                except:
                    product.product_name = "N/A"
                try:
                    product.package_id = row.find_element(By.CSS_SELECTOR, "div[data-colindex='2'] .MuiDataGrid-cellContent").text
                except:
                    product.package_id = "N/A"
                try:
                    product.available = row.find_element(By.CSS_SELECTOR, "div[data-colindex='3'] .MuiDataGrid-cellContent").text
                except:
                    product.available = "N/A"
                try:
                    product.inventory_date = row.find_element(By.CSS_SELECTOR, "div[data-colindex='4'] .MuiDataGrid-cellContent").text
                except:
                    product.inventory_date = "N/A"
                try:
                    product.unit_price = row.find_element(By.CSS_SELECTOR, "div[data-colindex='5'] .MuiDataGrid-cellContent").text
                except:
                    product.unit_price = "N/A"
                try:
                    product.batch = row.find_element(By.CSS_SELECTOR, "div[data-colindex='6'] .MuiDataGrid-cellContent").text
                except:
                    product.batch = "N/A"
                try:
                    product.thc = row.find_element(By.CSS_SELECTOR, "div[data-colindex='7'] .MuiDataGrid-cellContent").text
                except:
                    product.thc = "N/A"
                try:
                    product.room = row.find_element(By.CSS_SELECTOR, "div[data-colindex='8'] .MuiDataGrid-cellContent").text
                except:
                    product.room = "N/A"

                processed_products.append(product)

            return processed_products

        all_products.extend(fetch_and_process_rows())

        while True:
            previous_count = len(all_products)
            if not scroll_table(scroll_container):
                print("Reached the end of the table, no more scrolling needed.")
                break
            new_products = fetch_and_process_rows()
            all_products.extend(new_products)

            if len(all_products) == previous_count:
                print("No new rows were loaded after scrolling.")
                break
    except Exception as e:
        print(f"Exception: {e}")
finally:
    try:
        time.sleep(2)  # Add a small delay before quitting
        driver.close()
        driver.quit()
        print("Driver quit successfully.")

        for product in all_products:
            print(product)
    except Exception as e:
        print(f"Exception during driver quit: {e}")




SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = spreadSheetID
RANGE_NAME = 'Sheet1!A2'
SERVICE_ACCOUNT_FILE = 'service_account.json'

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Prepare the data in the format required by the API

def writeToGoogleSheets(data):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = spreadSheetID
    RANGE_NAME = 'Sheet1!A1'
    SERVICE_ACCOUNT_FILE = 'service_account.json'

    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Prepare the data in the format required by the API
    values = [[product.rowId, product.product_name, product.package_id, product.available, product.inventory_date, product.unit_price, product.batch, product.thc, product.room] for product in data]

    body = {
        'values': values
    }

    # Use the Sheets API to update the sheet
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()

    print(f"{result.get('updatedCells')} cells updated.")

writeToGoogleSheets(all_products)
