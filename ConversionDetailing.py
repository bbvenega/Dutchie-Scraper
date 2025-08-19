from httpcore import TimeoutException
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
from selenium.webdriver.common.action_chains import ActionChains


import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime


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
        
def get_date_range_ui():
    def submit():
        nonlocal start_date, end_date
        start_date = start_entry.get_date().strftime("%Y-%m-%d")
        end_date = end_entry.get_date().strftime("%Y-%m-%d")
        root.destroy()

    root = tk.Tk()
    root.title("Dutchie Scraper - Date Range")
    root.geometry("350x150")

    tk.Label(root, text="Start Date:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    start_entry = DateEntry(root, width=18, background="darkblue",
                            foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
    start_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="End Date:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    end_entry = DateEntry(root, width=18, background="darkblue",
                          foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
    end_entry.grid(row=1, column=1, padx=10, pady=10)

    submit_btn = ttk.Button(root, text="Submit", command=submit)
    submit_btn.grid(row=2, columnspan=2, pady=15)

    start_date = end_date = None
    root.mainloop()
    return start_date, end_date
        
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


def open_date_range_menu(driver, timeout=10):
    """Clicks the date range button to open the calendar dropdown."""
    try:
        date_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "actions-menu-button"))
        )
        date_button.click()
        print("✅ Date range button clicked.")
    except Exception as e:
        print("❌ Could not click date range button:", e)


def set_date_range(driver, start_date, end_date, timeout=10):
    """
    Enter start_date and end_date into Dutchie date fields.
    Dates should be 'YYYY-MM-DD'.
    """
    # Convert format → MM/DD/YYYY
    start_fmt = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    end_fmt = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    wait = WebDriverWait(driver, timeout)
    inputs = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[placeholder='MM/DD/YYYY']"))
    )

    if len(inputs) < 2:
        raise RuntimeError("❌ Could not find start & end date inputs")

    start_input, end_input = inputs[0], inputs[1]

    # --- Start Date ---
    start_input.click()
    time.sleep(0.3)  # Ensure input is focused
    start_input.send_keys(Keys.CONTROL + "a")
    start_input.send_keys(Keys.DELETE)
    time.sleep(0.3)  # Wait for input to clear
    start_input.send_keys(start_fmt)

    # --- End Date ---
    end_input.click()
    time.sleep(0.3)  # Ensure input is focused
    end_input.send_keys(Keys.CONTROL + "a")
    end_input.send_keys(Keys.DELETE)
    time.sleep(0.3)  # Wait for input to clear
    end_input.send_keys(end_fmt)

    print(f"✅ Date range set: {start_fmt} → {end_fmt}")
    time.sleep(5)  # Allow time for input to register



def confirm_date_range(driver):
    """
    Sends ESC to the focused element reliably.
    """
    try:
        # Focus the last input (end date) to ensure picker is active
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='MM/DD/YYYY']")
        if inputs:
            inputs[-1].click()
            time.sleep(0.2)

        # Send ESC via ActionChains
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)

        print("✅ Date range confirmed with ESC via automation")
    except Exception as e:
        print("⚠️ Could not confirm date range via automated ESC:", e)




def main():
    print_header()
    start_date, end_date = get_date_range_ui()
    print(f"📅 Selected range: {start_date} → {end_date}")

    try:
        login()
        open_date_range_menu(driver)
        set_date_range(driver, start_date, end_date)
        confirm_date_range(driver)
        print("✅ Successfully set date range in Dutchie Backoffice")
    except Exception as e:
        print("❌ Error during login:", e)
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    main()
