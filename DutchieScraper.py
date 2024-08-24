# Description: This program is used to fetch the inventory data from the Dutchie Backoffice and write it to a Google Sheet
# This program is currently configured to fetch very specific data (such as the product name, package ID, available quantity, inventory date, unit price, batch, THC percentage, and room) from the Dutchie Backoffice
# In order to change the data that is fetched, you will need to modify the code in the fetch_Inventories function and ensure that your account has those values present in the Dutchie Backoffice inventory table in the proper order
# Author: Brian Venegas 

# The following imports are used to create a headless browser using the undetected_chromedriver package
import undetected_chromedriver as uc
import time
import warnings
import sys
from dotenv import load_dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

# The following imports are used to interact with the Google Sheets API
import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# The following class is used to store the data of each product that is fetched from the Dutchie Backoffice
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


# SETUP: The following variables are used to store the user's credentials, the ID of the Google Sheet, and the name of the Service Account JSON file
# Please enter your own values for the following variables: The program will not work if you do not enter your own values.
# The username and password are used to login to the Dutchie Backoffice]
# The spreadSheetID is the ID of the Google Sheet that you want to write the data to


def load_environment_variables():
    if hasattr(sys, '_MEIPASS'):
        # If running as a bundled executable, the .env file will be in the same directory
        dotenv_path = os.path.join(sys._MEIPASS, '.env')
    else:
        # Otherwise, it will be in the current directory
        dotenv_path = '.env'

    load_dotenv(dotenv_path)

def get_token_file():
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, 'token.json')
    return 'token.json'

def get_service_account_file():
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, 'service_account.json')
    return 'service_account.json'


load_environment_variables()

username = os.getenv("DUTCHIE_USERNAME")
passW = os.getenv("DUTCHIE_PASSWORD")
spreadSheetID = os.getenv("SPREADSHEET_ID")
ServiceAccountJSON = get_service_account_file()
FilterList = os.getenv("FILTER_LIST")
BULK_FLOWER_LINK = os.getenv("BULK_FLOWER_LINK")




# The following code is used to suppress the ResourceWarning that is thrown by the undetected_chromedriver package
warnings.filterwarnings("ignore", category=ResourceWarning)

# The following code is used to create a headless browser using the undetected_chromedriver package
# For debugging purposes, you can set headless to False to see the browser in action
chromeOptions = uc.ChromeOptions()
chromeOptions.headless = True
driver = uc.Chrome(use_subprocess=True, options=chromeOptions)

# The following code is used to create an empty list to store all the products that are fetched from the Dutchie Backoffice
# The seen_rows set is used to keep track of the rows that have already been processed
all_products = []
seen_rows = set()



def print_header():
        print("""


            ██████                                                                                            
        █     ███████                                                                         ██              
   ██████████   ███████                  ███                ███                 ███          ████             
  ██████████      ██████                 ███                ███                 ███                           
 ███████           ██████         ██████ ███ ███      ███ ████████   ████████   ███ ██████   ███    ███████   
██████     █████   ██████       ████   █████ ███      ███   ███     ████  ████  █████   ████ ███  ████    ███ 
█████    ████████   █████      ███       ███ ███      ███   ███    ███      ███ ███      ███ ███  ███      ███
████     ████████   ████       ███       ███ ███      ███   ███    ███          ███      ███ ███  ████████████
████       █████   ████        ███      ████ ███      ███   ███    ███      ███ ███      ███ ███  ███         
 ██   ███                       █████ ██████  ███████████   ███████ ████  ████  ███      ███ ███   ████  ████ 
  █   ██████         ███          ██████ ███   ██████ ███     █████   ██████    ███      ███ ███     ██████   
      █████████████████                                                                                       
       ██████████████                                                                                         
          ████████                                                                                            


Developed by Brian Venegas

""")

