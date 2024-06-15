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
chromeOptions.headless = True
driver = uc.Chrome(use_subprocess=True, options=chromeOptions)

all_products = []
seen_rows = set()

# The following function is used to login to the Dutchie Backoffice
def login():
        driver.get("https://cove.backoffice.dutchie.com/products/inventory?pageSize=1000&categories=Everyday+3.5g+%28Promo%29+Flower%2CEveryday+3.5g+Flower%2CEveryday+14g+Flower%2CEveryday+14g+Shake+Flower%2CEveryday+28g+Flower%2CLoud+Pax+3.5g+Flower%2CLoud+Pax+3.5g+Flower+%28MED%29%2CLoud+Pax+14g+Flower%2CLoud+Pax+28g+Flower%2CCookies+3.5g+Flower%2CCookies+7g+Flower%2CLiquid+Gold+1g+Shatter+Concentrates%2CLiquid+Gold+Concentrates%2CLiquid+Gold+LR+Concentrate&sortFields=product.whseProductsDescription&sortDirections=asc")
        time.sleep(5)

        # The following code is used to enter the username and password into the login form
        userName = driver.find_element(By.ID, "input-input_login-email")
        userName.send_keys(username)
        time.sleep(2)

        # The following code is used to enter the password into the login form
        password = driver.find_element(By.ID, "input-input_login-password")
        password.send_keys(passW)

        # The following code is used to click the login button
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='auth_button_go-green']"))
        )
        login_button.click()
        time.sleep(5)


# The following function is used to fetch the inventory data from the Dutchie Backoffice
def fetch_Inventories():
    all_products = []
    seen_rows = set()
                
    try:

        print("Page is ready!")
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
        
    return all_products



def mapProducts(products):
    categorized_products = {}
    for product in products:
        substring = product.product_name.split("-")[0].strip()
        substringCopy = substring
        if "Liquid Gold" in substring:
            substring = "Liquid Gold Concentrates"
            if "Shatter" in substringCopy:
                substring = "Liquid Gold Shatter"
        
        if substring not in categorized_products:
            categorized_products[substring] = []
        categorized_products[substring].append(product)
    return categorized_products



SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = spreadSheetID

SERVICE_ACCOUNT_FILE = 'service_account.json'

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Prepare the data in the format required by the API

def writeToGoogleSheets(categoriezed_products):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = spreadSheetID
    SERVICE_ACCOUNT_FILE = 'service_account.json'

    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Prepare the data in the format required by the API
    for category, products in categoriezed_products.items():
        RANGE_NAME = f"'{category}'!A2"
        values = [[product.rowId, product.product_name, product.package_id, product.available, product.inventory_date, product.unit_price, product.batch, product.thc, product.room] for product in products]

        body = {
        'values': values
        }

    # Use the Sheets API to update the sheet
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='RAW', body=body).execute()
        

        time_range = f"'{category}'!K2"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        time_body = {
            'values': [[current_time]]
        }

        time_result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=time_range,
            valueInputOption='RAW', body=time_body).execute()

        print(f"{result.get('updatedCells')} cells updated.")




# The user's credentials are used to login to the Dutchie Backoffice
login()

# The fetch_Inventories is repeatedly called to fetch the inventory data from the Dutchie Backoffice (in 30 second intervals) until the program is terminated
while True:
    products = fetch_Inventories()
    print("Data fetched from Dutchie Backoffice @ " + str(time.ctime() + "..."))
    categorized_products = mapProducts(products)
    print("Printing products categories...")
    for category in categorized_products:
        print(category)
    writeToGoogleSheets(categorized_products)
    print("Data written to Google Sheets @ " + str(time.ctime()))
    print("Sleeping for 30 seconds...")
    time.sleep(30)
    driver.refresh()
    time.sleep(5)
    
