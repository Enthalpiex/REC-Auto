import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from settings_manager import SettingsManager
import time

class SeleniumUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Setting")
        self.root.geometry("300x400")

        content_frame = tk.Frame(root)
        content_frame.pack(expand=True)

        version_label = tk.Label(content_frame, text="Version 0.1.0")
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

        self.countdown_timer = None

        self.remaining_time_var = tk.StringVar()
        self.remaining_time_label = tk.Label(
            content_frame, textvariable=self.remaining_time_var
        )
        self.remaining_time_label.grid(row=11, column=0, columnspan=2, pady=5)
        self.remaining_time_label.grid_remove()


        self.start_button_text = tk.StringVar()
        self.start_button_text.set("Start")
        self.start_button = tk.Button(content_frame, textvariable=self.start_button_text, command=self.handle_start_button)
        self.start_button.grid(row=12, column=0, columnspan=2, pady=20)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.email = ""
        self.password = ""
        self.stay_signed_in = False
        self.selected_day = ""

        self.load_settings_from_cache()
        self.init_remaining_time()
        self.update_scheduled_label()

    def init_remaining_time(self):
        self.remaining_time_label.grid(row=11, column=0, columnspan=2, pady=5)

    def update_scheduled_label(self):
        if self.scheduled_var.get():
            scheduled_text = self.get_scheduled_text()
            self.scheduled_label.config(text=scheduled_text)
            self.start_button.config(state=tk.NORMAL)
            if self.remaining_time_var.get():
                self.remaining_time_label.grid(row=11, column=0, columnspan=2, pady=5)
                self.root.after(1000, self.update_countdown)
        else:
            self.scheduled_label.config(text="")
            self.remaining_time_label.grid_remove()
            self.start_button.config(state=tk.NORMAL)

    def get_scheduled_text(self):
        selected_day = self.day_combobox.get()
        scheduled_times = {
            "Tuesday": "Saturday 5:30PM",
            "Friday": "Tuesday 7:15PM",
            "Sunday": "Thursday 8:15AM"
        }
        return f"Scheduled: {scheduled_times.get(selected_day, 'Not available')}"

    def handle_start_button(self):
        if self.scheduled_var.get():
            if self.start_button_text.get() == "Start":
                # 如果计划执行，等待倒计时结束后执行 run_selenium_script
                self.start_button_text.set("Cancel")
                self.start_button.config(state=tk.DISABLED)
                if self.countdown_timer:
                    # 取消现有的定时器
                    self.root.after_cancel(self.countdown_timer)
                self.start_countdown()
            else:
                # 如果是取消按钮，取消计时并关闭浏览器
                self.cleanup_driver()
                self.start_button_text.set("Start")
                self.start_button.config(state=tk.NORMAL)
        else:
            self.start_selenium_script()
            # 如果未计划执行，直接执行 run_selenium_script

    from datetime import datetime, timedelta

    def get_scheduled_datetime(self):
        selected_day = self.day_combobox.get()
        current_datetime = datetime.now()
        
        # 获取今天是星期几
        current_weekday = current_datetime.weekday()
        
        # 获取选择的日期对应的星期几的数值
        scheduled_weekday = {
            "Tuesday": 1,
            "Friday": 4,
            "Sunday": 6
        }.get(selected_day)

        if scheduled_weekday is None:
            raise ValueError("Invalid day selected")

        # 计算距离下一次计划执行的天数
        days_until_scheduled = (scheduled_weekday - current_weekday + 7) % 7
        
        # 获取计划执行的具体时间
        scheduled_time_str = {
            "Tuesday": "17:30:00",
            "Friday": "19:15:00",
            "Sunday": "08:15:00"
        }.get(selected_day)

        if scheduled_time_str is None:
            raise ValueError("Invalid day selected")

        scheduled_hour, scheduled_minute, scheduled_second = map(int, scheduled_time_str.split(':'))

        # 计算计划执行的具体日期和时间
        scheduled_date = current_datetime + timedelta(days=days_until_scheduled)
        scheduled_datetime = scheduled_date.replace(hour=scheduled_hour, minute=scheduled_minute, second=scheduled_second, microsecond=0)

        return scheduled_datetime

    def start_countdown(self):
        # 获取当前时间和计划执行时间
        scheduled_datetime = self.get_scheduled_datetime() - timedelta(days=3)  # 提前3天

        current_datetime = datetime.now()

        print(f"Debug: Scheduled Datetime: {scheduled_datetime}")
        print(f"Debug: Current Datetime: {current_datetime}")

        # 如果选择的日期是今天并且当前时间已经超过目标时间，则将目标时间推迟到下一次的同一天
        if current_datetime.date() == scheduled_datetime.date() and current_datetime > scheduled_datetime:
            scheduled_datetime += timedelta(days=7)  # 推迟到下一次的同一天

        # 计算时间差
        time_difference = scheduled_datetime - current_datetime

        # 判断是否应该设置倒计时时间
        if self.countdown_timer is None and time_difference.total_seconds() > 0:
            self.update_countdown(time_difference)
            self.remaining_time_label.grid(row=11, column=0, columnspan=2, pady=5)
            # 设置倒计时时间，并保存定时器ID
            self.countdown_timer = self.root.after(1000, lambda: self.start_countdown())
        elif time_difference.total_seconds() <= 0:
            # 如果倒计时已经归零，执行 run_selenium_script
            self.start_selenium_script()
            # 重置按钮文本和状态
            self.start_button_text.set("Start")
            self.start_button.config(state=tk.NORMAL)
        else:
            # 如果倒计时已经在运行，更新倒计时显示
            self.update_countdown(time_difference)
            self.countdown_timer = self.root.after(1000, lambda: self.start_countdown())

    def update_countdown(self, remaining_time):
        remaining_time_str = str(remaining_time).split(".")[0]
        self.remaining_time_var.set(f"Time remaining: {remaining_time_str}")
        self.start_button.config(text=f"Time remaining: {remaining_time_str}")
    
    def start_selenium_script(self):
        self.email = self.email_entry.get()
        self.password = self.password_entry.get()
        self.stay_signed_in = self.stay_signed_in_var.get()
        self.selected_day = self.day_combobox.get()
        self.run_selenium_script()
        self.root.destroy()

    def run_selenium_script(self):
        try:
            with webdriver.Chrome() as driver:
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

        except Exception as e:
            print(f"An error occurred during script execution: {e}")

        finally:
            self.cleanup_driver(driver)

    def load_settings_from_cache(self):
        SettingsManager.load_settings_from_cache(self)

    def save_settings_to_cache(self):
        SettingsManager.save_settings_to_cache(self)

    def on_close(self):
        # Save settings to cache if "Remember Info" is checked
        self.save_settings_to_cache()
        # Do other cleanup tasks as needed
        self.root.destroy()

