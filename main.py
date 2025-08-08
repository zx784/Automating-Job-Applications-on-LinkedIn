# === 1. IMPORT LIBRARIES ===
# Import necessary libraries for web automation, system operations, and handling credentials.
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
from selenium.common.exceptions import NoSuchElementException

# === 2. LOAD ENVIRONMENT VARIABLES ===
# Load sensitive data (email and password) from a .env file for security.
# This prevents hardcoding credentials directly in the script.
load_dotenv()
Email = os.getenv("Email")
Password = os.getenv("Password")

# === 3. SETUP SELENIUM WEBDRIVER ===
# Configure options for the Chrome browser.
chrome_options = webdriver.ChromeOptions()
# The 'detach' option keeps the browser window open even after the script finishes.
chrome_options.add_experimental_option("detach", True)
# This option can help bypass certain security certificate errors on websites.
chrome_options.add_argument('--ignore-certificate-errors')
# Initialize the Chrome driver with the specified options.
driver = webdriver.Chrome(options=chrome_options)

# === 4. OPEN LINKEDIN JOB SEARCH ===
# Navigate to the LinkedIn job search page with pre-filled filters.
# Filters used: Easy Apply (f_E=2), Remote (f_WT=2), in Malaysia (geoId=102454443).
driver.get("https://www.linkedin.com/jobs/search/?f_E=2"  # Filter for "Easy Apply"
           "&f_WT=2"  # Filter for "Remote"
           "&geoId=102454443"  # geoId for Malaysia
           "&keywords=Machine%20learning"
           "&location=Malaysia"
           "&redirect=false&position=1&pageNum=0")
sleep(1)

# === 5. LOGIN SEQUENCE ===
# Find and click the main sign-in button on the jobs page.
sign_in = driver.find_element(by=By.XPATH,
                              value='//*[@id="base-contextual-sign-in-modal"]/div/section/div/div/div/div[2]/button')
sleep(1)
sign_in.click()
sleep(1)

# Find the email and password fields and enter the credentials.
email = driver.find_element(By.XPATH, '//*[@id="base-sign-in-modal_session_key"]')
password = driver.find_element(By.XPATH, '//*[@id="base-sign-in-modal_session_password"]')
sleep(1)
email.send_keys(Email)
password.send_keys(Password)
# Send the 'Enter' key to submit the login form.
password.send_keys(Keys.ENTER)

# Pause the script to allow for manual CAPTCHA solving if it appears.
input("Press Enter in the console after you have solved the puzzle")
sleep(1)


# === 6. APPLICATION LOGIC FUNCTION ===
def attempt_to_apply():
    """
    This function attempts to apply for a single job that has already been selected.
    It uses a try/except block to differentiate between simple and complex applications.
    """
    try:
        # Find and click the "Easy Apply" button for the selected job.
        easy_apply = driver.find_element(By.CSS_SELECTOR, ".jobs-apply-button")
        easy_apply.click()
        sleep(2)  # Wait for the application modal to load.

        # Check the text of the main button in the modal footer.
        check = driver.find_element(By.CSS_SELECTOR, "footer button span")
        
        # This is the control flow for handling different application types.
        if check.text == "Next":
            # If the button says "Next", it's a multi-step application.
            # This line intentionally causes an error to jump to the `except` block.
            driver.find_element(By.ID, "Nothing")
        else:
            # If the button is "Submit", it's a single-step application.
            submit_button = driver.find_element(by=By.CSS_SELECTOR, value="footer button")
            submit_button.click()
            sleep(1) # Wait for the confirmation screen.
            # Close the "Application Submitted" confirmation dialog.
            close_confirmation_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
            close_confirmation_button.click()
            print("Application Submitted.")

    except NoSuchElementException:
        # This block runs when the "try" block fails (i.e., on a "Next" button).
        print("Complex application detected. Discarding...")
        try:
            # The correct way to discard is a two-step process.
            # Step 1: Click the 'X' button to close the main application window.
            close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
            close_button.click()
            sleep(1)  # Wait for the discard confirmation dialog to appear.

            # Step 2: Click the 'Discard' button on the confirmation dialog.
            discard_confirmation_button = driver.find_element(By.CSS_SELECTOR,
                                                               "button[data-test-dialog-secondary-btn]")
            discard_confirmation_button.click()
            print("Application discarded.")
        except NoSuchElementException:
            # If for some reason the modal can't be closed, we print a message and move on.
            print("No application modal to close. Moving on.")


# === 7. MAIN EXECUTION LOOP ===
print("Waiting for job listings to load...")
# Wait for 8 seconds to ensure the job list on the left is fully loaded.
sleep(8)

# Find all the clickable job cards on the first page.
job_listings = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")

print(f"Found {len(job_listings)} jobs. Starting to apply...")

# Loop through each job listing found.
for job in job_listings:
    # Click the job card to view its details in the right-hand pane.
    job.click()
    print("\n--- Processing new job ---")
    sleep(2)  # Wait for the job details to load.
    
    # Call the function to attempt the application process for this single job.
    attempt_to_apply()

print("\n--- All jobs have been processed. ---")