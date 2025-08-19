import os
import time
import warnings
import pandas as pd
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime

# ----------------------- ENV -----------------------
load_dotenv()
username = os.getenv("DUTCHIE_USERNAME")
password = os.getenv("DUTCHIE_PASSWORD")
report_url = "https://birch.backoffice.dutchie.com/reports/inventory/reports/conversion-detail-costing-report"
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
# ----------------------- BROWSER -----------------------
warnings.filterwarnings("ignore", category=ResourceWarning)
options = uc.ChromeOptions()
options.headless = False  # set True if you want headless
options.add_argument("--disable-popup-blocking")
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_setting_values.notifications": 2
})


driver = uc.Chrome(options=options)

# ----------------------- UI -----------------------
def get_date_range_ui():
    def submit():
        nonlocal start_date, end_date
        start_date = start_entry.get_date().strftime("%Y-%m-%d")
        end_date = end_entry.get_date().strftime("%Y-%m-%d")
        root.destroy()

    root = tk.Tk()
    root.title("Select Date Range")
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

# ----------------------- LOGIN -----------------------
def login():
    driver.get(report_url)
    time.sleep(3)

    user_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='auth_input_username']")
    user_input.send_keys(username)
    time.sleep(0.5)

    pass_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='auth_input_password']")
    pass_input.send_keys(password)
    time.sleep(0.5)

    login_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='auth_button_go-green']"))
    )
    login_btn.click()
    time.sleep(3)

# ----------------------- DATE RANGE -----------------------
def open_date_range_menu():
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "actions-menu-button"))
    )
    btn.click()
    time.sleep(1)

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def set_date_range(start_date, end_date):
    """
    Set start and end dates in the Conversion Detail Costing Report page.
    Dates should be 'YYYY-MM-DD'.
    """
    start_fmt = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    end_fmt = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    # Wait for date inputs to be present
    inputs = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input.cTwclH.dMdWtf.MuiOutlinedInput-input[type='text']")
        )
    )
    if len(inputs) < 2:
        raise RuntimeError("❌ Could not find both start and end date inputs")

    start_input, end_input = inputs[0], inputs[1]

    for input_elem, value in [(start_input, start_fmt), (end_input, end_fmt)]:
        # Click via JS to avoid overlay issues
        driver.execute_script("arguments[0].click();", input_elem)
        time.sleep(0.2)
        input_elem.send_keys(Keys.CONTROL + "a")
        input_elem.send_keys(Keys.DELETE)
        time.sleep(0.2)
        input_elem.send_keys(value)
        time.sleep(0.2)

    # Close the calendar after entering the second date
    title_elem = driver.find_element(By.CSS_SELECTOR, "h1.sc-cmSbgX.lfzUAs")
    driver.execute_script("arguments[0].click();", title_elem)
    time.sleep(0.3)

    print(f"✅ Date range set: {start_fmt} → {end_fmt}")



def confirm_date_range():
    inputs = driver.find_elements(By.CSS_SELECTOR, "input.MuiOutlinedInput-input[type='text']")
    if inputs:
        inputs[-1].click()
        time.sleep(0.2)
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(0.5)

# ----------------------- EXPORT -----------------------

def run_report():
    # Wait for buttons with class MuiButton-containedPrimary
    buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.MuiButton-containedPrimary"))
    )

    # Find the one with visible text "Run"
    run_btn = None
    for btn in buttons:
        if btn.is_displayed() and btn.text.strip().lower() == "run":
            run_btn = btn
            break

    if not run_btn:
        raise RuntimeError("❌ Could not find visible Run button")

    # Click via JS to bypass overlays
    driver.execute_script("arguments[0].click();", run_btn)
    print("▶️ Run button clicked via JS")
    
    # Optional: wait for some report-specific element to appear after running
    time.sleep(3)




def export_report():
    # Click Actions menu
    actions_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "actions-menu-button"))
    )
    driver.execute_script("arguments[0].click();", actions_btn)
    print("✅ Actions menu clicked")
    time.sleep(0.3)  # let menu render

    # Wait for the menu container
    menu_container = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.MuiMenu-list"))
    )

    # Find Export item
    menu_items = menu_container.find_elements(By.CSS_SELECTOR, "li[role='menuitem']")
    for item in menu_items:
        if item.text.strip().lower() == "export":
            driver.execute_script("arguments[0].click();", item)
            print("✅ Export clicked")
            return

    raise RuntimeError("❌ Export menu item not found")


def download_excel(download_dir):
    """
    Wait for a new Excel file to appear in download_dir and return its full path.
    """
    os.makedirs(download_dir, exist_ok=True)
    timeout = 30  # seconds
    elapsed = 0
    filename = None

    while elapsed < timeout:
        files = os.listdir(download_dir)
        excel_files = [f for f in files if f.endswith(".xlsx")]
        if excel_files:
            # Pick the most recent file
            excel_files.sort(key=lambda f: os.path.getmtime(os.path.join(download_dir, f)), reverse=True)
            filename = excel_files[0]
            break
        time.sleep(1)
        elapsed += 1

    if not filename:
        raise RuntimeError("❌ Excel file not downloaded")

    file_path = os.path.join(download_dir, filename)
    print(f"✅ Excel downloaded: {file_path}")
    return file_path

def clean_excel(file_path):
    df = pd.read_excel(file_path, skiprows=4)
    df = df.iloc[:, 6:]
    df.reset_index(drop=True, inplace=True)
    print(f"✅ Excel cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

# ----------------------- MAIN -----------------------
def main():
    start_date, end_date = get_date_range_ui()
    print(f"📅 Selected range: {start_date} → {end_date}")

    login()
    set_date_range(start_date, end_date)
    time.sleep(0.3)
    run_report()
    export_report()
    time.sleep(5)


    excel_file = download_excel(download_dir)

    # Placeholder: send df to Google Sheets
    # upload_to_google_sheet(df, spreadSheetID, sheet_name="Conversion Detail Costing")

    input("Press Enter to close browser...")

    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"🗑️ Deleted file: {excel_file}")
    driver.quit()

if __name__ == "__main__":
    main()