# The following function is used to login to the Dutchie Backoffice
def login():

        #Please enter the URL of the Dutchie Backoffice table with all of the filters you wish to have applied as well as showing all the products on one page 
        driver.get(FilterList)
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
def fetch_Inventories(bulk_flower = True):
    if(bulk_flower):
        driver.get(BULK_FLOWER_LINK)
        time.sleep(5)
    
    all_products = []
    seen_rows = set()

    #The following try block attempts to fetch the inventory data from the Dutchie Backoffice by scrolling through the table         
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

        # The following function is used to fetch and process the rows of the table into a list of Product objects, and returns every product found on the page as a list
        def fetch_and_process_rows():
            rows = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")  # Find all rows in the table
            processed_products = []
                    
            for row in rows[1:]:  # Skip the first row as it is the header
                row_id = row.get_attribute("data-rowindex")
                # print(f"Processing row_id: {row_id}")
                if row_id in seen_rows:
                    # print(f"Row {row_id} already processed, skipping.")
                    continue
                else:
                    print(f"Processing row_id: {row_id}")

                seen_rows.add(row_id)

                # print("Scanning row " + str(rows.index(row)) + "...")
                product = Product()
                
                #This is the point of the code in which you can modify the data that is fetched from the Dutchie Backoffice
                #If modified, ensure to modify the Product class as well
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

        #This while loop is used to scroll through the table and fetch all the products on the page
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


    if(bulk_flower):
        driver.get(FilterList)
        time.sleep(5)
    return all_products



# The following function is used to map the products to their respective categories
# If modifying this code, you made need to hadd more precise categories to the product names
# ex: if "Liquid Gold" is in the product name, then the product is a "Liquid Gold Concentrate"

def mapProducts(products, bulk_flower):

    counter = 0
    categorized_products = {}
    print("Total products fetched: " + str(len(products)))
    if(bulk_flower == False):
        for product in products:
            substring = product.product_name.split("-")[0].strip()

            substringCopy = substring
            if "Liquid Gold" in substring:
                substring = "Liquid Gold Concentrates"
                if "Shatter" in substringCopy:
                    substring = "Liquid Gold Shatter"

                if "LR" in substringCopy:
                    substring = "Liquid Gold LR Concentrate"

                if "Kief" in substringCopy:
                    substring = "Liquid Gold Kief"
                
                if "Cart" in substringCopy:
                    substring = "Liquid Gold Cartridges"

                    if ".5ml" in product.product_name:
                        substring = "Liquid Gold .5ml Cartridges"
                    
                    if "1ml" in product.product_name:
                        substring = "Liquid Gold 1ml Cartridges"
                
                if "Disposable" in substringCopy:
                    substring = "Liquid Gold Disposable"
                


                
            if "Shake" in product.product_name:
                substring = substring + " Shake"

            
            if "Backpackboyz" in product.product_name:
                substring = "Backpackboyz"
                if "3.5g" in product.product_name:
                    substring = substring + " 3.5 g"
                
            if "MAC Oils Glass" in product.product_name:
                substring = "MAC Pharms Cartridges"
            
            if "Mac Oils Glass" in product.product_name:
                substring = "MAC Pharms Cartridges"

            
            if substring not in categorized_products:
                categorized_products[substring] = []
            categorized_products[substring].append(product)
            counter += 1
    else: 
        for product in products:
            substring = product.product_name.split("-")[0].strip()
            if "N/A" in substring:
                continue
            else:
                if "BULK FLOWER" not in categorized_products:
                    categorized_products["BULK FLOWER"] = []
            categorized_products["BULK FLOWER"].append(product)
            counter += 1
    print(f"Total products categorized: {counter}")
    return categorized_products

# The following code is used to authenticate the user's credentials and connect to the Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = spreadSheetID
SERVICE_ACCOUNT_FILE = get_service_account_file()
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)


# The following function is used to check if a sheet exists in the Google Sheet
# If the sheet does not exist, it creates the sheet
def checkIfSheetExists(sheetName):
    sheets = service.spreadsheets().get(spreadsheetId=spreadSheetID).execute().get('sheets', [])
    sheet_titles = [sheet['properties']['title'] for sheet in sheets]
    if sheetName not in sheet_titles:
        print(f"Sheet '{sheetName}' does not exist. Creating sheet...")
        body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': sheetName
                        }
                    }
                }
            ]
        }
        request = service.spreadsheets().batchUpdate(spreadsheetId=spreadSheetID, body=body)
        response = request.execute()
        print(f"Sheet '{sheetName}' created successfully.") 
    else: 
        print(f"Sheet '{sheetName}' already exists.")

