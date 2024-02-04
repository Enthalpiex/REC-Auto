from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

email = ' '
password = ' '

driver = webdriver.Chrome()
driver.get('https://accounts.surrey.ca/auth.aspx?action=login&s=e30=&return_url=https%3A%2F%2Faccounts.surrey.ca%2Fprofile.aspx%3Faction%3Dlogin%26s%3De30%3D%26language%3D')

# Find email, password input fields, and submit button
email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'loginradius-login-emailid'))
)
password_input = driver.find_element(By.ID, 'loginradius-login-password')
stay_signed_in_checkbox = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'loginradius-login-stayLogin'))
)
submit_button = driver.find_element(By.ID, 'loginradius-validate-login')

# Input email and password
email_input.send_keys(email)
password_input.send_keys(password)

driver.execute_script("arguments[0].click();", stay_signed_in_checkbox)

submit_button.click()

time.sleep(2)

driver.get('https://www.surrey.ca/parks-recreation/activities-registration/search-results?age_groups=youth&type=dropins&activities=drop_in_badminton&locations=3c2aa8a6-94b9-4667-bd3e-545d2023fa4f')

# Find all dropdowns
dropdowns = driver.find_elements(By.CSS_SELECTOR, 'details.dropins-date')

for dropdown in dropdowns:

    if 'Sunday' in dropdown.text:

        dropdown_summary = dropdown.find_element(By.CSS_SELECTOR, 'summary.dropins-date-header')
        dropdown_summary.click()

        current_window = driver.window_handles[0]
        join_button = dropdown.find_element(By.XPATH, './/a[@class="button button--pm-alt external-link"]')
        join_button.click()
        wait = WebDriverWait(driver, 10)
        # 获取所有窗口句柄``
        handles = driver.window_handles
        for window_id in handles:
            if window_id != current_window:
                # 切换到新窗口
                driver.switch_to.window(window_id)
                print(driver.current_url)
                break
        current_window = driver.window_handles[0]
        driver.find_element(by=By.XPATH, value='//*[@id="main-content"]/div/div/div[1]/div/section[2]/a').click()
        
        # 等待新窗口打开
        wait = WebDriverWait(driver, 4)
        driver.find_element(by=By.XPATH, value='//*[@id="event-attendees"]/div[2]/div/a').click()
        wait = WebDriverWait(driver, 2)
        driver.find_element(by=By.XPATH, value='//*[@id="90673420-fa18-4494-87e3-5352c8ad09a7"]/div/ul/li[1]/div/table/tbody/tr[2]').click()
        wait = WebDriverWait(driver, 4)
        driver.find_element(by=By.XPATH, value='//*[@id="process-now-335"]').click()
    break 

input("Please manually close the browser...")

driver.quit()