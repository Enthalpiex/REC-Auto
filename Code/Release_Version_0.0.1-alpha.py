import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class SeleniumUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Setting")
        self.root.geometry("300x300")

        content_frame = tk.Frame(root)
        content_frame.pack(expand=True)

        version_label = tk.Label(content_frame, text="Version 0.0.1")
        version_label.grid(row=0, column=0, columnspan=2, pady=10)

        rec_label = tk.Label(content_frame, text="REC auto-booking scripts", font=("Helvetica", 8, "italic"), fg="gray")
        rec_label.grid(row=1, column=0, columnspan=2)

        email_label = tk.Label(content_frame, text="Email:")
        email_label.grid(row=2, column=0, sticky=tk.E)
        self.email_entry = tk.Entry(content_frame)
        self.email_entry.grid(row=2, column=1)

        password_label = tk.Label(content_frame, text="Password:")
        password_label.grid(row=3, column=0, sticky=tk.E)
        self.password_entry = tk.Entry(content_frame, show="*")
        self.password_entry.grid(row=3, column=1)

        self.stay_signed_in_var = tk.BooleanVar()
        stay_signed_in_checkbox = tk.Checkbutton(content_frame, text="Stay Signed In", variable=self.stay_signed_in_var)
        stay_signed_in_checkbox.grid(row=4, column=0, columnspan=2, pady=5)

        self.remember_info_var = tk.BooleanVar(value=True)
        remember_info_checkbox = tk.Checkbutton(content_frame, text="Remember Info", variable=self.remember_info_var)
        remember_info_checkbox.grid(row=5, column=0, columnspan=2, pady=5)

        days_label = tk.Label(content_frame, text="Select Day:")
        days_label.grid(row=6, column=0, sticky=tk.E)
        days_options = ["Tuesday", "Friday", "Sunday"]
        self.day_combobox = ttk.Combobox(content_frame, values=days_options)
        self.day_combobox.grid(row=6, column=1)

        start_button = tk.Button(content_frame, text="Start", command=self.start_selenium_script)
        start_button.grid(row=7, column=0, columnspan=2, pady=20)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.email = ""
        self.password = ""
        self.stay_signed_in = False
        self.selected_day = ""

        self.load_settings_from_cache()

    def start_selenium_script(self):
        self.email = self.email_entry.get()
        self.password = self.password_entry.get()
        self.stay_signed_in = self.stay_signed_in_var.get()
        self.selected_day = self.day_combobox.get()
        self.run_selenium_script()
        self.root.destroy()

    def run_selenium_script(self):
        driver = webdriver.Chrome()
        driver.get('https://accounts.surrey.ca/auth.aspx?action=login&s=e30=&return_url=https%3A%2F%2Faccounts.surrey.ca%2Fprofile.aspx%3Faction%3Dlogin%26s%3De30%3D%26language%3D')

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginradius-login-emailid'))
        )
        password_input = driver.find_element(By.ID, 'loginradius-login-password')
        stay_signed_in_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginradius-login-stayLogin'))
        )
        submit_button = driver.find_element(By.ID, 'loginradius-validate-login')

        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        driver.execute_script("arguments[0].click();", stay_signed_in_checkbox)
        submit_button.click()
        time.sleep(1)
        driver.get('https://www.surrey.ca/parks-recreation/activities-registration/search-results?age_groups=youth&type=dropins&activities=drop_in_badminton&locations=3c2aa8a6-94b9-4667-bd3e-545d2023fa4f')
        dropdowns = driver.find_elements(By.CSS_SELECTOR, 'details.dropins-date')
        time.sleep(0.5)
        for dropdown in dropdowns:
            if self.selected_day in dropdown.text:
                dropdown_summary = dropdown.find_element(By.CSS_SELECTOR, 'summary.dropins-date-header')
                dropdown_summary.click()
                current_window = driver.window_handles[0]
                buttons = dropdown.find_elements(By.XPATH, './/a[@class="button button--pm-alt external-link"]')

                first_button_clicked = False

                for button in buttons:
                    if "Youth" in button.text:
                        driver.execute_script("arguments[0].click();", button)
                        first_button_clicked = True
                        break
                    elif "13" in button.text:
                        driver.execute_script("arguments[0].click();", button)
                        first_button_clicked = True

                if not first_button_clicked and len(buttons) > 1:
                    driver.execute_script("arguments[0].click();", buttons[1])

                wait = WebDriverWait(driver, 30)
                # 获取所有窗口句柄
                handles = driver.window_handles
                for window_id in handles:
                    if window_id != current_window:
                        # 切换到新窗口
                        driver.switch_to.window(window_id)
                        print(driver.current_url)
                        break
                current_window = driver.window_handles[0]
                driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[1]/div/section[2]/a').click()

                time.sleep(5)
                
                wait = WebDriverWait(driver, 4)
                driver.find_element(by=By.XPATH, value='//*[@id="event-attendees"]/div[2]/div/a').click()
                wait = WebDriverWait(driver, 2)
                driver.find_element(by=By.XPATH, value='//*[@id="90673420-fa18-4494-87e3-5352c8ad09a7"]/div/ul/li[1]/div/table/tbody/tr[2]').click()
                wait = WebDriverWait(driver, 4)
                driver.find_element(by=By.XPATH, value='//*[@id="process-now-335"]').click()

                break


        if self.remember_info_var.get():
            self.save_settings_to_cache()

        input("Please manually close the browser...")

        driver.quit()

    def load_settings_from_cache(self):
        try:
            with open('settings_cache.json', 'r') as file:
                data = json.load(file)
                self.email_entry.insert(0, data.get('email', ''))
                self.password_entry.insert(0, data.get('password', ''))
                self.stay_signed_in_var.set(data.get('stay_signed_in', False))
                self.remember_info_var.set(data.get('remember_info', True))
                self.selected_day = data.get('selected_day', '')
                if self.selected_day:
                    self.day_combobox.set(self.selected_day)
        except FileNotFoundError:
            pass  # File doesn't exist, ignore

    def save_settings_to_cache(self):
        data = {
            'email': self.email_entry.get(),
            'password': self.password_entry.get(),
            'stay_signed_in': self.stay_signed_in_var.get(),
            'remember_info': self.remember_info_var.get(),
            'selected_day': self.selected_day
        }
        with open('settings_cache.json', 'w') as file:
            json.dump(data, file)

    def on_close(self):
        # Save settings to cache if "Remember Info" is checked
        self.save_settings_to_cache()
        # Do other cleanup tasks as needed
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    selenium_ui = SeleniumUI(root)
    root.mainloop()
