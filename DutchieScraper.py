import undetected_chromedriver as uc
import time
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#SETUP: Enter your username and password for the Dutchie Backoffice
username = "victorv1798"
passW = "BIGSMOKE98"

#The following code is used to suppress the ResourceWarning that is thrown by the undetected_chromedriver package
warnings.filterwarnings("ignore", category=ResourceWarning)


#The following code is used to create a headless browser using the undetected_chromedriver package
chromeOptions = uc.ChromeOptions()
chromeOptions.headless = True
driver = uc.Chrome(use_subprocess=True, options=chromeOptions)

#The following code is used to login to the Dutchie Backoffice
try:
    driver.get("https://cove.backoffice.dutchie.com/home")
    time.sleep(10)

    #The following code is used to enter the username and password into the login form
    userName = driver.find_element(By.ID, "input-input_login-email")
    userName.send_keys(username)
    time.sleep(5)

    #The following code is used to enter the password into the login form
    password = driver.find_element(By.ID, "input-input_login-password")
    password.send_keys(passW)

    #The following code is used to click the login button
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='auth_button_go-green']"))
    )
    login_button.click()
    time.sleep(5)

    try:
        #The following code checks if the page is ready by looking for the main navigation menu
        presElement = EC.presence_of_element_located((By.ID, 'main-navigation-menu'))
        WebDriverWait(driver, 10).until(presElement)
        print("Page is ready!")

        driver.get("https://cove.backoffice.dutchie.com/products/inventory?categories=Everyday+14g+Pre-Packed+Flower%2CEveryday+14g+Pre-Packed+Shake+Flower%2CEveryday+28g+Pre-Packed+Flower%2CEveryday+3.5g+Pre-Packed")
        time.sleep(5)

        # Scroll to the bottom of the page to load all elements
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load new elements
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract the data (available quantities for set filters)
        available_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-field='quantity'] div.MuiDataGrid-cellContent")
        available_data = [elem.text for elem in available_elements]
        print(available_data)  # Print the extracted data
    except:
        print("Login failed or elemement not found")
finally:
    try:
        time.sleep(2)  # Add a small delay before quitting
        driver.close()
        driver.quit()
        print("Driver quit successfully.")
    except Exception as e:
        print(f"Exception during driver quit: {e}")