# The following function is used to clear the data in a sheet in the Google Sheet
def clearSheet(category):
    try:
        sheet_id = getSheetId(category)
        if sheet_id is None:
            print(f"Sheet ID not found for category '{category}'")
            return

        request_body = {
            "requests": [
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,  # Row 2 (0-indexed, so row 1)
                            "startColumnIndex": 0,  # Column A (0-indexed)
                            "endColumnIndex": 8  # Column I (0-indexed, exclusive)
                        },
                        "fields": "userEnteredValue"
                    }
                }
            ]
        }

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=request_body
        ).execute()
        print(f"Cleared data in sheet '{category}'")
    except Exception as e:
        print(f"Error clearing data in sheet '{category}': {e}")
    

# The following function is used to get the ID of a sheet in the Google Sheet
def getSheetId(sheetName):
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None

    for sheet in spreadsheet.get('sheets'):
        if sheet.get('properties').get('title') == sheetName:
            sheet_id = sheet.get('properties').get('sheetId')
            break

    return sheet_id

# This portion of the code is used to write the data to the Google Sheet
# This function is meant to be customized due to the structure of your Google Sheet
# The current code is set up to write the data to the Google Sheet in the following format:
# Product Name | Package ID | Available | Inventory Date | Batch | THC | Room as well as the current time in the K column
# In spereate sheets for each category of product

def writeToGoogleSheets(categoriezed_products):

    # This for loop goes through each category and for each product in that category, it writes the product data to the correct category sheet in the Google Sheet
    for category, products in categoriezed_products.items():
        if category == "N/A":
            continue
        checkIfSheetExists(category)
        clearSheet(category)
        RANGE_NAME = f"'{category}'!A2"
        values = [[product.product_name, product.package_id, product.available, product.inventory_date, product.batch, product.thc, product.room] for product in products]

        body = {
        'values': values
        }


        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='USER_ENTERED', body=body).execute()
        

        time_range = f"'{category}'!I2"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        time_body = {
            'values': [[current_time]]
        }

        time_result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=time_range,
            valueInputOption='USER_ENTERED', body=time_body).execute()

        print(f"{result.get('updatedCells')} cells updated.")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    time_body = {
        'values': [[current_time]]
    }

    time_result = service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID, range="'PN W/ CS.'!D3",
    valueInputOption='USER_ENTERED', body=time_body).execute()




## MAIN PROGRAM ##
# The user's credentials are used to login to the Dutchie Backoffice
print_header()
login()

# The fetch_Inventories is repeatedly called to fetch the inventory data from the Dutchie Backoffice (in 30 second intervals) until the program is terminated
while True:
    # The fetch_Inventories function is called to fetch the inventory data from the Dutchie Backoffice
    print("Fetching product data from Dutchie Backoffice...")
    products = fetch_Inventories(False)
    print("Data fetched, attempting to fetch bulk flower data...")
    all_bulk_flower = fetch_Inventories(True)
    print("All Data fetched from Dutchie Backoffice @ " + str(time.ctime() + "..."))
    # all_bulk_flower = fetch_Production_Bulk_Flower()

    # The mapProducts function is called to map the products to their respective categories
    print("Mapping products to categories...")
    
    categorized_products = mapProducts(products, False)
    
    print("Mapping bulk flower to categories...")
    categorized_flowers = mapProducts(all_bulk_flower, True)
    print("Printing products categories...")

    # The categories are printed to the console
    for category in categorized_products:
        print(category)

    # The writeToGoogleSheets function is called to write the data to the Google Sheet
    writeToGoogleSheets(categorized_products)
    writeToGoogleSheets(categorized_flowers)
    # writeToGoogleSheets_single(all_bulk_flower)
    print("Data written to Google Sheets @ " + str(time.ctime()))

    # The program sleeps for 30 seconds before refreshing the Dutchie Backoffice page and fetching the inventory data again
    print("Sleeping for 30 seconds...")
    time.sleep(30)
    driver.refresh()
    time.sleep(5)
    
