Dutchie Scraper

This Python script is designed to expedite the export/import of certain products on the Dutchie inventory system.
Disclaimer

In order for this program to work, the user must enter their own Dutchie  REPLACE_USERNAMEand password, Google Sheets ID, Google Sheets API Key, and service account credentials. Customize the script as indicated to match personal preferences for input scanning and output to sheets.

Features
    ~ Uses a headless Chrome browser to log into an authorized Dutchie account.
    ~ Scans, categorizes, and outputs inventory products to a Google Spreadsheet.
    ~ Extracts details such as product name, package ID, available amount, inventory date, batch ID, THC percentage, and storage room.
    ~ Categorizes products based on the product name up to the hyphen and writes to the ~ corresponding tab in the Google Sheet.
    ~ Continuously runs every 30 seconds (customizable).

Features Coming Soon:

Fluid Row Selection:
    ~ As is, the program will read in the product properties based on how you have them set on your Dutchie Account. So, they must be in the same order as the script reads them in or they will incorrectly print to your sheet. 
    ~ I plan to rework the "read_and_proccess_rows" function so that this is not an issue. 

    
GUI MENU:
    ~ A menu where the user can easily select what product properties, which categories, etc. and how they want it formatted on the google sheet. 
    ~ The main purpose is to provide a much friendlier user experience and fluidity in customization. 

Prerequisites

    ~ Python 3.x
    ~ Google Sheets API credentials (service account JSON file)
    ~ Dutchie account credentials

Libraries

The following Python libraries are required:

    ~ undetected_chromedriver
    ~ selenium
    ~ google-auth
    ~ google-auth-oauthlib
    ~ google-auth-httplib2
    ~ google-api-python-client

Install the required libraries using pip:

bash

    ~ pip install undetected_chromedriver selenium google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Setup Instructions

    1. Clone the Repository:

    bash

    git clone <repository-url>
    cd <repository-directory>

    2. Add Your Credentials:
        Place your  ENTER_SERVICE_ACCOUNT_JSON_HEREfile in the project directory.
        Open the script and enter your Dutchie username, password, and Google Sheets ID.

    3. Customize the Script:
        Modify the script to customize the scanning and categorization logic as per your needs.

Running the Script

    ~ To run the script, use the following command:

    python DutchieScraper.py

Customization

Product Parameters
    ~ The script is configured to read specific product parameters. You can add or remove parameters by modifying the Product class and the scanning logic.

Categorization
    ~ The categorization logic is based on the product name up to the hyphen. Modify the mapProducts function to change the categorization rules.

Run Interval
    ~ The script is set to run every 30 seconds. Change the interval by modifying the sleep duration in the while loop at the end of the script.

Pyinstaller
    ~ After configuring the script to your liking, I recommened making it an executable with PyInstaller.

Security Considerations
    ~ Keep your credentials secure: Do not share your service account JSON file, Dutchie account credentials, or Google Sheets ID publicly.
    ~ Environment Variables: Consider using environment variables to store sensitive information.

Troubleshooting
Common Issues
    ~ Authentication Errors: Ensure your Google API credentials are correct and have the necessary permissions.
    ~ Element Not Found: Verify the CSS selectors in the script match the Dutchie interface.
    ~ ChromeDriver Errors: Ensure the correct version of ChromeDriver is installed and matches your Chrome browser version.

