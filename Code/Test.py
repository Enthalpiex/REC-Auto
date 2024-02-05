import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime, timedelta

class SeleniumUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Setting")
        self.root.geometry("300x400")

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

        self.day_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_scheduled_label())

        self.scheduled_var = tk.BooleanVar()
        scheduled_checkbox = tk.Checkbutton(content_frame, text="Scheduled", variable=self.scheduled_var, command=self.update_scheduled_label)
        scheduled_checkbox.grid(row=8, column=0, columnspan=2, pady=5)

        self.scheduled_label = tk.Label(content_frame, text="")
        self.scheduled_label.grid(row=9, column=0, columnspan=2, pady=5)

        # Initialize remaining time variable and label
        self.remaining_time_var = tk.StringVar()
        self.remaining_time_label = tk.Label(content_frame, textvariable=self.remaining_time_var, font=("Helvetica", 10, "bold"), fg="black")

        start_button = tk.Button(content_frame, text="Start", command=self.start_selenium_script)
        start_button.grid(row=10, column=0, columnspan=2, pady=20)  # Adjusted the row to 10
        self.start_button = start_button  # Store a reference to the START button

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.email = ""
        self.password = ""
        self.stay_signed_in = False
        self.selected_day = ""

        self.load_settings_from_cache()

    def update_scheduled_label(self):
        if self.scheduled_var.get():
            scheduled_text = self.get_scheduled_text()
            self.scheduled_label.config(text=scheduled_text)
            self.start_button.config(state=tk.NORMAL)  # Enable START button
            if self.remaining_time_var.get():  # Check if there is remaining time text
                self.remaining_time_label.grid(row=11, column=0, columnspan=2, pady=5)  # Show remaining time label
                self.start_button.config(state=tk.DISABLED)  # Disable START button until countdown is finished
                self.update_countdown()  # Start the countdown
        else:
            self.scheduled_label.config(text="")
            self.remaining_time_label.grid_forget()  # Hide remaining time label
            self.start_button.config(state=tk.NORMAL)  # Enable START button

    def get_scheduled_text(self):
        selected_day = self.day_combobox.get()
        if selected_day == "Tuesday":
            return "Scheduled: Saturday 5:30PM"
        elif selected_day == "Friday":
            return "Scheduled: Tuesday 7:15PM"
        elif selected_day == "Sunday":
            return "Scheduled: Thursday 8:15AM"
        else:
            return "Scheduled information not available for this day"

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

                # Add loading scheduled information
                self.scheduled_var.set(data.get('scheduled', False))
                self.update_scheduled_label()

                # Add loading remaining time information
                self.remaining_time_var.set(data.get('remaining_time', ''))
        except FileNotFoundError:
            pass  # File doesn't exist, ignore

    def save_settings_to_cache(self):
        data = {
            'email': self.email_entry.get(),
            'password': self.password_entry.get(),
            'stay_signed_in': self.stay_signed_in_var.get(),
            'remember_info': self.remember_info_var.get(),
            'selected_day': self.selected_day,
            'scheduled': self.scheduled_var.get(),  # Save scheduled information
            'remaining_time': self.remaining_time_var.get()  # Save remaining time information
        }
        with open('settings_cache.json', 'w') as file:
            json.dump(data, file)

    def on_close(self):
        # Save settings to cache if "Remember Info" is checked
        self.save_settings_to_cache()
        # Do other cleanup tasks as needed
        self.root.destroy()

    # Add the following two functions to handle countdown
    def update_countdown(self):
        remaining_time = self.calculate_remaining_time()
        if remaining_time.total_seconds() > 0:
            self.remaining_time_var.set(str(remaining_time))
            self.root.after(1000, self.update_countdown)
        else:
            self.remaining_time_var.set("")  # Countdown finished, hide the text
            self.start_selenium_script()

    def calculate_remaining_time(self):
        scheduled_datetime = self.get_scheduled_datetime()
        current_datetime = datetime.now()
        remaining_time = scheduled_datetime - current_datetime
        return remaining_time

    def get_scheduled_datetime(self):
        selected_day = self.day_combobox.get()
        if selected_day == "Tuesday":
            scheduled_time = datetime.strptime("17:30:00", "%H:%M:%S")
        elif selected_day == "Friday":
            scheduled_time = datetime.strptime("19:15:00", "%H:%M:%S")
        elif selected_day == "Sunday":
            scheduled_time = datetime.strptime("08:15:00", "%H:%M:%S")
        else:
            # Default to today's date and time
            scheduled_time = datetime.now().replace(second=0, microsecond=0)
        return scheduled_time

if __name__ == "__main__":
    root = tk.Tk()
    selenium_ui = SeleniumUI(root)
    root.mainloop()