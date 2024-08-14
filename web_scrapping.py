from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the target URL
driver.get('https://hprera.nic.in/PublicDashboard')

# Wait for the Registered Projects tab to be clickable and click it
wait = WebDriverWait(driver, 80)  # Increased timeout for better reliability
try:
    print("Waiting for Registered Projects tab to be clickable...")
    reg_projects_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-target='#reg-Projects']")))
    print("Registered Projects tab found, clicking...")
    driver.execute_script("arguments[0].scrollIntoView(true);", reg_projects_tab)
    driver.execute_script("arguments[0].click();", reg_projects_tab)
except Exception as e:
    print("Error finding or clicking Registered Projects tab:", e)
    driver.quit()
    exit()

# Pause to let the tab content load
time.sleep(40)

# Use BeautifulSoup to parse the page content
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find the Registered Projects section
projects_section = soup.find('div', id='reg-Projects')

if not projects_section:
    print("Registered Projects section not found.")
else:
    print("Registered Projects section found.")

# Extract the first 6 project elements
project_elements = projects_section.find_all('a', title='View Application', limit=6)

if not project_elements:
    print("No project elements found.")
else:
    print(f"Found {len(project_elements)} project elements.")

project_details = []

for i, project in enumerate(project_elements):
    print(f"Processing project {i+1}")
    # Find the project element using Selenium
    project_element = driver.find_elements(By.CSS_SELECTOR, "a[title='View Application']")[i]
    
    # Scroll the project element into view and click it
    driver.execute_script("arguments[0].scrollIntoView(true);", project_element)
    driver.execute_script("arguments[0].click();", project_element)
    
    # Ensure modal is visible
    try:
        wait.until(EC.visibility_of_element_located((By.ID, 'modal-data-display-tab_project_main')))
    except Exception as e:
        print("Error finding modal:", e)
        continue
    
    # Click on the "Promoter Details" tab within the modal
    try:
        promoter_tab = wait.until(EC.element_to_be_clickable((By.ID, 'PromoterDetails')))
        driver.execute_script("arguments[0].scrollIntoView(true);", promoter_tab)
        driver.execute_script("arguments[0].click();", promoter_tab)
    except Exception as e:
        print("Error finding or clicking Promoter Details tab:", e)
        continue

    # Pause to let the tab content load
    time.sleep(40)

    # Use BeautifulSoup to parse the modal content
    modal_soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract details from the table
    table = modal_soup.find('table', class_='table-borderless')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    details = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            key = cells[0].text.strip()
            value = cells[1].text.strip()
            # Clean up the value to remove unwanted words
            if key == 'GSTIN No.':
                value = value.replace('GST Certificate', '').strip()
            if key == 'PAN No.':
                value = value.replace('PAN File', '').replace('PAN Card', '').strip()
            details[key] = value
    
    # Append details to project details list
    project_details.append({
        'Project Name': project_element.text.strip(),
        'GSTIN': details.get('GSTIN No.', 'N/A'),
        'PAN': details.get('PAN No.', 'N/A'),
        'Name': details.get('Name', 'N/A'),
        'Permanent Address': details.get('Permanent Address', 'N/A')
    })

    # Close the modal
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close")))
        driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
        driver.execute_script("arguments[0].click();", close_button)
    except Exception as e:
        print("Error finding or clicking Close button:", e)

    # Pause to let the modal close
    time.sleep(40)

    # Refresh the page to reset the state
    driver.refresh()

    # Wait for the Registered Projects tab to be clickable and click it again
    try:
        print("Waiting for Registered Projects tab to be clickable again after refresh...")
        reg_projects_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-target='#reg-Projects']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", reg_projects_tab)
        driver.execute_script("arguments[0].click();", reg_projects_tab)
    except Exception as e:
        print("Error finding or clicking Registered Projects tab on refresh:", e)

    # Pause to let the tab content load again
    time.sleep(40)

# Print the project details
print("\nProject Details:")
for i, detail in enumerate(project_details):
    print(f"\nProject {i+1}:")
    for key, value in detail.items():
        print(f"{key}: {value}")
    print("-" * 40)


# Close the driver
driver.quit()
