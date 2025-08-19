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
reports_inventory = os.getenv("REPORTS_INVENTORY")





# The following code is used to suppress the ResourceWarning that is thrown by the undetected_chromedriver package
warnings.filterwarnings("ignore", category=ResourceWarning)

# The following code is used to create a headless browser using the undetected_chromedriver package
# For debugging purposes, you can set headless to False to see the browser in action
options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(options=options)


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
        
def login():

        #Please enter the URL of the Dutchie Backoffice table with all of the filters you wish to have applied as well as showing all the products on one page 
        try:
            print(f"Accessing the URL: {reports_inventory}")
            driver.get(reports_inventory)
            time.sleep(5)
        except Exception as e:
            print(f"Error accessing the URL: {e}")
            return

        # The following code is used to enter the username and password into the login form
        userName = driver.find_element(By.CSS_SELECTOR, "[data-testid='auth_input_username']")
        userName.send_keys(username)
        time.sleep(2)

        # The following code is used to enter the password into the login form
        password = driver.find_element(By.CSS_SELECTOR, "[data-testid='auth_input_password']")
        password.send_keys(passW)

        # The following code is used to click the login button
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='auth_button_go-green']"))
        )
        login_button.click()
        time.sleep(5)


def main():
    print_header()

    try:
        login()
        print("✅ Login attempted, check the browser window.")
    except Exception as e:
        print("❌ Error during login:", e)
    finally:
        # Optional: keep browser open for inspection
        input("Press Enter to close browser...")
        driver.quit()


if __name__ == "__main__":
    main()
